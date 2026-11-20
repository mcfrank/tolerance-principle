"""A joint model of which verbs children know and how often they use them.

Unit: a child in a 6-month age window, with m verb tokens recorded.
For verb v and unit j:
    knows_jv ~ Bernoulli(sigmoid(theta_j - d_v))          (Rasch model of knowledge)
    count_jv | knows ~ NegBin(mean m_j * rho_v, shape alpha)   (usage among knowers)
    count_jv = 0 otherwise
theta_j  child ability;  d_v verb difficulty;  rho_v usage rate among children
who know the verb;  alpha burstiness (large = Poisson).

The point of fitting usage among KNOWERS, across many children, is that a rare
verb may be rare because few children know it, not because knowers seldom say
it. Treating the pooled rate as every child's rate inflates the estimate.

Priors (empirical Bayes, refitted each iteration):
    d_v        ~ Normal(b0 + b1 * log r_v, TAU^2)
    log rho_v  shrunk toward g0 + g1 * log r_v, worth two pseudo-tokens
where r_v is the verb's share of verb tokens in speech to children.

Estimate for a unit: N = sum_v P(knows | data), e = same over irregular verbs.
"""

import sys
import numpy as np
import pandas as pd

sys.path.insert(0, "data")
from tail_model import IRREGULAR
from estimators import load

pd.set_option("display.width", 220)
TAU = 1.5
WINDOWS = [(18, 24), (24, 30), (30, 36), (36, 42)]


def sig(x):
    return 1 / (1 + np.exp(-np.clip(x, -30, 30)))


def p_zero(mu, alpha):
    return np.exp(-mu) if np.isinf(alpha) else (alpha / (alpha + mu)) ** alpha


def build_units(ch, lex, min_tokens=300):
    idx = {s: i for i, s in enumerate(lex)}
    rows = []
    for lo, hi in WINDOWS:
        w = ch[(ch.month >= lo) & (ch.month < hi)]
        tot = w.groupby("target_child_id").n.sum()
        for cid in tot[tot >= min_tokens].index:
            rows.append((cid, lo, hi))
    C = np.zeros((len(rows), len(lex)))
    for j, (cid, lo, hi) in enumerate(rows):
        w = ch[(ch.target_child_id == cid) & (ch.month >= lo) & (ch.month < hi)].groupby("stem").n.sum()
        C[j, [idx[s] for s in w.index]] = w.values
    units = pd.DataFrame(rows, columns=["child", "lo", "hi"])
    units["m"] = C.sum(1)
    return units, C


def posterior(c, m, theta, d, rho, alpha):
    k = sig(theta - d)
    p0 = p_zero(m * rho, alpha)
    return np.where(c > 0, 1.0, k * p0 / (1 - k + k * p0))


def fit(C, m, lr, alpha=np.inf, iters=80, verbose=False):
    J, V = C.shape
    seen = C > 0
    theta = np.log(seen.sum(1) + 1.0) - np.log(seen.sum(1) + 1.0).mean()
    d = -1.0 * (lr - lr.mean())
    rho = np.exp(lr) / np.exp(lr).sum() * 1.0
    for it in range(iters):
        K = sig(theta[:, None] - d[None, :])
        P0 = p_zero(m[:, None] * rho[None, :], alpha)
        W = np.where(seen, 1.0, K * P0 / (1 - K + K * P0))
        # usage rates among knowers, shrunk toward a log-linear function of input frequency
        num, den = (W * C).sum(0), (W * m[:, None]).sum(0)
        good = num >= 20
        g1, g0 = np.polyfit(lr[good], np.log(num[good] / den[good]), 1)
        prior = np.exp(g0 + g1 * lr)
        rho = (num + 2.0) / (den + 2.0 / prior)
        # Rasch parameters, a few Newton steps
        for _ in range(3):
            K = sig(theta[:, None] - d[None, :])
            info = K * (1 - K)
            theta += ((W - K).sum(1) - theta / 100) / (info.sum(1) + 0.01)
            K = sig(theta[:, None] - d[None, :])
            info = K * (1 - K)
            b1, b0 = np.polyfit(lr, d, 1)
            mu_d = b0 + b1 * lr
            d += (-(W - K).sum(0) - (d - mu_d) / TAU**2) / (info.sum(0) + 1 / TAU**2)
        if verbose and it % 20 == 0:
            print(f"   iter {it}: mean P(know) {W.mean():.3f}; difficulty slope {b1:.2f}; rate slope {g1:.2f}")
    K = sig(theta[:, None] - d[None, :])
    mu = m[:, None] * rho[None, :]
    if np.isinf(alpha):
        from scipy.special import gammaln
        lp = C * np.log(mu) - mu - gammaln(C + 1)
    else:
        from scipy.special import gammaln
        lp = (gammaln(C + alpha) - gammaln(alpha) - gammaln(C + 1)
              + alpha * np.log(alpha / (alpha + mu)) + C * np.log(mu / (alpha + mu)))
    ll = np.where(seen, np.log(K) + lp, np.log(1 - K + K * np.exp(lp))).sum()
    return dict(theta=theta, d=d, rho=rho, alpha=alpha, ll=ll, prior_rho=(g0, g1), prior_d=(b0, b1))


def estimate_unit(c, m, par, irregular):
    """Ability and inventory for one sample, with verb parameters held fixed."""
    d, rho, alpha = par["d"], par["rho"], par["alpha"]
    theta = 0.0
    for _ in range(60):
        w = posterior(c, m, theta, d, rho, alpha)
        k = sig(theta - d)
        step = (w - k).sum() / ((k * (1 - k)).sum() + 1e-9)
        theta += np.clip(step, -1, 1)
        if abs(step) < 1e-5:
            break
    w = posterior(c, m, theta, d, rho, alpha)
    return w.sum(), w[irregular].sum(), theta


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    ch, inp = load()
    lex = inp.index
    irregular = lex.isin(IRREGULAR)
    lr = np.log((inp / inp.sum()).values)
    units, C = build_units(ch, lex)
    m = units.m.values
    print(f"{len(units)} child-windows from {units.child.nunique()} children; {len(lex)} verbs; "
          f"median {np.median(m):.0f} verb tokens per window")

    best = None
    for alpha in (np.inf, 2.0, 1.0, 0.5, 0.25):
        par = fit(C, m, lr, alpha)
        print(f"  alpha = {alpha}: log likelihood {par['ll']:.0f}")
        if best is None or par["ll"] > best["ll"]:
            best = par
    par = best
    print(f"chosen alpha = {par['alpha']}; usage rate among knowers ~ input share^{par['prior_rho'][1]:.2f}; "
          f"difficulty slope on log input share {par['prior_d'][1]:.2f}")
    np.savez("data/zip_irt_fit.npz", theta=par["theta"], d=par["d"], rho=par["rho"], alpha=par["alpha"])

    # ---- thinning validation on the dense windows ----
    dense = units[units.m >= 6000].index
    rows = []
    for j in dense:
        c = C[j].astype(int)
        for f in (1, 1 / 4, 1 / 16, 1 / 64):
            mm = int(c.sum() * f)
            acc = []
            for _ in range(1 if f == 1 else 8):
                s = c if f == 1 else rng.multivariate_hypergeometric(c, mm)
                acc.append(estimate_unit(s, mm, par, irregular)[:2] + ((s > 0).sum(), (s[irregular] > 0).sum()))
            N, e, kN, ke = np.mean(acc, axis=0)
            rows.append(dict(unit=j, frac=f, m=mm, N=N, e=e, seen=kN, seen_irr=ke))
    val = pd.DataFrame(rows)
    full = val[val.frac == 1].set_index("unit")
    val = val.join(full[["seen", "seen_irr"]], on="unit", rsuffix="_full")
    t = val.groupby("frac").apply(lambda x: pd.Series({
        "verb tokens": x.m.median(),
        "raw count / full": (x.seen / x.seen_full).median(),
        "model N / full": (x.N / x.seen_full).median(),
        "raw irregular / full": (x.seen_irr / x.seen_irr_full).median(),
        "model e / full": (x.e / x.seen_irr_full).median(),
        "model irregular share": (x.e / x.N).median()}), include_groups=False).sort_index(ascending=False)
    print(f"\nThinning validation, {len(dense)} dense child-windows (medians; 'full' = types seen in the full sample)")
    print(t.round(2).to_string())

    # ---- estimates for every unit ----
    W = np.vstack([posterior(C[j], m[j], par["theta"][j], par["d"], par["rho"], par["alpha"]) for j in range(len(units))])
    units["seen"] = (C > 0).sum(1)
    units["seen_irr"] = (C[:, irregular] > 0).sum(1)
    units["N"] = W.sum(1)
    units["e"] = W[:, irregular].sum(1)
    units.to_csv("data/unit_estimates.csv", index=False)
    dens = pd.read_csv("data/childes_density.csv").set_index("target_child_id")
    big = units[units.m >= 6000].copy()
    big["name"] = [f"{dens.corpus.get(c, '?')}/{dens.target_child_name.get(c, '?')}" for c in big.child]
    big["TP_limit"] = big.N / np.log(big.N)
    big["exc_share"] = big.e / big.N
    print("\nDense child-windows")
    print(big[["name", "lo", "m", "seen", "seen_irr", "N", "e", "exc_share", "TP_limit"]].round(2).to_string(index=False))
