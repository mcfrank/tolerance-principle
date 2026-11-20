"""Aggregate results of the BabAR pilot (run_pilot.sh). Prints aggregates only.

  A. Label agreement: for each existing transcript token, which VTC 2.0 (rerun) segments
     cover its midpoint. Tests whether the existing labels are VTC 2.0, and checks that
     the 2026.1 mp3 lines up with the transcript times.
  B. BabAR output by segment set (vtc2 KCHI, existing-transcript KCHI, VTC adult control)
     and age band: share with empty output, phonemes per segment and per second.
  C. Word-phoneme match: Whisper's words vs BabAR's phonemes for the same stretch, as a
     normalised edit distance on a consonant skeleton (vowels collapsed to V), compared
     with a shuffled baseline that pairs words and phonemes from different stretches in
     the same band. Real words should match better than chance; hallucinated ones should not.
  D. Existing KCHI verb rate after filtering to tokens that VTC 2.0 also calls KCHI and
     where BabAR heard something.

Usage: python 06_pilot_analysis.py --work /data2/mcfrank/tp_babyview/pilot --lex ../verb_lexicon.csv
"""

import argparse
from pathlib import Path

import cmudict
import numpy as np
import pandas as pd

TRANSCRIPT = "/ccn2b/dataset/babyview/2026.1/outputs/merged_transcripts_parsed.csv"
pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)

ARPA = {"B": "b", "CH": "tʃ", "D": "d", "DH": "ð", "F": "f", "G": "ɡ", "HH": "h", "JH": "dʒ",
        "K": "k", "L": "l", "M": "m", "N": "n", "NG": "ŋ", "P": "p", "R": "ɹ", "S": "s",
        "SH": "ʃ", "T": "t", "TH": "θ", "V": "v", "W": "w", "Y": "j", "Z": "z", "ZH": "ʒ"}
BABAR_CONS = set("b d f h j k l m n p s t v w z ð ŋ ɡ ʃ ʒ θ ɹ".split())
BABAR_NORM = {"r": "ɹ", "ɾ": "ɹ", "ʁ": "ɹ", "x": "h", "ç": "h", "g": "ɡ", "ɲ": "n", "ʎ": "l",
              "ɥ": "w"}


def skel_babar(ph):
    out = []
    for p in str(ph).split():
        p = BABAR_NORM.get(p, p)
        out.append(p if p in BABAR_CONS else "V")
    return out


def skel_word(w, cmu):
    prons = cmu.get(w.lower())
    if not prons:
        return None
    out = []
    for p in prons[0]:
        base = p.rstrip("012")
        if base in ARPA:
            out.extend({"tʃ": ["t", "ʃ"], "dʒ": ["d", "ʒ"]}.get(ARPA[base], [ARPA[base]]))
        else:
            out.append("V")
    return out


def lev(a, b):
    if not a and not b:
        return 0.0
    d = np.arange(len(b) + 1)
    for i, x in enumerate(a, 1):
        prev, d[0] = d[0], i
        for j, y in enumerate(b, 1):
            prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (x != y))
    return d[-1] / max(len(a), len(b))


def read_rttm(p):
    rows = []
    for line in open(p):
        s = line.split()
        if len(s) >= 8 and s[0] == "SPEAKER":
            rows.append((s[1], float(s[3]), float(s[3]) + float(s[4]), s[7]))
    return rows


def read_babar(d):
    fs = [pd.read_csv(p, keep_default_na=False).assign(video_id=p.stem) for p in sorted(Path(d).glob("*.csv"))]
    fs = [f for f in fs if len(f)]
    df = pd.concat(fs) if fs else pd.DataFrame(columns=["onset", "offset", "phonemes", "video_id"])
    df["n_ph"] = df.phonemes.astype(str).str.split().str.len().fillna(0)
    df.loc[df.phonemes.astype(str).str.strip() == "", "n_ph"] = 0
    df["dur"] = df.offset - df.onset
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--lex", type=Path, required=True)
    ap.add_argument("--shuffles", type=int, default=50)
    a = ap.parse_args()
    W = a.work
    lst = pd.read_csv(W / "list.tsv", sep="\t")
    band = dict(zip(lst.video_id, lst.band))
    lex = set(pd.read_csv(a.lex).lemma)

    t = pd.read_csv(TRANSCRIPT, usecols=["video_id", "utterance_id", "token", "token_start_time",
                                         "token_end_time", "speaker", "spacy_token_lemma", "spacy_pos",
                                         "spacy_is_punct"], dtype=str)
    t = t[t.video_id.isin(band) & (t.spacy_is_punct.str.lower() != "true")].copy()
    for c in ["token_start_time", "token_end_time"]:
        t[c] = pd.to_numeric(t[c], errors="coerce")
    t = t.dropna(subset=["token_start_time", "token_end_time"])
    t["mid"] = (t.token_start_time + t.token_end_time) / 2
    t["band"] = t.video_id.map(band)
    t["verb"] = t.spacy_pos.isin(["VERB", "AUX"]) & t.spacy_token_lemma.str.lower().isin(lex)

    # A. agreement with VTC 2.0 rerun
    rt = pd.DataFrame([r for p in sorted((W / "vtc2" / "rttm").glob("*.rttm")) for r in read_rttm(p)],
                      columns=["video_id", "on", "off", "lab"])
    labs = ["KCHI", "OCH", "FEM", "MAL"]
    for lab in labs:
        t["v_" + lab] = False
    for vid, g in t.groupby("video_id"):
        r = rt[rt.video_id == vid]
        for lab in labs:
            rr = r[r.lab == lab]
            if len(rr) == 0:
                continue
            on, off = rr.on.values, rr.off.values
            m = g.mid.values[:, None]
            t.loc[g.index, "v_" + lab] = ((m >= on) & (m <= off)).any(1)
    t["v_none"] = ~t[["v_" + l for l in labs]].any(axis=1)
    print("A. Existing label (rows) vs VTC 2.0 rerun label at token midpoint (share of tokens; "
          "labels can overlap)")
    print(t.groupby("speaker")[["v_" + l for l in labs] + ["v_none"]].mean().round(3)
          .assign(n=t.groupby("speaker").size()))
    print("\n   KCHI tokens only, by band")
    k = t[t.speaker == "KCHI"]
    print(k.groupby("band")[["v_" + l for l in labs] + ["v_none"]].mean().round(3)
          .assign(n=k.groupby("band").size()))

    # B. BabAR outputs
    print("\nB. BabAR output by segment set and band")
    sets = {"vtc2_KCHI": W / "vtc2" / "phonemes", "orig_KCHI": W / "babar_orig", "vtc2_adult": W / "babar_adult"}
    out = {}
    rows = []
    for name, d in sets.items():
        df = read_babar(d)
        df["band"] = df.video_id.map(band)
        out[name] = df
        for b, g in df.groupby("band"):
            rows.append(dict(set=name, band=b, n_seg=len(g), empty=(g.n_ph == 0).mean(),
                             med_ph=g.n_ph.median(), ph_per_s=g.n_ph.sum() / max(g.dur.sum(), 1e-9),
                             med_dur=g.dur.median()))
    print(pd.DataFrame(rows).round(3).to_string(index=False))

    # join orig segments to BabAR output and to their words
    seg = pd.read_csv(W / "orig_segments.csv")
    ob = out["orig_KCHI"][["video_id", "onset", "phonemes", "n_ph"]].copy()
    seg["onset_r"] = seg.onset.round(3)
    ob["onset_r"] = ob.onset.round(3)
    seg = seg.merge(ob.drop(columns="onset"), on=["video_id", "onset_r"], how="left")
    print(f"\n   orig segments matched to BabAR rows: {seg.phonemes.notna().mean():.3f}")
    t = t.sort_values(["video_id", "token_start_time"])
    k = t[t.speaker == "KCHI"].copy()
    # assign each KCHI token to its orig segment (same video, inside [onset, offset])
    k["seg"] = -1
    for vid, g in k.groupby("video_id"):
        s = seg[seg.video_id == vid]
        if len(s) == 0:
            continue
        idx = np.searchsorted(s.onset.values, g.token_start_time.values + 1e-6, side="right") - 1
        ok = (idx >= 0) & (g.token_end_time.values <= s.offset.values[np.clip(idx, 0, None)] + 1e-6)
        k.loc[g.index[ok], "seg"] = s.index.values[idx[ok]]
    words = k[k.seg >= 0].groupby("seg").agg(words=("token", lambda x: list(x)),
                                             any_verb=("verb", "any"))
    seg = seg.join(words, how="inner")
    seg["band"] = seg.video_id.map(band)
    seg["empty"] = seg.n_ph.fillna(0) == 0
    print("   orig segments: empty BabAR output by band x contains-verb")
    print(seg.groupby(["band", "any_verb"]).empty.agg(["mean", "size"]).round(3))

    # C. word-phoneme match
    cmu = cmudict.dict()
    seg["w_sk"] = seg.words.map(lambda ws: None if any(skel_word(w, cmu) is None for w in ws)
                                else sum((skel_word(w, cmu) for w in ws), []))
    c = seg[~seg.empty & seg.w_sk.notna()].copy()
    c["b_sk"] = c.phonemes.map(skel_babar)
    c["d"] = [lev(x, y) for x, y in zip(c.w_sk, c.b_sk)]
    rng = np.random.default_rng(0)
    res = []
    for (b, single), g in c.groupby(["band", c.n_tok == 1]):
        sh = []
        for _ in range(a.shuffles):
            perm = rng.permutation(len(g))
            sh.append(np.mean([lev(x, y) for x, y in zip(g.w_sk.values, g.b_sk.values[perm])]))
        res.append(dict(band=b, single_word=single, n=len(g), matched=g.d.mean(), shuffled=np.mean(sh),
                        shuffled_sd=np.std(sh)))
    print("\nC. Word-phoneme distance (0 = identical skeletons); lower than shuffled = real signal")
    print(pd.DataFrame(res).round(3).to_string(index=False))
    res = []
    for (b, v), g in c.groupby(["band", "any_verb"]):
        sh = [np.mean([lev(x, y) for x, y in zip(g.w_sk.values, g.b_sk.values[rng.permutation(len(g))])])
              for _ in range(a.shuffles)]
        res.append(dict(band=b, has_verb=v, n=len(g), matched=g.d.mean(), shuffled=np.mean(sh)))
    print(pd.DataFrame(res).round(3).to_string(index=False))

    # D. filtered verb rate
    k = k.merge(seg[["empty"]], left_on="seg", right_index=True, how="left")
    k["babar_heard"] = k["empty"].eq(False)
    print("\nD. Existing KCHI verb rate under filters, by band")
    rows = []
    for b, g in k.groupby("band"):
        for name, m in [("all", np.ones(len(g), bool)), ("vtc2_KCHI", g.v_KCHI.values),
                        ("babar_heard", g.babar_heard.values),
                        ("both", g.v_KCHI.values & g.babar_heard.values)]:
            rows.append(dict(band=b, filter=name, n=int(m.sum()), verb_rate=g.verb.values[m].mean()))
    print(pd.DataFrame(rows).round(3).to_string(index=False))
    adult = t[t.speaker.isin(["FEM", "MAL"])]
    print("   adult verb rate:", adult.groupby("band").verb.mean().round(3).to_dict())


if __name__ == "__main__":
    main()
