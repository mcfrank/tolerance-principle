"""BabyView paired data: how well does automatic child-speech attribution agree with parent report?

For every CDI administration, compare the 103 checklist verbs (parent: produces
or not) with whether the verb was attributed to the key child in recordings
within +/- 2 months.
"""
import numpy as np
import pandas as pd

pd.set_option("display.width", 220)
D = "data/babyview/"


def load():
    items = pd.read_csv(D + "cdi_items.csv")
    v = items[(items.item_kind == "word") & (items.category == "action_words")].copy()
    v["lemma"] = v.item_definition.str.replace(r" \(.*\)", "", regex=True)
    v["known"] = v.value == "produces"
    counts = pd.read_csv(D + "child_verb_counts.csv")
    totals = pd.read_csv(D + "child_totals.csv")
    lex = pd.read_csv("docs/verb_lexicon.csv").set_index("lemma")
    return items, v, counts, totals, lex


def paired_table(v, counts, half_width=2):
    rows = []
    for (cid, age, form), g in v.groupby(["child_id", "age_month", "form"]):
        w = counts[(counts.child_id == cid) & (counts.age_month.between(age - half_width, age + half_width))]
        m = w.n.sum()
        c = w.groupby("lemma").n.sum()
        gg = g[["lemma", "known"]].copy()
        gg["count"] = gg.lemma.map(c).fillna(0).astype(int)
        gg["child_id"], gg["age"], gg["form"], gg["m"] = cid, age, form, m
        gg["n_known"] = g.known.sum()
        rows.append(gg)
    return pd.concat(rows)


if __name__ == "__main__":
    items, v, counts, totals, lex = load()
    print("checklist verbs not in lexicon:", sorted(set(v.lemma) - set(lex.index)))

    t = totals.copy()
    t["bin"] = pd.cut(t.age_month, [0, 11, 14, 17, 20, 23, 26, 29, 32, 60], right=True)
    g = t.groupby("bin", observed=True)
    print("\nSpeech attributed to the key child, by age")
    print(pd.DataFrame({"child-months": g.size(), "children": g.child_id.nunique(), "hours": g.hours_lb.sum().round(0),
                        "tokens/hour": (g.n_tokens_all.sum() / g.hours_lb.sum()).round(0),
                        "verb tokens/hour": (g.n_verb_tokens_whitelist.sum() / g.hours_lb.sum()).round(1)}).to_string())

    p = paired_table(v, counts)
    p["seen"] = p["count"] > 0
    p.to_csv(D + "paired_table.csv", index=False)
    adm = p.groupby(["child_id", "age", "form"]).agg(m=("m", "first"), known=("known", "sum"),
                                                      seen=("seen", "sum")).reset_index()
    print(f"\n{len(adm)} administrations; with >= 500 verb tokens within 2 months: {(adm.m >= 500).sum()}; "
          f">= 2000: {(adm.m >= 2000).sum()}")

    ok = p[p.m >= 500].copy()
    ok["agebin"] = pd.cut(ok.age, [8, 12, 16, 20, 24, 28, 33])
    rows = []
    for b, g in ok.groupby("agebin", observed=True):
        k, s = g.known, g.seen
        rows.append({"age": str(b), "admins": g.groupby(["child_id", "age"]).ngroups,
                     "median verb tokens": g.m.median(),
                     "parent: known (of 103)": g.groupby(["child_id", "age"]).known.sum().median(),
                     "attributed to child (of 103)": g.groupby(["child_id", "age"]).seen.sum().median(),
                     "P(attributed | parent says known)": s[k].mean() if k.any() else np.nan,
                     "P(attributed | parent says NOT known)": s[~k].mean()})
    print("\nChecklist verbs: parent report against recordings (administrations with >= 500 verb tokens)")
    print(pd.DataFrame(rows).round(2).to_string(index=False))
