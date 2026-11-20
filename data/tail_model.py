"""Estimate a child's full verb inventory from the 103 CDI checklist verbs (English).

Model: child with ability a knows verb v with probability
    sigmoid(a + beta * log f_v - delta * [v not on the checklist])
where f_v is the verb's frequency in child-directed speech (CHILDES, Eng-NA).
beta is fitted on the checklist verbs; a is set per child so the expected number
of checklist verbs equals the number the child produces.

delta is NOT identified by the data: checklist verbs were chosen because they
are learned early, so off-list verbs of equal frequency are probably harder.
We report results for a range of delta, and for two frequency floors on what
counts as a verb in the input.

Output: for each checklist count n, the estimated total verbs N and
irregulars e, and where each candidate threshold says -ed becomes productive.
"""

import numpy as np
import pandas as pd

pd.set_option("display.width", 220)

IRREGULAR = set("""be have do go say get make know think take see come find give tell feel become
leave put mean keep let begin hear run hold bring write sit stand lose pay meet set lead understand
speak read spend grow win teach buy send build fall cut sell light drive break wear eat hide hit
hurt shut sing sink sleep slide steal stick sting strike swim swing tear throw wake wind bite bleed
blow breed catch choose cling creep deal dig draw drink feed fight flee fling fly forbid forget
forgive freeze grind hang kneel lay lend lie quit ride ring rise seek shake shed shine shoot shrink
slit spin spit split spread spring stink stride swear sweep weep bend bet bind burst cast cost fit
bear beat bid mistake overcome undo redo withdraw awake arise outgrow rebuild rewind unwind upset
sew mow bust sneak dive""".split())
NOT_VERBS = set("""can will would should could might shall may must hafta needta gonna wanna gotta
lemme dunno ha okay goodbye""".split())


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def load(min_count):
    raw = pd.read_csv("data/childes_verbs_raw.csv")
    v = raw.groupby("stem")[["n_input", "n_child", "n_children"]].sum()
    v = v[~v.index.isin(NOT_VERBS) & v.index.str.fullmatch(r"[a-z]+")]
    items = pd.read_csv("data/english_verb_items.csv")
    checklist = sorted(items.verb.unique())
    missing = [c for c in checklist if c not in v.index]
    v["checklist"] = v.index.isin(checklist)
    v = v[(v.n_input >= min_count) | v.checklist].copy()
    v["irregular"] = v.index.isin(IRREGULAR)
    v["lf"] = np.log(v.n_input.clip(lower=1))
    v["lf"] -= v.lf[v.checklist].mean()
    return v, items, missing


def ability(n, lf_check, beta):
    """Ability at which the expected number of checklist verbs known equals n."""
    lo, hi = -40.0, 40.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if sigmoid(mid + beta * lf_check).sum() < n:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def fit_beta(v, items):
    lf = v.lf[v.checklist]
    tab = items[(items.n_verbs >= 3) & (items.n_verbs <= 100)]
    tab = tab[tab.verb.isin(lf.index)]
    x = lf.loc[tab.verb].values
    best = None
    for beta in np.linspace(0.0, 2.0, 41):
        a = {n: ability(n, lf.values, beta) for n in tab.n_verbs.unique()}
        p = sigmoid(tab.n_verbs.map(a).values + beta * x).clip(1e-9, 1 - 1e-9)
        ll = np.sum(tab.n_yes * np.log(p) + (tab.n_children - tab.n_yes) * np.log(1 - p))
        if best is None or ll > best[1]:
            best = (beta, ll)
    return best[0]


def inventory(v, beta, delta, ns):
    lf_check = v.lf[v.checklist].values
    off = (~v.checklist).values * delta
    out = []
    for n in ns:
        a = ability(n, lf_check, beta)
        p = sigmoid(a + beta * v.lf.values - off)
        out.append((n, p.sum(), p[v.irregular.values].sum(),
                    p[(v.irregular & v.checklist).values].sum()))
    return pd.DataFrame(out, columns=["n", "N", "e", "e_checklist"])


def crossing(inv, rule):
    """Smallest checklist count from which the rule is predicted productive."""
    prop = inv.e / inv.N
    if rule == "TP":
        ok = inv.e <= inv.N / np.log(inv.N)
    else:
        ok = prop < rule
    ok = ok.values & (inv.N.values > 3)
    bad = np.nonzero(~ok)[0]
    if len(bad) == 0:
        return int(inv.n.iloc[0])
    return int(inv.n.iloc[bad[-1] + 1]) if bad[-1] + 1 < len(inv) else None


if __name__ == "__main__":
    obs = pd.read_csv("data/english_ws.csv")
    obs = obs[obs.n_overreg_items == 31]
    p_over = obs.groupby("n_verbs").apply(lambda x: (x.n_overreg > 0).mean(), include_groups=False)
    ns = np.arange(3, 101)

    v, items, missing = load(5)
    print("checklist verbs missing from CHILDES list:", missing)
    lf = v.lf[v.checklist]
    easy = items[(items.n_verbs >= 20) & (items.n_verbs <= 80)].groupby("verb")[["n_yes", "n_children"]].sum()
    easy = (easy.n_yes / easy.n_children).reindex(lf.index)
    print(f"correlation of checklist verb ease with log input frequency: r = {np.corrcoef(lf, easy)[0,1]:.2f}")
    beta = fit_beta(v, items)
    print(f"fitted frequency slope beta = {beta:.2f}")
    print(f"verbs in input lexicon: {len(v)} ({v.irregular.sum()} irregular; "
          f"{(v.irregular & v.checklist).sum()} irregular on checklist)\n")

    inv = inventory(v, beta, 1.0, ns)
    show = inv[inv.n.isin([10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100])].copy()
    show["exc_prop"] = show.e / show.N
    show["TP_prop"] = 1 / np.log(show.N)
    show["P_overreg"] = [p_over.loc[max(n - 2, 0):n + 2].mean() for n in show.n]
    print("Estimated inventory (floor 5 tokens, delta = 1)")
    print(show.round(2).to_string(index=False))

    print("\nChecklist count at which each threshold predicts -ed turns productive")
    print("(blank = not by 100 checklist verbs)")
    rows = []
    for floor in (5, 20):
        v, items, _ = load(floor)
        b = fit_beta(v, items)
        for delta in (0.0, 1.0, 2.0, 3.0):
            inv = inventory(v, b, delta, ns)
            at90 = inv[inv.n == 90].iloc[0]
            rows.append(dict(floor=floor, delta=delta, verbs_at_90=round(at90.N),
                             irregular_at_90=round(at90.e),
                             majority=crossing(inv, 0.5), cut40=crossing(inv, 0.4),
                             cut30=crossing(inv, 0.3), TP=crossing(inv, "TP")))
    print(pd.DataFrame(rows).to_string(index=False))

    q = obs.n_verbs[obs.n_overreg > 0]
    print("\nObserved: share of children reported to overregularise, by checklist verbs")
    for lo, hi in [(3, 10), (11, 20), (21, 40), (41, 60), (61, 80), (81, 95), (96, 103)]:
        s = obs[(obs.n_verbs >= lo) & (obs.n_verbs <= hi)]
        print(f"  {lo:>3}-{hi:<3}: {(s.n_overreg > 0).mean():.2f}   (n = {len(s)})")
