"""Learnability models of productivity under a Zipfian sample.

Environment: N item types with Zipfian token probabilities p_i = 1/(i H_N);
e of them are exceptions to a rule. The learner hears S tokens, each showing
an item with its correct inflected form. Objective: probability of producing
the wrong form for the next token (symmetric 0/1 loss).

Learners
  lister       no rule. Correct iff the item has been heard.
  hybrid       productive rule + one-shot memorisation of exceptions.
               Wrong only on exceptions not yet heard.
  competition  productive rule that competes with memory: an exception heard
               c times is still regularised with probability 1/(1+c).
  pure_rule    productive rule, exceptions never stored.
               Wrong on every exception token.

For each learner we find the largest e at which it does no worse than the
lister, and ask whether that threshold scales like N / ln N.

Sample size is S = t * N * H_N; t = 1 is "saturation", where the rarest item
has expected count 1 and the mean number of tokens per type is H_N.
"""

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

rng = np.random.default_rng(1)
LEARNERS = ["hybrid", "competition", "pure_rule"]


def zipf(N):
    p = 1.0 / np.arange(1, N + 1)
    return p / p.sum()


def thresholds(N, t=1.0, beta=0.0, n_samp=200, n_grid=150):
    """Largest tolerated e for each rule learner (vs. the lister)."""
    p = zipf(N)
    H = np.sum(1.0 / np.arange(1, N + 1))
    S = t * N * H
    grid = np.unique(np.round(np.linspace(1, N - 1, min(N - 1, n_grid))).astype(int))
    logw = -beta * np.log(np.arange(1, N + 1))
    err = {k: np.zeros(len(grid)) for k in LEARNERS}
    lister = 0.0
    for _ in range(n_samp):
        c = rng.poisson(S * p)                       # token counts per item
        lister += np.sum(p[c == 0])
        order = np.argsort(-(logw + rng.gumbel(size=N)))   # nested exception sets
        # cumulative sums along the exception ordering give every e at once
        unheard = np.cumsum((p * (c == 0))[order])
        compete = np.cumsum((p / (1.0 + c))[order])
        mass = np.cumsum(p[order])
        err["hybrid"] += unheard[grid - 1]
        err["competition"] += compete[grid - 1]
        err["pure_rule"] += mass[grid - 1]
    lister /= n_samp
    out = {}
    for k in LEARNERS:
        worse = np.nonzero(err[k] / n_samp > lister)[0]
        if len(worse) == 0:
            out[k] = N - 1                     # the rule never loses
        else:
            out[k] = grid[worse[0] - 1] if worse[0] > 0 else 0
    return out


if __name__ == "__main__":
    Ns = [9, 20, 50, 100, 200, 500, 1000, 2000]
    res = {}
    for beta in [0.0, 1.0]:
        label = "frequency-neutral" if beta == 0 else "frequent (weight 1/rank)"
        print(f"\nExceptions {label}; sample size S = N * H_N")
        print(f"{'N':>6} {'N/lnN':>7} | {'hybrid':>7} {'compet.':>8} {'pure rule':>10}")
        for N in Ns:
            r = thresholds(N, beta=beta)
            res[(beta, N)] = r
            print(f"{N:>6} {N/np.log(N):>7.1f} | {r['hybrid']:>7} "
                  f"{r['competition']:>8} {r['pure_rule']:>10}")

    print("\nDependence on sample size (N = 500, frequency-neutral exceptions)")
    ts = [0.125, 0.25, 0.5, 1, 2, 4, 8]
    by_t = {}
    print(f"{'t':>6} {'tokens/type':>12} | {'hybrid':>7} {'compet.':>8} {'pure rule':>10}")
    for t in ts:
        r = thresholds(500, t=t)
        by_t[t] = r
        H = np.sum(1.0 / np.arange(1, 501))
        print(f"{t:>6} {t*H:>12.1f} | {r['hybrid']:>7} "
              f"{r['competition']:>8} {r['pure_rule']:>10}")
    print(f"(N/ln N at N = 500 is {500/np.log(500):.1f})")

    fig, ax = plt.subplots(1, 3, figsize=(14, 4.2))
    names = {"hybrid": "rule + memorised exceptions",
             "competition": "rule competes with memory",
             "pure_rule": "rule, exceptions never stored"}
    for j, beta in enumerate([0.0, 1.0]):
        for k in LEARNERS:
            ax[j].plot(Ns, [res[(beta, N)][k] / N for N in Ns], marker="o", ms=3,
                       label=names[k])
        ax[j].plot(Ns, [1 / np.log(N) for N in Ns], "k--", lw=1, label="1 / ln N")
        ax[j].set_xscale("log")
        ax[j].set_ylim(-0.03, 1.03)
        ax[j].set_xlabel("N")
        ax[j].set_ylabel("tolerated proportion of exceptions")
        ax[j].set_title("frequency-neutral exceptions" if beta == 0
                        else "frequent exceptions")
    ax[0].legend(frameon=False, fontsize=8)
    for k in LEARNERS:
        ax[2].plot(ts, [by_t[t][k] / 500 for t in ts], marker="o", ms=3, label=names[k])
    ax[2].axhline(1 / np.log(500), color="k", ls="--", lw=1)
    ax[2].set_xscale("log")
    ax[2].set_ylim(-0.03, 1.03)
    ax[2].set_xlabel("sample size, in units of N * H_N")
    ax[2].set_ylabel("tolerated proportion of exceptions")
    ax[2].set_title("N = 500: dependence on sample size")
    fig.tight_layout()
    fig.savefig("sims/learnability.png", dpi=150)
    print("\nwrote sims/learnability.png")


def cumulative_thresholds(N, t=1.0, beta=0.0, n_samp=200, n_grid=150):
    """Same comparison, but scoring total errors made over the whole sample.
    lister: one error per type heard.  hybrid: one per exception heard.
    competition: H_c per exception heard c times.  pure_rule: every exception token."""
    p = zipf(N)
    H = np.sum(1.0 / np.arange(1, N + 1))
    S = t * N * H
    grid = np.unique(np.round(np.linspace(1, N - 1, min(N - 1, n_grid))).astype(int))
    logw = -beta * np.log(np.arange(1, N + 1))
    harm = np.concatenate([[0.0], np.cumsum(1.0 / np.arange(1, int(S * p[0] * 3) + 50))])
    err = {k: np.zeros(len(grid)) for k in LEARNERS}
    lister = 0.0
    for _ in range(n_samp):
        c = np.minimum(rng.poisson(S * p), len(harm) - 1)
        lister += np.sum(c > 0)
        order = np.argsort(-(logw + rng.gumbel(size=N)))
        err["hybrid"] += np.cumsum((c > 0)[order])[grid - 1]
        err["competition"] += np.cumsum(harm[c][order])[grid - 1]
        err["pure_rule"] += np.cumsum(c[order])[grid - 1]
    out = {}
    for k in LEARNERS:
        worse = np.nonzero(err[k] > lister)[0]
        out[k] = N - 1 if len(worse) == 0 else (grid[worse[0] - 1] if worse[0] > 0 else 0)
    return out


if __name__ == "__main__":
    for beta in [0.0, 1.0]:
        label = "frequency-neutral" if beta == 0 else "frequent (weight 1/rank)"
        print(f"\nCUMULATIVE errors; exceptions {label}; S = N * H_N")
        print(f"{'N':>6} {'N/lnN':>7} {'N/H_N':>7} | {'hybrid':>7} {'compet.':>8} {'pure rule':>10}")
        for N in [9, 20, 50, 100, 200, 500, 1000, 2000]:
            r = cumulative_thresholds(N, beta=beta)
            H = np.sum(1.0 / np.arange(1, N + 1))
            print(f"{N:>6} {N/np.log(N):>7.1f} {N/H:>7.1f} | {r['hybrid']:>7} "
                  f"{r['competition']:>8} {r['pure_rule']:>10}")
    print("\nCUMULATIVE, N = 500, neutral: dependence on sample size")
    for t in [0.25, 0.5, 1, 2, 4]:
        r = cumulative_thresholds(500, t=t)
        print(f"  t={t:<5} competition {r['competition']:>4}   pure rule {r['pure_rule']:>4}")
