"""Description-length accounts of "rule + exceptions" vs "list everything".

N items, e exceptions. Storing one form costs c nats. All lengths in nats.

Ways to say which items are exceptions:
  set      optimal code for an unordered set:  ln C(N, e) + ln(N + 1)
           (equivalently: a cheap regular/irregular flag on every lexical entry)
  list     e separate entries, each naming its item:  e ln N
           (an ordered list; the extra ln e! nats encode the order)

Ways to list everything:
  fixed    every form costs c, however common it is:  N c
  entropy  forms coded by their frequency. The regular form then gets a short
           codeword and this is the same code as "set", so there is nothing
           to compare: productivity is graded, not thresholded.
"""

import numpy as np
from scipy.special import gammaln


def log_choose(n, k):
    return gammaln(n + 1) - gammaln(k + 1) - gammaln(n - k + 1)


def thr(N, cost_rule, c):
    e = np.arange(0, N)
    bad = np.nonzero(cost_rule(N, e, c) >= N * c)[0]
    return N - 1 if len(bad) == 0 else int(bad[0]) - 1


def rule_set(N, e, c, r=0.0):
    return r + log_choose(N, e) + np.log(N + 1) + e * c


def rule_list(N, e, c, r=0.0):
    return r + e * np.log(N) + e * c


if __name__ == "__main__":
    Ns = [9, 30, 100, 1000, 10_000, 100_000]
    print("Tolerated PROPORTION of exceptions (rule vs fixed-cost lister)")
    print(f"{'N':>7} {'1/lnN':>6} | {'set c=ln2':>9} {'set c=1':>8} {'set c=ln4':>9} "
          f"| {'list c=ln2':>10} {'list c=1':>8} {'list c=ln4':>10}")
    for N in Ns:
        row = [thr(N, f, c) / N for f in (rule_set, rule_list)
               for c in (np.log(2), 1.0, np.log(4))]
        print(f"{N:>7} {1/np.log(N):>6.3f} | {row[0]:>9.3f} {row[1]:>8.3f} {row[2]:>9.3f} "
              f"| {row[3]:>10.3f} {row[4]:>8.3f} {row[5]:>10.3f}")

    print("\nSame, as COUNTS, c = 1 nat")
    print(f"{'N':>7} {'N/lnN':>8} | {'set':>7} {'list':>7}")
    for N in Ns:
        print(f"{N:>7} {N/np.log(N):>8.1f} | {thr(N, rule_set, 1.0):>7} {thr(N, rule_list, 1.0):>7}")

    print("\nWhat an ordered list costs beyond a set, at e = N / ln N")
    print(f"{'N':>7} {'e':>6} | {'e ln N':>9} {'ln C(N,e)':>10} {'difference':>11} {'ln e!':>9}")
    for N in Ns:
        e = int(N / np.log(N))
        a, b = e * np.log(N), log_choose(N, e)
        print(f"{N:>7} {e:>6} | {a:>9.1f} {b:>10.1f} {a-b:>11.1f} {gammaln(e+1):>9.1f}")

    print("\nRule whose own length grows: r = k ln N nats (set code, c = 1)")
    print(f"{'N':>7} | " + " ".join(f"k={k:>3}" for k in (0, 5, 20)))
    for N in Ns:
        print(f"{N:>7} | " + " ".join(
            f"{thr(N, lambda N_, e, c, k=k: rule_set(N_, e, c, k*np.log(N_)), 1.0)/N:>5.3f}"
            for k in (0, 5, 20)))

    print("\nFixed memory capacity B nats (set code, c = 1): most exceptions that fit")
    print(f"{'N':>7} | {'B=200':>7} {'B=2000':>7}")
    for N in Ns[2:]:
        out = []
        for B in (200, 2000):
            e = np.arange(0, N)
            ok = np.nonzero(rule_set(N, e, 1.0) <= B)[0]
            out.append(int(ok[-1]) if len(ok) else 0)
        print(f"{N:>7} | {out[0]:>7} {out[1]:>7}")
