"""Numerical checks on Yang's derivation of the Tolerance Principle.

Check 1: solve the cost equation exactly and compare with N / ln N.
Check 2: drop the assumption that exceptions are frequency-neutral.

Cost model (Yang 2016): items are Zipfian, p_i = 1 / (i * H_N).
  Listing:  every item costs its frequency rank.          T_list = N / H_N
  Rule:     an exception costs its rank among exceptions;
            a regular costs e (it waits for all exceptions).
"""

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

rng = np.random.default_rng(0)


def harmonic(n):
    return np.sum(1.0 / np.arange(1, n + 1))


def t_list(N):
    return N / harmonic(N)


def t_rule_yang(N, e):
    """Yang's closed form: exceptions carry token mass e/N and are
    themselves Zipfian over e items."""
    return (e / N) * (e / harmonic(e)) + (1 - e / N) * e


def t_rule_set(p, exc):
    """Cost for an explicit exception set (indices into rank-ordered p)."""
    exc = np.sort(exc)
    e = len(exc)
    return np.sum(p[exc] * np.arange(1, e + 1)) + (1 - p[exc].sum()) * e


def exact_threshold_yang(N):
    """Largest integer e (below N) for which the rule is no slower than listing."""
    target = t_list(N)
    best = 0
    for e in range(1, N):
        if t_rule_yang(N, e) <= target:
            best = e
        else:
            break
    return best


def threshold_biased(N, beta, n_samp=200, e_grid=None):
    """Largest e for which the mean rule cost beats listing, when exceptions
    are drawn without replacement with weight rank^(-beta).
    beta = 0: frequency-neutral.  beta > 0: exceptions tend to be frequent.
    beta < 0: exceptions tend to be rare."""
    p = 1.0 / np.arange(1, N + 1)
    p /= p.sum()
    target = t_list(N)
    if e_grid is None:
        e_grid = np.arange(1, N)
    logw = -beta * np.log(np.arange(1, N + 1))
    cost = np.zeros(len(e_grid))
    for _ in range(n_samp):
        # Gumbel trick: one weighted ordering gives nested exception sets
        order = np.argsort(-(logw + rng.gumbel(size=N)))
        for k, e in enumerate(e_grid):
            cost[k] += t_rule_set(p, order[:e])
    cost /= n_samp
    worse = np.nonzero(cost > target)[0]
    if len(worse) == 0:
        return e_grid[-1]  # rule never loses
    return e_grid[worse[0]] - 1 if worse[0] > 0 else 0


if __name__ == "__main__":
    # ---- Check 1 ----
    print("Check 1: exact threshold vs N/ln N")
    print(f"{'N':>6} {'N/lnN':>8} {'floor':>6} {'exact':>6} {'N/H_N':>8}")
    Ns = [5, 6, 7, 8, 9, 10, 12, 15, 20, 30, 50, 100, 200, 500, 1000, 5000]
    for N in Ns:
        approx = N / np.log(N)
        print(f"{N:>6} {approx:>8.2f} {int(approx):>6} "
              f"{exact_threshold_yang(N):>6} {t_list(N):>8.2f}")

    allN = np.arange(4, 2001)
    exact = np.array([exact_threshold_yang(N) for N in allN])
    approx = np.floor(allN / np.log(allN)).astype(int)
    diff = exact - approx
    print(f"\nN in 4..2000: exact == floor(N/lnN) for {np.mean(diff == 0):.1%}; "
          f"difference ranges {diff.min()} to {diff.max()}")
    small = allN <= 100
    print(f"N in 4..100:  exact == floor(N/lnN) for {np.mean(diff[small] == 0):.1%}; "
          f"difference ranges {diff[small].min()} to {diff[small].max()}")

    # ---- Check 2 ----
    print("\nCheck 2: threshold when exceptions are frequency-biased")
    betas = [-1.0, -0.5, 0.0, 0.25, 0.5, 0.75, 1.0]
    Ns2 = [20, 50, 100, 200, 500, 1000]
    table = {}
    print(f"{'N':>6} {'N/lnN':>7} | " + " ".join(f"b={b:>5}" for b in betas))
    for N in Ns2:
        grid = np.unique(np.round(np.linspace(1, N - 1, min(N - 1, 150))).astype(int))
        row = [threshold_biased(N, b, n_samp=200 if N <= 200 else 60, e_grid=grid)
               for b in betas]
        table[N] = row
        print(f"{N:>6} {N/np.log(N):>7.1f} | " + " ".join(f"{r:>7}" for r in row))

    # ---- Figure ----
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    ax[0].plot(allN, exact / allN, lw=1.2, label="exact solution of cost equation")
    ax[0].plot(allN, 1 / np.log(allN), lw=1.2, ls="--", label="1 / ln N")
    ax[0].set_xscale("log")
    ax[0].set_xlabel("N (items the rule could apply to)")
    ax[0].set_ylabel("tolerated proportion of exceptions")
    ax[0].set_title("Check 1: exact vs. approximate threshold")
    ax[0].legend(frameon=False)

    for j, b in enumerate(betas):
        ax[1].plot(Ns2, [table[N][j] / N for N in Ns2], marker="o", ms=3,
                   label=f"beta = {b}")
    ax[1].plot(Ns2, [1 / np.log(N) for N in Ns2], "k--", lw=1, label="1 / ln N")
    ax[1].set_xscale("log")
    ax[1].set_xlabel("N")
    ax[1].set_ylabel("tolerated proportion of exceptions")
    ax[1].set_title("Check 2: exceptions sampled with weight rank^(-beta)")
    ax[1].legend(frameon=False, fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig("sims/tp_checks.png", dpi=150)
    print("\nwrote sims/tp_checks.png")
