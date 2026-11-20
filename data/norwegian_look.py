"""Norwegian WS: overregularisation by suffix against checklist verb counts, and longitudinal onset."""
import numpy as np
import pandas as pd

pd.set_option("display.width", 220)
d = pd.read_csv("data/norwegian_ws.csv")
d["n_verbs"] = d[["S", "W1", "W2", "W3"]].sum(axis=1)
d["over_any"] = d[["over_et", "over_te", "over_de"]].sum(axis=1)
d = d[d.production > 0]
print(len(d), "administrations;", d.child_id.nunique(), "children; ages", d.age.min(), "-", d.age.max())

d["bin"] = pd.cut(d.n_verbs, [0, 10, 20, 40, 60, 80, 95, 107], include_lowest=True)
g = d.groupby("bin", observed=True)
t = pd.DataFrame({
    "n": g.size(),
    "strong_share": (g.S.sum() / g.n_verbs.sum()).round(2),
    "W1_share": (g.W1.sum() / g.n_verbs.sum()).round(2),
    "W2_share": (g.W2.sum() / g.n_verbs.sum()).round(2),
    "any_overreg": g.apply(lambda x: (x.over_any > 0).mean(), include_groups=False).round(2),
    "any_-et": g.apply(lambda x: (x.over_et > 0).mean(), include_groups=False).round(2),
    "any_-te": g.apply(lambda x: (x.over_te > 0).mean(), include_groups=False).round(2),
    "any_-de": g.apply(lambda x: (x.over_de > 0).mean(), include_groups=False).round(2),
    "-et_per_item": (g.over_et.mean() / 17).round(3),
    "-te_per_item": (g.over_te.mean() / 10).round(3),
    "-de_per_item": (g.over_de.mean() / 10).round(3),
})
print(t.to_string())

long = d.sort_values(["child_id", "age"])
rows = []
for cid, c in long.groupby("child_id"):
    if len(c) < 2:
        continue
    c = c.reset_index(drop=True)
    on = np.nonzero((c.over_any > 0).values)[0]
    if len(on) and on[0] > 0:
        prev, cur = c.loc[on[0] - 1], c.loc[on[0]]
        first = max(["over_et", "over_te", "over_de"], key=lambda k: cur[k])
        rows.append(dict(age=cur.age, gap=cur.age - prev.age, N=cur.n_verbs, N_prev=prev.n_verbs,
                         S=cur.S, W1=cur.W1, W2=cur.W2, et=cur.over_et, te=cur.over_te, de=cur.over_de))
o = pd.DataFrame(rows)
print(f"\nChildren with an observed onset: {len(o)}; visit gap before onset: "
      f"median {o.gap.median():.0f}, quartiles {o.gap.quantile(.25):.0f}-{o.gap.quantile(.75):.0f} months")
tight = o[o.gap <= 2]
print(f"Onsets bracketed within 2 months: {len(tight)}")
print(tight[["age", "N_prev", "N", "S", "W1", "W2"]].describe().loc[["25%", "50%", "75%"]].round(1).to_string())
print("\nAt tightly bracketed onsets, share of children whose first reported overregularisations include:")
for k, lab in [("et", "-et"), ("te", "-te"), ("de", "-de/-dde")]:
    print(f"  {lab:9s} {np.mean(tight[k] > 0):.2f}")
n = tight.N
print(f"\nChecklist-only tolerance check at onset (rule = largest weak class, exceptions = all other verbs):")
exc = tight.N - tight.W1
print(f"  within N/ln N: {np.mean(exc <= n / np.log(n)):.1%};   under half: {np.mean(exc / n < 0.5):.1%};"
      f"   median exception proportion {np.median(exc / n):.2f}")
