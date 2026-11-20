"""First descriptive look: overregularisation against checklist verb counts (English WS)."""
import numpy as np
import pandas as pd

pd.set_option("display.width", 200)
d = pd.read_csv("data/english_ws.csv")
d = d[d.n_overreg_items == 31].copy()
d["any_overreg"] = d.n_overreg > 0
d["ed_used"] = d.ed.isin(["sometimes", "often", "sometimes/often"])
d["has_ed"] = d.ed.notna()
print(len(d), "administrations with the overregularisation list;", d.child_id.nunique(), "children\n")

bins = [0, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 103]
d["bin"] = pd.cut(d.n_verbs, bins, include_lowest=True)
g = d.groupby("bin", observed=True)
t = pd.DataFrame({
    "n": g.size(),
    "verbs": g.n_verbs.mean().round(1),
    "irregular": g.n_irreg.mean().round(1),
    "exc_prop": (g.n_irreg.sum() / g.n_verbs.sum()).round(2),
    "TP_prop": g.n_verbs.mean().apply(lambda n: 1 / np.log(n) if n > 1.5 else np.nan).round(2),
    "any_overreg": g.any_overreg.mean().round(2),
    "two_plus": g.apply(lambda x: (x.n_overreg >= 2).mean(), include_groups=False).round(2),
    "uses_ed": g.apply(lambda x: x.ed_used[x.has_ed].mean(), include_groups=False).round(2),
})
print("By number of checklist verbs produced")
print(t.to_string())

# Longitudinal: state of the checklist lexicon at the first report of overregularisation
long = d.sort_values(["child_id", "age"])
long = long[long.groupby("child_id").data_id.transform("size") >= 2]
rows = []
for cid, c in long.groupby("child_id"):
    c = c.reset_index(drop=True)
    on = np.nonzero(c.any_overreg.values)[0]
    if len(on) and on[0] > 0:                      # onset observed after a visit without it
        prev, cur = c.loc[on[0] - 1], c.loc[on[0]]
        rows.append(dict(child_id=cid, age=cur.age, gap=cur.age - prev.age,
                         N=cur.n_verbs, e=cur.n_irreg, N_prev=prev.n_verbs, e_prev=prev.n_irreg))
o = pd.DataFrame(rows)
print(f"\nLongitudinal children: {long.child_id.nunique()}; with an observed onset: {len(o)}")
o = o[o.N >= 3]
print(f"Onsets with at least 3 checklist verbs: {len(o)}; median gap between visits {o.gap.median():.0f} months")
print(o[["age", "N", "e", "N_prev", "e_prev"]].describe().loc[["25%", "50%", "75%"]].round(1).to_string())
prop = o.e / o.N
print(f"\nAt onset, on the checklist alone:")
print(f"  exceptions within N/ln N:        {np.mean(o.e <= o.N / np.log(o.N)):.1%}")
print(f"  exceptions under half of verbs:  {np.mean(prop < 0.5):.1%}")
print(f"  median exception proportion:     {prop.median():.2f}  (checklist as a whole: {46/103:.2f})")
