"""Simulation test of a vocabulary estimator calibrated on paired parent report + recordings.

Setting: for some children we have BOTH a CDI (103 checklist verbs marked known
or not, independent of sampling) and transcribed speech. Among verbs the parent
says the child knows, we can observe directly how often a known verb shows up
in m tokens, as a function of the verb's input frequency. That calibrated
detection function is then applied to verbs that are not on the checklist.

Truth in the simulation (real verb list, input frequencies, irregular flags and
checklist membership from CHILDES / the English CDI):
  knowledge   Rasch: P(know) = sigmoid(theta_child - d_verb); difficulty only
              weakly related to input frequency; checklist verbs easier.
  usage       a child who knows verb v uses it at rate KAPPA * r_v^GAMMA times a
              child-specific gamma factor (bursty / idiosyncratic usage).
  CDI         known verbs reported with 10% misses and 3% false alarms.

Estimators of total verbs N and irregular verbs e for each child
  raw         types seen in the transcript
  ht_ref      Horvitz-Thompson assuming every child uses each verb at its input rate
  paired      CDI answers for checklist verbs + Horvitz-Thompson for off-list
              verbs with the detection function fitted on CDI-known verbs
"""

import sys
import numpy as np
import warnings
import pandas as pd
from scipy.optimize import minimize

warnings.filterwarnings("ignore")

sys.path.insert(0, "data")
from tail_model import load

pd.set_option("display.width", 220)
KAPPA, GAMMA, ALPHA = 0.25, 0.6, 1.0     # true usage law
W_MAX = 40.0


def detect(m, r, kappa, gamma, alpha):
    """P(a known verb appears at least once in m tokens)."""
    return 1 - (1 + m * kappa * r**gamma / alpha) ** (-alpha)


def simulate(v, n_children, m, rng, checklist_usage_bonus=1.0):
    r = (v.n_input / v.n_input.sum()).values
    z = (np.log(r) - np.log(r).mean()) / np.log(r).std()
    d = -0.6 * z + rng.normal(0, 1.5, len(v)) - 1.0 * v.checklist.values
    theta = rng.normal(-2.0, 1.2, n_children)
    know = rng.random((n_children, len(v))) < 1 / (1 + np.exp(-(theta[:, None] - d[None, :])))
    rate = KAPPA * r**GAMMA * np.where(v.checklist.values, checklist_usage_bonus, 1.0)
    g = rng.gamma(ALPHA, 1 / ALPHA, know.shape)
    counts = rng.poisson(m * rate[None, :] * g) * know
    cdi = np.where(know, rng.random(know.shape) > 0.10, rng.random(know.shape) < 0.03)
    return r, know, counts, cdi


def fit_detection(counts, cdi, r, m, check):
    """Fit (kappa, gamma, alpha) on checklist verbs the parent reports as known."""
    seen = (counts[:, check] > 0)[cdi[:, check]]
    rr = np.broadcast_to(r[check], counts[:, check].shape)[cdi[:, check]]

    def nll(w):
        p = detect(m, rr, np.exp(w[0]), w[1], np.exp(w[2])).clip(1e-9, 1 - 1e-9)
        return -(np.log(p[seen]).sum() + np.log(1 - p[~seen]).sum())

    best = None
    bounds = [(np.log(1e-3), np.log(50)), (0.2, 1.3), (np.log(0.1), np.log(20))]
    for start in ([np.log(0.1), 0.8, 0.0], [np.log(1.0), 0.5, 0.0], [np.log(0.03), 1.0, 1.0]):
        o = minimize(nll, start, method="L-BFGS-B", bounds=bounds)
        if best is None or o.fun < best.fun:
            best = o
    w = best.x
    return np.exp(w[0]), w[1], np.exp(w[2])


def run(v, n_children, m, rng, bonus=1.0):
    r, know, counts, cdi = simulate(v, n_children, m, rng, bonus)
    check, irr = v.checklist.values, v.irregular.values
    seen = counts > 0
    kap, gam, alp = fit_detection(counts, cdi, r, m, check)
    pi_cal = detect(m, r, kap, gam, alp)
    pi_ref = 1 - np.exp(-m * r)
    w_cal = np.minimum(1 / pi_cal, W_MAX)
    w_ref = np.minimum(1 / np.maximum(pi_ref, 1e-12), W_MAX)
    out = []
    for j in range(n_children):
        s = seen[j]
        on_list = (cdi[j] | s) & check                    # parent report, plus anything actually heard
        est = {
            "raw": (s.sum(), (s & irr).sum()),
            "ht_ref": (w_ref[s].sum(), w_ref[s & irr].sum()),
            "paired": (on_list.sum() + w_cal[s & ~check].sum(),
                       (on_list & irr).sum() + w_cal[s & ~check & irr].sum()),
        }
        for k, (N, e) in est.items():
            out.append(dict(est=k, N=N, e=e, N_true=know[j].sum(), e_true=(know[j] & irr).sum()))
    return pd.DataFrame(out), (kap, gam, alp)


def summarise(df):
    rows = []
    for k, g in df.groupby("est", sort=False):
        tp_true = g.e_true <= g.N_true / np.log(g.N_true)
        tp_hat = g.e <= g.N / np.log(g.N)
        rows.append({"estimator": k,
                     "N: median est/true": np.median(g.N / g.N_true),
                     "N: correlation": np.corrcoef(g.N, g.N_true)[0, 1],
                     "N: typical error": np.median(np.abs(np.log(g.N / g.N_true))),
                     "e: median est/true": np.median(g.e / g.e_true),
                     "e: correlation": np.corrcoef(g.e, g.e_true)[0, 1],
                     "N/ln N verdict correct": np.mean(tp_true == tp_hat)})
    return pd.DataFrame(rows).set_index("estimator").round(2)


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    v, _, _ = load(5)
    print(f"{len(v)} verbs, {v.irregular.sum()} irregular, {v.checklist.sum()} on the checklist\n")
    for m in (500, 2000, 8000):
        df, par = run(v, 200, m, rng)
        print(f"--- {m} verb tokens per child; 200 paired children ---")
        print(f"true verbs known: median {df.N_true.median():.0f} (range {df.N_true.min()}-{df.N_true.max()}); "
              f"recovered usage law kappa={par[0]:.2f} gamma={par[1]:.2f} alpha={par[2]:.2f} (truth {KAPPA}, {GAMMA}, {ALPHA})")
        print(summarise(df).to_string(), "\n")

    print("--- How many paired children are needed? (2,000 tokens each; spread of calibration over 30 runs) ---")
    for n in (5, 10, 20, 50):
        acc = []
        for _ in range(30):
            df, par = run(v, n, 2000, rng)
            g = df[df.est == "paired"]
            acc.append((np.median(g.N / g.N_true), par[1]))
        a = np.array(acc)
        print(f"  {n:>3} children: median N est/true {np.median(a[:,0]):.2f} "
              f"(10th-90th pct {np.quantile(a[:,0], .1):.2f}-{np.quantile(a[:,0], .9):.2f}); "
              f"gamma {np.median(a[:,1]):.2f} ({np.quantile(a[:,1], .1):.2f}-{np.quantile(a[:,1], .9):.2f})")

    print("\n--- Violated assumption: checklist verbs are used more than input frequency predicts (2,000 tokens) ---")
    for bonus in (1.0, 1.5, 2.0, 3.0):
        df, _ = run(v, 200, 2000, rng, bonus)
        g = df[df.est == "paired"]
        print(f"  usage bonus x{bonus}: median N est/true {np.median(g.N / g.N_true):.2f}; "
              f"e est/true {np.median(g.e / g.e_true):.2f}; correlation {np.corrcoef(g.N, g.N_true)[0,1]:.2f}")
