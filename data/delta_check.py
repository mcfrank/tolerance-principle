"""How much easier are checklist verbs than off-list verbs of the same input frequency?
Estimated from which verbs children actually produce in CHILDES (Eng-NA, under 48 months)."""
import sys
sys.path.insert(0, "data")
import numpy as np
from scipy.optimize import minimize
from tail_model import load, sigmoid

v, items, _ = load(5)
total = v.n_children.max()            # 'be', 'go' etc. are produced by nearly every child
k, lf, c = v.n_children.values, v.lf.values, v.checklist.values.astype(float)


def nll(w):
    p = sigmoid(w[0] + w[1] * lf + w[2] * c).clip(1e-9, 1 - 1e-9)
    return -np.sum(k * np.log(p) + (total - k) * np.log(1 - p))


w = minimize(nll, [0, 1, 0], method="BFGS").x
print(f"children in sample (proxy): {total}")
print(f"production model: slope on log input frequency = {w[1]:.2f}, checklist advantage = {w[2]:.2f} logits")
for lo, hi in [(5, 20), (20, 100), (100, 500), (500, 2000), (2000, 1e9)]:
    m = (v.n_input >= lo) & (v.n_input < hi)
    a, b = v[m & v.checklist], v[m & ~v.checklist]
    print(f"  input tokens {lo:>5}-{hi:<10.0f} checklist: {len(a):>3} verbs, {a.n_children.mean()/total if len(a) else float('nan'):.2f} of children"
          f" | off-list: {len(b):>4} verbs, {b.n_children.mean()/total:.2f} of children")
