"""Write the small aggregate file the book's empirical chapter renders from.

Reads the derived tables in data/ (pulled from Wordbank and childes-db, both
public) and writes notebooks/results/empirical.json. Aggregates only: no rows
per child, no identifiers.
"""
import json
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, "data")
import tail_model as T
from estimators import load as load_child

rng = np.random.default_rng(0)
out = {}

# ---- map of English irregular verbs against input frequency ----
v, items, _ = T.load(5)
s = v.sort_values("n_input", ascending=False)
cum = s.irregular.cumsum().values
tok = s.n_input.cumsum().values / s.n_input.sum()
ks = [10, 20, 50, 100, 200, 300, 500, 800, 1200, len(s)]
out["irregular_map"] = {"k": ks, "irregular": [int(cum[k - 1]) for k in ks],
                        "token_share": [float(tok[k - 1]) for k in ks],
                        "all_k": list(range(1, len(s) + 1)), "all_irregular": [int(x) for x in cum],
                        "n_verbs": int(len(s)), "n_irregular": int(s.irregular.sum())}

# ---- English Wordbank: checklist counts and reported overregularisation ----
d = pd.read_csv("data/english_ws.csv")
d = d[d.n_overreg_items == 31]
bins = [0, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 103]
d["bin"] = pd.cut(d.n_verbs, bins, include_lowest=True)
g = d.groupby("bin", observed=True)
out["wordbank_english"] = {
    "n_admins": int(len(d)), "n_children": int(d.child_id.nunique()),
    "verbs": [float(x) for x in g.n_verbs.mean()],
    "n": [int(x) for x in g.size()],
    "exception_share": [float(x) for x in g.n_irreg.sum() / g.n_verbs.sum()],
    "any_overreg": [float(x) for x in g.apply(lambda x: (x.n_overreg > 0).mean(), include_groups=False)],
    "checklist_verbs": 103, "checklist_irregular": 46}

# ---- tail model: how far the assumptions move the predicted onset ----
ns = np.arange(3, 101)
rows = []
for beta, delta, label in [(0.30, 0.0, "slope fitted to parent report"),
                           (0.30, 1.0, "same, off-checklist verbs harder"),
                           (0.69, 0.2, "slope fitted to children's production"),
                           (1.00, 0.2, "steeper slope")]:
    inv = T.inventory(v, beta, delta, ns)
    at = inv[inv.n == 90].iloc[0]
    rows.append({"assumption": label, "verbs_at_90": float(at.N), "irregular_at_90": float(at.e),
                 "onset_TP": T.crossing(inv, "TP"), "onset_30": T.crossing(inv, 0.3)})
out["tail_model"] = rows

# ---- Norwegian Wordbank ----
nw = pd.read_csv("data/norwegian_ws.csv")
nw["n_verbs"] = nw[["S", "W1", "W2", "W3"]].sum(axis=1)
nw = nw[nw.production > 0]
big = nw[nw.n_verbs > 95]
pairs = [("drikket", "drikte"), ("finnet", "finte"), ("fryset", "fryste"), ("hjelpet", "hjelpte"),
         ("holdet", "holdte"), ("løpet", "løpte"), ("sprekket", "sprekte"), ("synget", "syngte")]
oi = pd.read_csv("data/norwegian_overreg_items.csv").set_index("form").n
out["norwegian"] = {
    "n_admins": int(len(nw)), "n_children": int(nw.child_id.nunique()),
    "checklist": {"strong": 40, "weak -et/-a": 38, "weak -te": 26, "weak -de/-dde": 3},
    "share_known": {k: float(nw[c].sum() / nw.n_verbs.sum()) for k, c in
                    [("strong", "S"), ("weak -et/-a", "W1"), ("weak -te", "W2"), ("weak -de/-dde", "W3")]},
    "overreg_near_ceiling": float((big[["over_et", "over_te", "over_de"]].sum(axis=1) > 0).mean()),
    "pairs": [{"et": a, "n_et": int(oi.get(a, 0)), "te": b, "n_te": int(oi.get(b, 0))} for a, b in pairs]}

# ---- CHILDES: verb types at a fixed sample size, by age ----
ch, inp = load_child()
lex = inp.index
irr = lex.isin(T.IRREGULAR)
rows = []
for lo in range(18, 42, 3):
    w = ch[(ch.month >= lo) & (ch.month < lo + 3)]
    tot = w.groupby("target_child_id").n.sum()
    for cid in tot[tot >= 1000].index:
        c = w[w.target_child_id == cid].groupby("stem").n.sum().reindex(lex, fill_value=0).values.astype(int)
        acc = [((x > 0).sum(), (x[irr] > 0).sum()) for x in (rng.multivariate_hypergeometric(c, 1000) for _ in range(20))]
        rows.append((lo, *np.mean(acc, axis=0)))
r = pd.DataFrame(rows, columns=["lo", "types", "irregular"])
g = r.groupby("lo")
out["rarefaction"] = {"tokens": 1000, "age": [int(x) for x in g.size().index], "children": [int(x) for x in g.size()],
                      "types_median": [float(x) for x in g.types.median()],
                      "types_q25": [float(x) for x in g.types.quantile(.25)],
                      "types_q75": [float(x) for x in g.types.quantile(.75)],
                      "irregular_median": [float(x) for x in g.irregular.median()]}

# ---- CHILDES: raw counts under thinning ----
val = pd.read_csv("data/estimator_validation.csv")
full = val[(val.frac == 1) & (val.est == "naive")].set_index(["child", "window"])[["N", "e"]]
val = val.join(full, on=["child", "window"], rsuffix="_full")
nv = val[val.est == "naive"].groupby("frac").apply(lambda x: pd.Series({
    "tokens": x.m.median(), "types_rel": (x.N / x.N_full).median(),
    "irregular_rel": (x.e / x.e_full).median(), "irregular_share": (x.e / x.N).median()}), include_groups=False)
nv = nv.sort_index(ascending=False)
out["thinning"] = {"n_windows": int(full.shape[0]), **{k: [float(x) for x in nv[k]] for k in nv.columns}}

# ---- CHILDES: densest English corpora ----
h = pd.read_csv("data/childes_hours.csv").sort_values("tokens_18_42mo", ascending=False).head(10)
out["dense"] = [{"corpus": a, "tokens": int(b), "hours": (None if not c or np.isnan(c) or c == 0 else float(c))}
                for a, b, c in zip(h.corpus, h.tokens_18_42mo, h.hours)]
out["n_children_50k"] = int((pd.read_csv("data/childes_density.csv").tokens_18_42mo >= 50000).sum())

json.dump(out, open("notebooks/results/empirical.json", "w"), indent=1)
print("wrote notebooks/results/empirical.json", {k: (len(v) if hasattr(v, "__len__") else v) for k, v in out.items()})
