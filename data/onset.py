"""State of each child's verb lexicon at the first observed past-tense overregularisation.

Overregularisation: a child token ending in -ed whose lemma is an irregular verb
(goed, falled, broked, ...), excluding forms that are legitimate.
Onset: the first month of age containing one. Children are kept only if they
were recorded before onset (enough verb tokens with no overregularisation), so
the onset is not simply the start of recording.

For each child we estimate verbs known (N) and irregular verbs known (e) from
the six months of speech up to and including the onset month, using the joint
knowledge-usage model in zip_irt.py, and compare with raw cumulative counts.
"""

import sys
import numpy as np
import pandas as pd

sys.path.insert(0, "data")
from tail_model import IRREGULAR
from estimators import load
import zip_irt as Z

pd.set_option("display.width", 230)
pd.set_option("display.max_rows", 200)
VARIABLE = set("lie hang bust sneak dive sew mow light shine fit quit bet kneel spit speed".split())
LEGIT = set("feed shed fed led bled bred fled sped wed need seed weed bleed breed speed".split())
MIN_PRE = 500       # verb tokens recorded before the onset month
MIN_WIN = 300       # verb tokens in the six-month estimation window


def overreg_table():
    d = pd.read_csv("data/overreg_candidates.csv")
    d = d[d.stem.isin(IRREGULAR - VARIABLE) & ~d.gloss.isin(LEGIT)]
    return d


def window_counts(ch, lex, cid, lo, hi):
    w = ch[(ch.target_child_id == cid) & (ch.month >= lo) & (ch.month <= hi)].groupby("stem").n.sum()
    return w.reindex(lex, fill_value=0).values.astype(int)


if __name__ == "__main__":
    ch, inp = load()
    lex = inp.index
    irregular = lex.isin(IRREGULAR)
    f = np.load("data/zip_irt_fit.npz")
    par = dict(d=f["d"], rho=f["rho"], alpha=float(f["alpha"]))
    dens = pd.read_csv("data/childes_density.csv").set_index("target_child_id")

    ov = overreg_table()
    print(f"{ov.n.sum()} overregularisation tokens from {ov.target_child_id.nunique()} children")
    print("most common:", ", ".join(f"{g} ({n})" for g, n in ov.groupby("gloss").n.sum().sort_values(ascending=False).head(15).items()))

    by_month = ch.groupby(["target_child_id", "month"]).n.sum()
    rows, traj = [], []
    for cid, o in ov.groupby("target_child_id"):
        t0 = int(o.month.min())
        if cid not in by_month.index.get_level_values(0):
            continue
        mm = by_month.loc[cid]
        pre = mm[mm.index < t0].sum()
        if pre < MIN_PRE or t0 < 18 or t0 > 47:
            continue
        c = window_counts(ch, lex, cid, t0 - 5, t0)
        if c.sum() < MIN_WIN:
            continue
        N, e, _ = Z.estimate_unit(c, int(c.sum()), par, irregular)
        cum = window_counts(ch, lex, cid, 0, t0)
        rows.append(dict(child=f"{dens.corpus.get(cid, '?')}/{dens.target_child_name.get(cid, '?')}",
                         onset=t0, first_rec=int(mm.index.min()), pre_tokens=int(pre), win_tokens=int(c.sum()),
                         raw_N=int((cum > 0).sum()), raw_e=int((cum[irregular] > 0).sum()),
                         N=N, e=e, n_overreg=int(o.n.sum())))
        for a, b, lab in [(-11, -6, "7-12 months before"), (-5, 0, "0-5 months before"),
                          (1, 6, "1-6 months after"), (7, 12, "7-12 months after")]:
            cc = window_counts(ch, lex, cid, t0 + a, t0 + b)
            if cc.sum() >= MIN_WIN:
                n_, e_, _ = Z.estimate_unit(cc, int(cc.sum()), par, irregular)
                traj.append(dict(child=cid, period=lab, order=a, N=n_, e=e_))
    r = pd.DataFrame(rows).sort_values("pre_tokens", ascending=False)
    r["share"] = r.e / r.N
    r["TP_limit"] = r.N / np.log(r.N)
    r["raw_share"] = r.raw_e / r.raw_N
    r["raw_TP_limit"] = r.raw_N / np.log(r.raw_N)
    r.to_csv("data/onset_estimates.csv", index=False)

    print(f"\n{len(r)} children with an onset observed after at least {MIN_PRE} recorded verb tokens\n")
    print(r[["child", "onset", "first_rec", "pre_tokens", "raw_N", "raw_e", "N", "e", "share", "TP_limit"]]
          .round(2).to_string(index=False))

    def verdicts(N, e, lab):
        s = e / N
        print(f"  {lab:34s} N/ln N: {np.mean(e <= N / np.log(N)):>4.0%}   under 30%: {np.mean(s < .3):>4.0%}"
              f"   under 40%: {np.mean(s < .4):>4.0%}   under 50%: {np.mean(s < .5):>4.0%}"
              f"   median share {np.median(s):.2f}")

    print("\nShare of children whose lexicon at onset satisfies each threshold")
    verdicts(r.raw_N, r.raw_e, "raw cumulative counts")
    verdicts(r.N, r.e, "model estimates")
    verdicts(r.N * 1.35, r.e, "model, total verbs raised 35%")
    verdicts(r.N * 2.0, r.e, "model, total verbs doubled")
    print(f"\nmedian at onset: age {r.onset.median():.0f} months; verbs {r.N.median():.0f}; irregular {r.e.median():.0f}; "
          f"N/ln N limit {r.TP_limit.median():.0f}")
    need = r.e.apply(lambda e: next(n for n in range(10, 5000) if n / np.log(n) >= e))
    print(f"total verbs N/ln N would require, as a multiple of the estimate: median {np.median(need / r.N):.2f} "
          f"(quartiles {np.quantile(need / r.N, .25):.2f}-{np.quantile(need / r.N, .75):.2f})")

    t = pd.DataFrame(traj)
    t["share"] = t.e / t.N
    t["TP_ratio"] = t.e / (t.N / np.log(t.N))
    print("\nLexicon around onset (medians; TP ratio above 1 means more exceptions than N/ln N allows)")
    print(t.groupby(["order", "period"]).agg(children=("child", "nunique"), N=("N", "median"), e=("e", "median"),
                                             share=("share", "median"), TP_ratio=("TP_ratio", "median"))
          .round(2).to_string())
