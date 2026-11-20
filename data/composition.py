"""Does the make-up of the verbs seen at a fixed sample size change with age,
even though their number does not? Rarefy each child's 3-month window to 1,000
verb tokens and count types by input-frequency band."""
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, "data")
from estimators import load
from tail_model import IRREGULAR

pd.set_option("display.width", 200)
rng = np.random.default_rng(0)
ch, inp = load()
lex = inp.index
rank = inp.rank(ascending=False, method="first").values
bands = [(1, 50), (51, 150), (151, 400), (401, 5000)]
M = 1000
rows = []
for lo in range(18, 42, 3):
    w = ch[(ch.month >= lo) & (ch.month < lo + 3)]
    tot = w.groupby("target_child_id").n.sum()
    for cid in tot[tot >= M].index:
        c = w[w.target_child_id == cid].groupby("stem").n.sum().reindex(lex, fill_value=0).values.astype(int)
        acc = []
        for _ in range(20):
            s = rng.multivariate_hypergeometric(c, M)
            seen = s > 0
            acc.append([(seen & (rank >= a) & (rank <= b)).sum() for a, b in bands]
                       + [s[rank > 150].sum() / M, np.median(rank[seen])])
        rows.append([lo, cid] + list(np.mean(acc, axis=0)))
cols = ["lo", "child"] + [f"types rank {a}-{b}" for a, b in bands] + ["token share beyond rank 150", "median rank of types"]
r = pd.DataFrame(rows, columns=cols)
print(r.groupby("lo").agg({**{c: "median" for c in cols[2:]}, "child": "nunique"}).round(3).to_string())
a, b = r[r.lo == 24].set_index("child"), r[r.lo == 33].set_index("child")
both = a.index.intersection(b.index)
print(f"\nsame child ({len(both)} children), 33-36 minus 24-27 months, median change:")
for c in cols[2:]:
    d = b.loc[both, c] - a.loc[both, c]
    print(f"  {c:30s} {d.median():+.3f}   (share of children increasing: {np.mean(d > 0):.2f})")
