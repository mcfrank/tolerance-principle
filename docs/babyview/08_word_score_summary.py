"""Aggregate summary of 07_word_scores.py output. Prints aggregates only.

  1. Support distribution by speaker x band. Under the hallucination null, support is
     uniform: mean 0.5 and share >= 0.9 of 0.1. The excess (share - 0.1) / 0.9 is a rough
     estimate of the share of tokens whose word is acoustically real.
  2. KCHI verb rate among tokens above support thresholds, vs the adult rate.
  3. Irregular verbs (KCHI): ASR's form category vs the acoustically best candidate,
     and how often the regularised form ("goed") beats the irregular form.

Usage: python 08_word_score_summary.py --work .../pilot
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", type=Path, required=True)
    a = ap.parse_args()
    s = pd.read_csv(a.work / "word_scores.csv", keep_default_na=False, na_values=[""])
    s = s[s.support.notna()]
    s["n_ph"] = s.ipa.str.split().str.len()

    print("1. Support (share of null words the ASR word beats), by speaker x band")
    g = s.groupby(["speaker", "band"])
    out = g.support.agg(n="size", mean="mean", median="median")
    out["ge_0.9"] = g.support.apply(lambda x: (x >= 0.9).mean())
    out["excess_real"] = (out["ge_0.9"] - 0.1) / 0.9
    print(out.round(3))
    print("\n   KCHI by band x verb, and by word length (phonemes)")
    k = s[s.speaker == "KCHI"]
    print(k.groupby(["band", "verb"]).support.agg(["size", "mean", lambda x: (x >= 0.9).mean()]).round(3))
    k = k.assign(len_bin=pd.cut(k.n_ph, [0, 2, 3, 4, 6, 99], labels=["1-2", "3", "4", "5-6", "7+"]))
    print(k.groupby(["band", "len_bin"], observed=True).support
          .agg(["size", "mean", lambda x: (x >= 0.9).mean()]).round(3))

    print("\n2. KCHI verb rate by support threshold (adult FEM rate for reference)")
    rows = []
    for b, gb in k.groupby("band"):
        for th in [0, 0.5, 0.8, 0.9, 0.95]:
            m = gb.support >= th
            rows.append(dict(band=b, min_support=th, n=int(m.sum()), verb_rate=gb.verb[m].mean()))
    print(pd.DataFrame(rows).round(3).to_string(index=False))
    print("   FEM verb rate:", s[s.speaker == "FEM"].groupby("band").verb.mean().round(3).to_dict())

    # combined filters: word acoustically supported; child voice (VTC 2.0 rerun calls the
    # token KCHI, and BabAR heard something in its transcript stretch); no adult overlap
    # (token's time span touches no VTC 2.0 FEM/MAL segment)
    rt = []
    for f in sorted((a.work / "vtc2" / "rttm").glob("*.rttm")):
        for line in open(f):
            x = line.split()
            if len(x) >= 8:
                rt.append((x[1], float(x[3]), float(x[3]) + float(x[4]), x[7]))
    rt_all = pd.DataFrame(rt, columns=["video_id", "on", "off", "lab"])
    rt = rt_all[rt_all.lab == "KCHI"]
    ad = rt_all[rt_all.lab.isin(["FEM", "MAL"])]
    seg = pd.read_csv(a.work / "orig_segments.csv")
    bo = pd.concat([pd.read_csv(f, keep_default_na=False).assign(video_id=f.stem)
                    for f in sorted((a.work / "babar_orig").glob("*.csv"))])
    bo = bo[bo.phonemes.astype(str).str.strip() != ""]
    k = k.copy()
    k["mid"] = (k.token_start_time + k.token_end_time) / 2
    k["vtc_kchi"] = False
    k["heard"] = False
    k["adult_overlap"] = False
    for vid, g in k.groupby("video_id"):
        r2 = ad[ad.video_id == vid]
        if len(r2):
            on, off = g.token_start_time.values[:, None], g.token_end_time.values[:, None]
            k.loc[g.index, "adult_overlap"] = ((on < r2.off.values) & (off > r2.on.values)).any(1)
        r = rt[rt.video_id == vid]
        m = g.mid.values[:, None]
        if len(r):
            k.loc[g.index, "vtc_kchi"] = ((m >= r.on.values) & (m <= r.off.values)).any(1)
        h = seg[(seg.video_id == vid) & seg.onset.round(3).isin(bo.onset[bo.video_id == vid].round(3))]
        if len(h):
            k.loc[g.index, "heard"] = ((m >= h.onset.values - 1e-3) & (m <= h.offset.values + 1e-3)).any(1)
    print("\n4. KCHI verb rate under combined filters")
    rows = []
    for b, gb in k.groupby("band"):
        child = gb.vtc_kchi & gb.heard
        for name, m in [("all", gb.support >= 0), ("child_voice", child),
                        ("support>=0.9", gb.support >= 0.9),
                        ("child_voice & support>=0.9", child & (gb.support >= 0.9)),
                        ("child_voice & no_adult", child & ~gb.adult_overlap),
                        ("child_voice & no_adult & support>=0.9",
                         child & ~gb.adult_overlap & (gb.support >= 0.9))]:
            rows.append(dict(band=b, filter=name, n=int(m.sum()), share=m.mean(),
                             verb_rate=gb.verb[m].mean()))
    print(pd.DataFrame(rows).round(3).to_string(index=False))
    print("   support >= 0.9 share among child_voice tokens:",
          k[k.vtc_kchi & k.heard].groupby("band").support.apply(lambda x: (x >= 0.9).mean()).round(3).to_dict())

    p = a.work / "irreg_scores.csv"
    ir = pd.read_csv(p) if p.stat().st_size > 1 else pd.DataFrame()
    if len(ir):
        print("\n3. Irregular verbs (KCHI tokens of lemmas with attested overregularisations)")
        ir = ir.merge(s[["tok_id", "word", "lemma", "band", "support", "spacy_tag"]], on="tok_id")
        ir = ir[np.isfinite(ir.ll)]
        asr_kind = ir[ir.form == ir.word].set_index("tok_id").kind.rename("asr_kind")
        best = ir.loc[ir.groupby("tok_id").ll.idxmax()].set_index("tok_id").kind.rename("best_kind")
        tok = pd.concat([asr_kind, best], axis=1).dropna()
        tok = tok.join(ir.drop_duplicates("tok_id").set_index("tok_id")[["band", "support"]])
        print("   tokens:", len(tok))
        print(pd.crosstab([tok.band, tok.asr_kind], tok.best_kind))
        # regularised vs irregular form, per token where both exist
        piv = ir.pivot_table(index="tok_id", columns="kind", values="ll", aggfunc="max")
        if {"overreg", "irregular"} <= set(piv.columns):
            piv = piv.dropna(subset=["overreg", "irregular"]).join(tok[["band", "asr_kind", "support"]])
            piv["d"] = piv.overreg - piv.irregular
            print("\n   overreg minus irregular log-lik (positive = acoustics favour e.g. 'goed' over 'went')")
            print(piv.groupby(["band", "asr_kind"]).d.describe(percentiles=[.5, .9]).round(2))
            print("   share with d > 2, among tokens ASR heard as the irregular form, by support >= 0.8:")
            q = piv[piv.asr_kind == "irregular"]
            print(q.groupby([q.band, q.support >= 0.8]).d.apply(lambda x: (x > 2).mean()).round(3))


if __name__ == "__main__":
    main()
