"""Per-word acoustic support from BabAR's CTC outputs.

Run on ccn2 with BabAR's venv. For each transcript token, take BabAR's frame log-probs over
the token's time window (+/- --pad s, inside BabAR's usual 20 s context) and compute the CTC
log-likelihood of:
  - the ASR word's pronunciation (CMUdict -> BabAR's IPA symbols)
  - K null pronunciations: words with the same number of phonemes, drawn from other tokens
    of the same speaker and age band
  - for irregular verbs: every candidate form of the lemma (stem, -s, -ing, irregular forms,
    regularised forms like "goed")
Support = share of nulls the ASR word beats. If ASR words are acoustically arbitrary
(hallucinated), support is uniform on [0, 1], so the share above 0.9 is 0.1 by chance.

Output (private, stays on ccn2): <work>/word_scores.csv and <work>/irreg_scores.csv.
Then run 08_word_score_summary.py for aggregates.

Usage (from BabAR root):
  .venv/bin/python 07_word_scores.py --work .../pilot --ref .../tp_babyview --babar .../BabAR
"""

import argparse
import json
import sys
from pathlib import Path

import cmudict
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

TRANSCRIPT = "/ccn2b/dataset/babyview/2026.1/outputs/merged_transcripts_parsed.csv"
CONS = {"B": "b", "CH": "t ʃ", "D": "d", "DH": "ð", "F": "f", "G": "ɡ", "HH": "h", "JH": "d ʒ",
        "K": "k", "L": "l", "M": "m", "N": "n", "NG": "ŋ", "P": "p", "R": "ɹ", "S": "s", "SH": "ʃ",
        "T": "t", "TH": "θ", "V": "v", "W": "w", "Y": "j", "Z": "z", "ZH": "ʒ"}
VOW = {"AA": "ɑ", "AE": "æ", "AH": "ʌ", "AO": "ɔ", "AW": "a ʊ", "AY": "a ɪ", "EH": "ɛ", "ER": "ɜ",
       "EY": "e ɪ", "IH": "ɪ", "IY": "i", "OW": "o ʊ", "OY": "ɔ ɪ", "UH": "ʊ", "UW": "u"}
VOICELESS = {"p", "k", "f", "s", "ʃ", "θ"}
BLOCK = set("bed seed need weed feed shed wed lied fed led bled bred fled sped".split())


def arpa_to_ipa(pron):
    out = []
    for p in pron:
        b = p.rstrip("012")
        if b == "AH" and p.endswith("0"):
            out.append("ə")
        elif b in VOW:
            out.extend(VOW[b].split())
        else:
            out.extend(CONS[b].split())
    return out


def regularise(stem_ipa):
    """Regular past of a stem pronunciation: /ɪd/ after t/d, /t/ after voiceless, else /d/."""
    last = stem_ipa[-1]
    if last in ("t", "d"):
        return stem_ipa + ["ɪ", "d"]
    return stem_ipa + (["t"] if last in VOICELESS else ["d"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--ref", type=Path, required=True, help="dir with verb_lexicon.csv etc.")
    ap.add_argument("--babar", type=Path, required=True)
    ap.add_argument("--pad", type=float, default=0.1)
    ap.add_argument("--k", type=int, default=50)
    ap.add_argument("--fem-sample", type=int, default=4000)
    ap.add_argument("--device", default="cuda")
    a = ap.parse_args()
    sys.path.insert(0, str(a.babar / "src"))
    from babar.infer import load_model
    from babar.datamodules.contextual_vtc_datamodule import ContextualVTCDataModule

    vocab = json.load(open(a.babar / "weights" / "vocab-phoneme-tinyvox.json"))
    blank = vocab["<blank>"]
    cmu = cmudict.dict()

    def pron(w):
        p = cmu.get(str(w).lower())
        return arpa_to_ipa(p[0]) if p else None

    lst = pd.read_csv(a.work / "list.tsv", sep="\t")
    band = dict(zip(lst.video_id, lst.band))
    lex = pd.read_csv(a.ref / "verb_lexicon.csv")
    whitelist, irregular = set(lex.lemma), set(lex.lemma[lex.irregular == 1])
    forms = pd.read_csv(a.ref / "verb_form_lemma.csv")
    over = pd.read_csv(a.ref / "overreg_forms.csv")
    target_lemmas = set(over.lemma) & irregular - {"be", "have", "do"}

    t = pd.read_csv(TRANSCRIPT, usecols=["video_id", "token", "token_start_time", "token_end_time",
                                         "speaker", "spacy_token_lemma", "spacy_pos", "spacy_tag",
                                         "spacy_is_punct"], dtype=str)
    t = t[t.video_id.isin(band) & (t.spacy_is_punct.str.lower() != "true")].copy()
    for c in ["token_start_time", "token_end_time"]:
        t[c] = pd.to_numeric(t[c], errors="coerce")
    t = t.dropna(subset=["token_start_time", "token_end_time"])
    t = t[t.token_end_time > t.token_start_time]
    t["band"] = t.video_id.map(band)
    t["lemma"] = t.spacy_token_lemma.str.lower()
    t["word"] = t.token.str.lower().str.strip(" .,!?\"'")
    t["verb"] = t.spacy_pos.isin(["VERB", "AUX"]) & t.lemma.isin(whitelist)
    fem = t[t.speaker == "FEM"].sample(min(a.fem_sample, (t.speaker == "FEM").sum()), random_state=0)
    t = pd.concat([t[t.speaker == "KCHI"], fem])
    t["ipa"] = t.word.map(pron)
    t = t[t.ipa.notna()].reset_index(drop=True)
    t["tok_id"] = np.arange(len(t))

    # candidate pronunciations for irregular verbs of interest
    cands = {}
    for lem in target_lemmas:
        sp = pron(lem)
        if sp is None:
            continue
        c = {}
        for f in set(forms.form[forms.lemma == lem]) | {lem}:
            p = pron(f)
            if p is None or f in set(over.form):
                continue
            kind = ("stem" if f == lem else "s" if f in (lem + "s", lem + "es")
                    else "ing" if f.endswith("ing") else "irregular")
            c[f] = (kind, p)
        reg = regularise(sp)
        rf = lem + ("d" if lem.endswith("e") else "ed")
        if rf not in BLOCK and not any(p == reg for _, p in c.values()):
            c[rf] = ("overreg", reg)
        cands[lem] = c

    model = load_model(a.babar / "weights" / "best.ckpt",
                       a.babar / "weights" / "vocab-phoneme-tinyvox.json", device=a.device)
    model = model.to(a.device).half().eval()
    rng = np.random.default_rng(0)
    rows, irow = [], []
    # nulls are length-matched: words with the same number of phonemes (from the same speaker
    # and band), widening to +/-1 phoneme if fewer than 20 such tokens exist
    t["n_ph"] = t.ipa.map(len)
    pools = {}
    for (spk, b), g in t.groupby(["speaker", "band"]):
        for n in g.n_ph.unique():
            p = g.ipa[g.n_ph == n].tolist()
            if len(p) < 20:
                p = g.ipa[(g.n_ph - n).abs() <= 1].tolist()
            pools[(spk, b, n)] = p

    def ids(p):
        return [vocab[x] for x in p if x in vocab]

    for vid, g in t.groupby("video_id"):
        rttm = a.work / "tmp_word.rttm"
        with open(rttm, "w") as f:
            for r in g.itertuples():
                on = max(0.0, r.token_start_time - a.pad)
                dur = max(r.token_end_time + a.pad - on, 0.25)
                f.write(f"SPEAKER {vid} 1 {on:.3f} {dur:.3f} <NA> <NA> KCHI <NA> <NA>\n")
        dm = ContextualVTCDataModule(audio_path=a.work / "wav" / f"{vid}.wav", rttm_path=rttm,
                                     context_duration=20.0, batch_size=32, num_workers=4,
                                     speaker_filter=["KCHI"], max_utt_dur=30.0, device=a.device)
        dm.set_processor(model.processor)
        dm.setup()
        gi = g.reset_index(drop=True)
        for batch in dm.dataloader():
            with torch.no_grad():
                batch["array"] = batch["array"].to(a.device, dtype=torch.float16)
                hs, lens, _ = model.get_hidden_states(batch)
                lp = F.log_softmax(model.get_logits(hs).float(), dim=-1)
            for i, uid in enumerate(batch["utterance_id"]):
                r = gi.iloc[uid]
                T = int(lens[i])
                x = lp[i, :T]
                greedy = x.max(-1).values.sum().item()
                pool = pools[(r.speaker, r.band, r.n_ph)]
                nulls = [pool[j] for j in rng.integers(0, len(pool), a.k * 2) if pool[j] != r.ipa][: a.k]
                targets = [ids(r.ipa)] + [ids(p) for p in nulls]
                extra = []
                if r.speaker == "KCHI" and r.lemma in cands and r.verb:
                    extra = list(cands[r.lemma].items())
                    targets += [ids(p) for _, (_, p) in extra]
                tl = torch.tensor([len(z) for z in targets])
                flat = torch.tensor([v for z in targets for v in z], dtype=torch.long)
                n = len(targets)
                ll = -F.ctc_loss(x.unsqueeze(1).expand(T, n, -1), flat, torch.full((n,), T), tl,
                                 blank=blank, reduction="none", zero_infinity=False).cpu().numpy()
                w, nl = ll[0], ll[1:1 + len(nulls)]
                fin = np.isfinite(nl)
                rows.append(dict(tok_id=r.tok_id, T=T, ll_word=w, ll_greedy=greedy,
                                 support=float((nl[fin] < w).mean()) if fin.any() and np.isfinite(w) else np.nan,
                                 n_null=int(fin.sum())))
                for (f, (kind, _)), v in zip(extra, ll[1 + len(nulls):]):
                    irow.append(dict(tok_id=r.tok_id, form=f, kind=kind, ll=v, T=T))
    s = t.drop(columns=["token"]).merge(pd.DataFrame(rows), on="tok_id")
    s["ipa"] = s.ipa.map(" ".join)
    s.to_csv(a.work / "word_scores.csv", index=False)
    pd.DataFrame(irow).to_csv(a.work / "irreg_scores.csv", index=False)
    print("scored", len(s), "tokens;", len(irow), "irregular candidate rows")


if __name__ == "__main__":
    main()
