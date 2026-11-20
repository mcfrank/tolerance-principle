"""Estimating how many verbs a child knows from a sparse sample of their speech.

Validation by thinning: take a densely recorded child in a 6-month window,
randomly keep a fraction of their verb tokens, and ask each estimator for the
number of verb types (and irregular verb types) the child knows. A good
estimator gives the same answer at every thinning level, and that answer is
at least the number of types seen in the full sample.

Estimators
  naive     types observed
  chao1     observed + f1^2 / (2 f2)   (uses only the sample's own counts)
  ht_input  Horvitz-Thompson: each observed verb counts 1 / P(detect), with
            P(detect) = 1 - (1 - r_v / Z)^m and r_v its share of verb tokens in
            speech addressed to children
  ht_child  same, with r_v from the pooled speech of all OTHER children
  model     P(know v) = sigmoid(a + b log r_v), fitted to which verbs were
            detected; sums posterior P(know) over the whole reference lexicon
Z is the total reference mass of the verbs the child knows (so r_v / Z is the
child's own usage probability); it is solved for by fixed-point iteration.
"""

import sys
import numpy as np
import pandas as pd
from scipy.optimize import minimize

sys.path.insert(0, "data")
from tail_model import IRREGULAR, NOT_VERBS

pd.set_option("display.width", 220)
rng = np.random.default_rng(0)
W_MAX = 25.0          # cap on Horvitz-Thompson weights


def load():
    ch = pd.read_csv("data/child_verb_counts.csv")
    inp = pd.read_csv("data/input_verb_counts.csv").groupby("stem").n.sum()
    ok = lambda s: s.str.fullmatch(r"[a-z]+") & ~s.isin(NOT_VERBS)
    ch = ch[ok(ch.stem.astype(str))]
    inp = inp[ok(inp.index.to_series().astype(str))]
    # reference lexicon: verbs with at least 5 tokens in the input
    lex = inp[inp >= 5].index
    ch = ch[ch.stem.isin(lex)]
    return ch, inp.loc[lex]


def ht(counts, r, m, irregular):
    """Horvitz-Thompson estimate of (N, e). counts, r aligned over the lexicon."""
    seen = counts > 0
    Z = 1.0
    for _ in range(50):
        pi = 1 - (1 - np.minimum(r / Z, 1.0)) ** m
        w = np.minimum(1 / np.maximum(pi, 1e-12), W_MAX)
        Z_new = min(1.0, np.sum(r[seen] * w[seen]))
        if abs(Z_new - Z) < 1e-6:
            break
        Z = Z_new
    return w[seen].sum(), w[seen & irregular].sum()


def model(counts, r, m, irregular):
    """Logistic knowledge model fitted to detections."""
    seen = counts > 0
    lr = np.log(r) - np.log(r).mean()
    Z = 1.0
    for _ in range(6):
        pi = 1 - (1 - np.minimum(r / Z, 1.0)) ** m

        def nll(w):
            k = 1 / (1 + np.exp(-(w[0] + w[1] * lr)))
            p = (k * pi).clip(1e-12, 1 - 1e-12)
            return -(np.log(p[seen]).sum() + np.log(1 - p[~seen]).sum())

        w = minimize(nll, [0.0, 1.0], method="Nelder-Mead").x
        k = 1 / (1 + np.exp(-(w[0] + w[1] * lr)))
        post = np.where(seen, 1.0, k * (1 - pi) / (1 - k * pi))
        Z = min(1.0, np.sum(post * r))
    return post.sum(), post[irregular].sum()


def chao1(counts, irregular):
    def one(c):
        k, f1, f2 = (c > 0).sum(), (c == 1).sum(), (c == 2).sum()
        return k + f1 * (f1 - 1) / (2 * (f2 + 1))
    return one(counts), one(counts[irregular])


def estimates(counts, m, r_in, r_ch, irregular):
    out = {"naive": ((counts > 0).sum(), (counts[irregular] > 0).sum()),
           "chao1": chao1(counts, irregular),
           "ht_input": ht(counts, r_in, m, irregular),
           "ht_child": ht(counts, r_ch, m, irregular),
           "model": model(counts, r_in, m, irregular)}
    return out


if __name__ == "__main__":
    ch, inp = load()
    lex = inp.index
    irregular = lex.isin(IRREGULAR)
    r_in = (inp / inp.sum()).values
    dens = pd.read_csv("data/childes_density.csv").set_index("target_child_id")
    print(f"reference lexicon: {len(lex)} verbs, {irregular.sum()} irregular")

    fracs = [1, 1 / 2, 1 / 4, 1 / 8, 1 / 16, 1 / 32, 1 / 64]
    rows = []
    for lo, hi in [(24, 30), (30, 36)]:
        win = ch[(ch.month >= lo) & (ch.month < hi)]
        tot = win.groupby("target_child_id").n.sum()
        for cid in tot[tot >= 6000].index:
            c = win[win.target_child_id == cid].groupby("stem").n.sum().reindex(lex, fill_value=0).values
            others = ch[ch.target_child_id != cid].groupby("stem").n.sum().reindex(lex, fill_value=0).values + 0.5
            r_ch = others / others.sum()
            M = int(c.sum())
            name = f"{dens.corpus.get(cid, '?')}/{dens.target_child_name.get(cid, '?')}"
            for f in fracs:
                m = int(M * f)
                reps = 1 if f == 1 else 8
                acc = {}
                for _ in range(reps):
                    s = c if f == 1 else rng.multivariate_hypergeometric(c, m)
                    for k, (N, e) in estimates(s, m, r_in, r_ch, irregular).items():
                        acc.setdefault(k, []).append((N, e))
                for k, v in acc.items():
                    N, e = np.mean(v, axis=0)
                    rows.append(dict(child=name, window=f"{lo}-{hi}", M=M, frac=f, m=m, est=k, N=N, e=e))
            print(f"  done {name} {lo}-{hi} (M = {M})", flush=True)
    res = pd.DataFrame(rows)
    res.to_csv("data/estimator_validation.csv", index=False)

    full = res[(res.frac == 1) & (res.est == "naive")].set_index(["child", "window"])[["N", "e"]]
    res = res.join(full, on=["child", "window"], rsuffix="_full")
    res["N_rel"] = res.N / res.N_full
    res["e_rel"] = res.e / res.e_full
    res["irr_share"] = res.e / res.N
    n_cw = full.shape[0]
    print(f"\n{n_cw} child-windows with at least 6,000 verb tokens. "
          f"Full sample: median {full.N.median():.0f} verb types seen, {full.e.median():.0f} irregular")
    for col, lab in [("N_rel", "Verb types: estimate / types seen in the full sample"),
                     ("e_rel", "Irregular types: estimate / irregulars seen in the full sample"),
                     ("irr_share", "Estimated irregular share")]:
        t = res.pivot_table(index="frac", columns="est", values=col, aggfunc="median").sort_index(ascending=False)
        t.index = [f"1/{int(round(1/f))}" if f < 1 else "all" for f in t.index]
        print(f"\n{lab} (median over child-windows)")
        print(t[["naive", "chao1", "ht_input", "ht_child", "model"]].round(2).to_string())
    med_m = res[res.est == "naive"].groupby("frac").m.median().sort_index(ascending=False)
    print("\nmedian verb tokens at each level:", dict(zip([f"1/{int(round(1/f))}" for f in med_m.index], med_m.astype(int))))
