"""A minimal fragment-grammar-style learner for one rule with exceptions.

This is a two-stage (adaptor-grammar) model with a single partially specified
fragment, small enough to score exactly. It is NOT O'Donnell's implementation.

Generative model for a token (stem i, form f):
  Word restaurant  (Pitman-Yor, discount a, concentration b). A table is either
      a whole stored word [stem_i + f], or
      the fragment [ _ + R ] with an open stem slot (the productive rule).
    A new table draws a stem and a suffix from the processes below and pays
    `rho` nats for its storage decisions.
  Stem restaurant  (Pitman-Yor a_s, b_s). Receives one customer per whole word
    table, and one customer per TOKEN generated through the fragment.
  Suffix process   Dirichlet-multinomial over K forms (symmetric alpha), with
    one count per Word table.

An analysis says, for each regular type, whether its tokens come from a whole
stored word or through the fragment. Exceptions are always stored whole.
We score analyses by exact joint log probability and take the best.
"""

import itertools
import numpy as np
from scipy.special import gammaln
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

DEFAULT = dict(a=0.0, b=1.0, a_s=0.0, b_s=1.0, alpha=1.0, K=8, rho=np.log(4.0))


def py_logp(counts, a, b):
    """Log probability of a Pitman-Yor seating arrangement with these table sizes."""
    counts = np.asarray(counts, float)
    T, n = len(counts), counts.sum()
    lp = np.sum(np.log(b + a * np.arange(1, T)))
    lp -= gammaln(b + n) - gammaln(b + 1)
    lp += np.sum(gammaln(counts - a) - gammaln(1 - a))
    return lp


def dm_logp(form_counts, alpha, K):
    fc = np.zeros(K)
    fc[: len(form_counts)] = form_counts
    T = fc.sum()
    return (gammaln(K * alpha) - gammaln(K * alpha + T)
            + np.sum(gammaln(alpha + fc) - gammaln(alpha)))


def lexicon(N, e, t=1.0, frequent=False):
    """Token counts per type and an exception mask. S = t * N * H_N tokens."""
    H = np.sum(1.0 / np.arange(1, N + 1))
    c = np.maximum(1, np.round(t * N / np.arange(1, N + 1))).astype(int)
    exc = np.zeros(N, bool)
    if e > 0:
        idx = np.arange(e) if frequent else np.round(np.linspace(0, N - 1, e + 2)[1:-1]).astype(int)
        exc[idx] = True
    return c, exc


def logp(c, exc, via_rule, a, b, a_s, b_s, alpha, K, rho):
    """Joint log probability of an analysis. via_rule: bool mask over types."""
    via_rule = via_rule & ~exc
    whole = ~via_rule
    word_tables = list(c[whole])
    if via_rule.any():
        word_tables.append(c[via_rule].sum())
    lp = py_logp(word_tables, a, b) - rho * len(word_tables)
    stem_customers = np.where(via_rule, c, 1)
    lp += py_logp(stem_customers, a_s, b_s)
    # suffix counts: form 0 = R; exceptions cycle through the other K-1 forms
    forms = np.zeros(K)
    forms[0] = (whole & ~exc).sum() + (1 if via_rule.any() else 0)
    n_exc = exc.sum()
    for k in range(1, K):
        forms[k] = len(range(k - 1, n_exc, K - 1))
    lp += dm_logp(forms, alpha, K)
    return lp


def best_analysis(c, exc, **kw):
    """Search the family 'the m rarest regular types go through the rule'
    (m = 0 is pure listing, m = all is the full rule)."""
    reg = np.nonzero(~exc)[0]
    by_rarity = reg[np.argsort(c[reg], kind="stable")]       # rarest first
    best = (-np.inf, 0)
    scores = []
    for m in range(len(reg) + 1):
        via = np.zeros(len(c), bool)
        via[by_rarity[:m]] = True
        s = logp(c, exc, via, **kw)
        scores.append(s)
        if s > best[0]:
            best = (s, m)
    return best[1], np.array(scores), by_rarity


def p_regular_novel(c, exc, m, by_rarity, a, b, alpha, K, **_):
    """Probability that a never-heard stem takes R, under the chosen analysis."""
    via = np.zeros(len(c), bool)
    via[by_rarity[:m]] = True
    n_frag = c[via].sum()
    T = (~via).sum() + (1 if m > 0 else 0)
    n_R_tables = ((~via) & ~exc).sum() + (1 if m > 0 else 0)
    pi_R = (alpha + n_R_tables) / (K * alpha + T)
    new = b + a * T
    frag = max(n_frag - a, 0) if m > 0 else 0.0
    return (frag + new * pi_R) / (frag + new)


def threshold(N, t=1.0, frequent=False, **over):
    """Largest e for which the best analysis sends any regular through the rule."""
    kw = {**DEFAULT, **over}
    last = -1
    for e in range(0, N):
        c, exc = lexicon(N, e, t, frequent)
        m, _, _ = best_analysis(c, exc, **kw)
        if m > 0:
            last = e
        elif e > last + max(3, N // 20):
            break
    return last


if __name__ == "__main__":
    # ---- Validation: is the searched family where the true optimum lives? ----
    print("Validation by exhaustive search (N = 12)")
    for e in [2, 4, 6, 8]:
        c, exc = lexicon(12, e)
        reg = np.nonzero(~exc)[0]
        top = -np.inf
        for bits in itertools.product([False, True], repeat=len(reg)):
            via = np.zeros(12, bool)
            via[reg] = bits
            top = max(top, logp(c, exc, via, **DEFAULT))
        m, scores, _ = best_analysis(c, exc, **DEFAULT)
        print(f"  e={e}: exhaustive best {top:8.3f}   family best {scores.max():8.3f}"
              f"   ({m} of {len(reg)} regulars via rule)")

    # ---- Threshold vs N ----
    Ns = [9, 20, 50, 100, 200, 500, 1000]
    variants = {
        "default": {},
        "b=0.1": dict(b=0.1, b_s=0.1),
        "b=10": dict(b=10.0, b_s=10.0),
        "discount .5": dict(a=0.5, a_s=0.5),
        "rho=0": dict(rho=0.0),
    }
    res = {k: [] for k in variants}
    print("\nLargest e at which the best analysis uses the rule (S = N * H_N, neutral exceptions)")
    print(f"{'N':>6} {'N/lnN':>7} | " + " ".join(f"{k:>12}" for k in variants))
    for N in Ns:
        row = [threshold(N, **v) for v in variants.values()]
        for k, r in zip(variants, row):
            res[k].append(r)
        print(f"{N:>6} {N/np.log(N):>7.1f} | " + " ".join(f"{r:>12}" for r in row))

    print("\nSame, default parameters: sample size and frequent exceptions")
    print(f"{'N':>6} | {'t=0.25':>7} {'t=1':>7} {'t=4':>7} {'t=16':>7} | {'frequent, t=1':>14}")
    for N in [9, 50, 200, 1000]:
        print(f"{N:>6} | " + " ".join(f"{threshold(N, t=t):>7}" for t in [0.25, 1, 4, 16])
              + f" | {threshold(N, frequent=True):>14}")

    # ---- How graded is productivity? ----
    print("\nN = 200: analysis and novel-stem prediction as exceptions increase")
    print(f"{'e':>5} {'regulars via rule':>18} {'P(R | novel stem)':>18} {'type share of R':>16}")
    es = list(range(0, 200, 5))
    pr, share = [], []
    for e in es:
        c, exc = lexicon(200, e)
        m, _, order = best_analysis(c, exc, **DEFAULT)
        p = p_regular_novel(c, exc, m, order, **DEFAULT)
        pr.append(p)
        share.append(m / max(1, 200 - e))
        if e % 20 == 0 or e > 180:
            print(f"{e:>5} {m:>10} of {200-e:<5} {p:>18.3f} {(200-e)/200:>16.2f}")

    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    for k in variants:
        ax[0].plot(Ns, np.array(res[k]) / np.array(Ns), marker="o", ms=3, label=k)
    ax[0].plot(Ns, 1 / np.log(Ns), "k--", lw=1, label="1 / ln N")
    ax[0].set_xscale("log")
    ax[0].set_ylim(0, 1.03)
    ax[0].set_xlabel("N")
    ax[0].set_ylabel("tolerated proportion of exceptions")
    ax[0].set_title("Fragment model: where the rule stops being used")
    ax[0].legend(frameon=False, fontsize=8)
    ax[1].plot(np.array(es) / 200, pr, label="P(R | novel stem)")
    ax[1].plot(np.array(es) / 200, 1 - np.array(es) / 200, color="0.6", ls=":",
               label="type share of R")
    ax[1].axvline(1 / np.log(200), color="k", ls="--", lw=1, label="tolerance threshold")
    ax[1].set_xlabel("proportion of exceptions (N = 200)")
    ax[1].set_ylabel("probability")
    ax[1].set_title("Generalisation to a novel stem")
    ax[1].legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig("sims/fragment.png", dpi=150)
    print("\nwrote sims/fragment.png")
