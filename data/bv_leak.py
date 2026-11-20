"""BabyView: how much of the speech attributed to the key child is really other speakers?

Before about 12 months children produce no verbs, so every verb token attributed
to the key child at those ages is misattributed. That gives a per-hour leak rate."""
import numpy as np
import pandas as pd

pd.set_option("display.width", 220)
D = "data/babyview/"
tot = pd.read_csv(D + "child_totals.csv")
cnt = pd.read_csv(D + "child_verb_counts.csv")
inp = pd.read_csv(D + "input_verb_counts.csv")
forms = pd.read_csv(D + "child_verb_forms.csv")
over = set(pd.read_csv("docs/overreg_forms.csv").form)
p = pd.read_csv(D + "paired_table.csv")
lex = pd.read_csv("docs/verb_lexicon.csv").set_index("lemma")

young = tot[tot.age_month <= 12]
leak = young.groupby("child_id").agg(hours=("hours_lb", "sum"), verbs=("n_verb_tokens_whitelist", "sum"))
leak["per_hour"] = leak.verbs / leak.hours
leak = leak[leak.hours >= 10]
print(f"Leak rate from months <= 12 ({len(leak)} children with >= 10 h): median {leak.per_hour.median():.1f} "
      f"verb tokens/hour attributed to a pre-verbal child (range {leak.per_hour.min():.0f}-{leak.per_hour.max():.0f})")

# does the leaked stream look like the surrounding adult speech?
yc = cnt[cnt.age_month <= 12].groupby("lemma").n.sum()
ic = inp.groupby("lemma").n.sum()
both = pd.concat([yc, ic], axis=1, keys=["leak", "input"]).fillna(0)
print(f"lemma shares, leaked stream vs other speakers: r = "
      f"{np.corrcoef(np.log(both.leak + 1), np.log(both.input + 1))[0, 1]:.2f}; "
      f"irregular share of types in leaked stream {lex.irregular.reindex(yc.index).mean():.2f}")

t = tot.merge(leak[["per_hour"]], on="child_id", how="left")
t["per_hour"] = t.per_hour.fillna(leak.per_hour.median())
t["bin"] = pd.cut(t.age_month, [12, 17, 20, 23, 26, 29, 32, 60])
g = t.groupby("bin", observed=True)
est = pd.DataFrame({"hours": g.hours_lb.sum().round(0), "attributed verb tokens": g.n_verb_tokens_whitelist.sum(),
                    "expected leak": g.apply(lambda x: (x.hours_lb * x.per_hour).sum(), include_groups=False).round(0)})
est["share plausibly the child's"] = (1 - est["expected leak"] / est["attributed verb tokens"]).clip(lower=0).round(2)
print("\nIf the leak rate per hour stays what it was before 12 months:")
print(est.to_string())

# child-only signal: overregularised forms
f = forms.copy()
f["err"] = f.form.isin(over)
f["bin"] = pd.cut(f.age_month, [0, 12, 17, 20, 23, 26, 29, 32, 60])
e = f[f.err].groupby("bin", observed=True).agg(tokens=("n", "sum"), children=("child_id", "nunique"))
e["hours"] = pd.cut(tot.age_month, [0, 12, 17, 20, 23, 26, 29, 32, 60]).to_frame("bin").assign(h=tot.hours_lb).groupby("bin", observed=True).h.sum().round(0)
e["per 100 hours"] = (100 * e.tokens / e.hours).round(1)
print("\nOverregularised forms attributed to the key child")
print(e.to_string())
print("most common:", ", ".join(f"{a} ({b})" for a, b in f[f.err].groupby("form").n.sum().sort_values(ascending=False).head(12).items()))

# parent report as a predictor of counts, for older children
old = p[(p.age >= 24) & (p.m >= 1000)].copy()
old["r"] = old.lemma.map(lex.n_input / lex.n_input.sum())
old["fbin"] = pd.qcut(old.r, 4, labels=["rarest quarter", "2nd", "3rd", "most frequent quarter"])
q = old.groupby(["fbin", "known"], observed=True).agg(pairs=("count", "size"), seen=("seen", "mean"), mean_count=("count", "mean")).round(2)
print("\nAge >= 24 months, >= 1000 verb tokens: checklist verbs by input frequency and parent report")
print(q.to_string())
