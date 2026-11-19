"""Productivity as Bayesian model comparison: "default rule + exceptions" vs "no default".

Lexicon: N item types, e of which do not take the regular form R. Forms are
deterministic per item, so after an item's first token nothing more is learned
about it: the evidence is the type-level lexicon (N, e), whatever the token
frequencies. Zipfian sampling only decides which types have been seen so far.

Costs are negative log marginal likelihoods in nats. K is the number of
possible forms; an unpredicted form costs ln K.

Rule hypotheses (how the set of exceptions is paid for)
  sharp    each item is an exception with fixed probability 1/N
           ("a rule has about one exception")       cost ~ e ln N
  learned  exception rate eps ~ Uniform(0,1), integrated out
                                                     cost = ln C(N,e) + ln(N+1)
  sparse   eps ~ Beta(1, N): prior mean 1/N but learnable
In every case each exception also pays ln K for its form.

No-default hypotheses
  lister   every item's form is an independent draw from K forms: N ln K
  (the "learned" rule model doubles as a no-default model that has merely
   learned how common the form R is)
"""

import numpy as np
from scipy.special import gammaln, betaln
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def log_choose(n, k):
    return gammaln(n + 1) - gammaln(k + 1) - gammaln(n - k + 1)


def cost_sharp(N, e, K):
    eps = 1.0 / N
    return -(e * np.log(eps) + (N - e) * np.log(1 - eps)) + e * np.log(K)


def cost_learned(N, e, K):
    return log_choose(N, e) + np.log(N + 1) + e * np.log(K)


def cost_sparse(N, e, K):
    # eps ~ Beta(1, N); marginal of a specific set of e exceptions among N
    return -(betaln(1 + e, N + N - e) - betaln(1, N)) + e * np.log(K)


def cost_lister(N, e, K):
    return N * np.log(K)


RULES = {"sharp": cost_sharp, "learned": cost_learned, "sparse": cost_sparse}


def threshold(N, rule, alt, K):
    """Largest e at which the rule hypothesis has the higher marginal likelihood."""
    e = np.arange(0, N)
    ok = RULES[rule](N, e, K) < alt(N, e, K)
    bad = np.nonzero(~ok)[0]
    return N - 1 if len(bad) == 0 else int(bad[0]) - 1


if __name__ == "__main__":
    Ns = [9, 20, 50, 100, 200, 500, 1000, 5000]

    print("A. Sharp rule (fixed exception rate 1/N) vs no-default lister")
    Ks = [2, np.e, 4, 8, 20]
    print(f"{'N':>6} {'N/lnN':>7} | " + " ".join(f"K={k:>5.1f}" for k in Ks))
    for N in Ns:
        print(f"{N:>6} {N/np.log(N):>7.1f} | "
              + " ".join(f"{threshold(N, 'sharp', cost_lister, k):>7}" for k in Ks))

    print("\nB. Same comparison, but the rule model learns its exception rate (K = 4)")
    print(f"{'N':>6} {'N/lnN':>7} | {'sharp':>6} {'sparse':>7} {'learned':>8}")
    for N in Ns:
        print(f"{N:>6} {N/np.log(N):>7.1f} | "
              + " ".join(f"{threshold(N, r, cost_lister, 4):>7}"
                         for r in ["sharp", "sparse", "learned"]))

    print("\nC. Sharp rule vs a no-default model that learns how common R is")
    print(f"{'N':>6} | {'threshold':>9}")
    for N in Ns:
        print(f"{N:>6} | {threshold(N, 'sharp', cost_learned, 4):>9}")

    # ---- D. Development under Zipfian sampling ----
    # 1000 types, 100 exceptions concentrated among frequent items.
    rng = np.random.default_rng(2)
    N, e_true, K = 1000, 100, 4
    p = 1.0 / np.arange(1, N + 1)
    p /= p.sum()
    print(f"\nD. Development: N = {N}, {e_true} exceptions drawn with weight 1/rank")
    print("   tokens heard at which each criterion first (stably) favours the rule")
    flips = {"TP": [], "sharp": [], "learned": []}
    S_grid = np.unique(np.round(np.logspace(1, 5, 400)).astype(int))
    traj = None
    for rep in range(200):
        order = np.argsort(-(-np.log(np.arange(1, N + 1)) + rng.gumbel(size=N)))
        is_exc = np.zeros(N, bool)
        is_exc[order[:e_true]] = True
        first = rng.exponential(1.0 / p)          # time of first token of each type
        n_seen = np.array([(first <= S).sum() for S in S_grid])
        e_seen = np.array([(first[is_exc] <= S).sum() for S in S_grid])
        n = np.maximum(n_seen, 2)
        fav = {
            "TP": e_seen <= n / np.log(n),
            "sharp": cost_sharp(n, e_seen, K) < cost_lister(n, e_seen, K),
            "learned": cost_learned(n, e_seen, K) < cost_lister(n, e_seen, K),
        }
        for k in flips:
            against = np.nonzero(~fav[k])[0]
            flips[k].append(S_grid[0] if len(against) == 0
                            else (np.inf if against[-1] == len(S_grid) - 1
                                  else S_grid[against[-1] + 1]))
        if rep == 0:
            traj = (n_seen, e_seen)
    for k, v in flips.items():
        v = np.array(v)
        fin = v[np.isfinite(v)]
        print(f"   {k:>8}: median {np.median(v):>8.0f} tokens "
              f"(never within 100k tokens in {np.mean(~np.isfinite(v)):.0%} of runs)")

    # ---- Figure ----
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    NN = np.unique(np.round(np.logspace(np.log10(6), np.log10(5000), 60)).astype(int))
    for k in [2, 4, 8]:
        ax[0].plot(NN, [threshold(N_, "sharp", cost_lister, k) / N_ for N_ in NN],
                   label=f"sharp rule, K = {k}")
    ax[0].plot(NN, [threshold(N_, "learned", cost_lister, 4) / N_ for N_ in NN],
               ls=":", label="learned rate, K = 4")
    ax[0].plot(NN, [threshold(N_, "sparse", cost_lister, 4) / N_ for N_ in NN],
               ls="-.", label="sparse prior, K = 4")
    ax[0].plot(NN, 1 / np.log(NN), "k--", lw=1, label="1 / ln N")
    ax[0].set_xscale("log")
    ax[0].set_xlabel("N")
    ax[0].set_ylabel("tolerated proportion of exceptions")
    ax[0].set_title("Rule vs. no-default lister")
    ax[0].legend(frameon=False, fontsize=8)

    n_seen, e_seen = traj
    ax[1].plot(S_grid, e_seen, label="exceptions heard")
    ax[1].plot(S_grid, np.maximum(n_seen, 2) / np.log(np.maximum(n_seen, 2)),
               "k--", lw=1, label="N_seen / ln N_seen")
    ax[1].plot(S_grid, n_seen, color="0.6", label="types heard")
    ax[1].set_xscale("log")
    ax[1].set_yscale("log")
    ax[1].set_xlabel("tokens heard")
    ax[1].set_ylabel("count")
    ax[1].set_title("One learner: 1000 types, 100 frequent exceptions")
    ax[1].legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig("sims/bayes_rule.png", dpi=150)
    print("\nwrote sims/bayes_rule.png")
