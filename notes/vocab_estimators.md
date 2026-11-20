# Estimating vocabulary size from sparse speech samples: Hidaka's general type-token distribution and alternatives

Provenance tags used throughout:

- [READ] = I read the full text of the source in this session.
- [ABSTRACT] = I read only the abstract or a search-engine summary of it in this session.
- [RECALLED] = from memory, not re-checked against the source in this session. Formulas under this tag are standard ones I am confident of, but verify before citing.
- [INFERENCE] = my own derivation or judgement, not a claim made by the source.

Notation: M = number of tokens sampled, K = number of distinct types observed, N = true (latent) number of types, p_i = probability of type i, f_k = number of types observed exactly k times (so K = sum_k f_k, M = sum_k k f_k, f_0 = N - K unseen).

---

## Part 1. Hidaka's general type-token distribution

### Sources and access

1. Hidaka, S. (2014). General type-token distribution. Biometrika 101(4), 999-1002. doi:10.1093/biomet/asu035.
   - [READ] arXiv version v2 (26 Jun 2014), which contains the main text and the supplementary material: https://arxiv.org/abs/1305.0328 (PDF https://arxiv.org/pdf/1305.0328)
   - Author-hosted copy of the published version (not separately read; same content expected): https://www.jaist.ac.jp/~shhidaka/cv_publications/Biometrika-2014-Hidaka.pdf
2. Hidaka, S. (2016). Estimating the latent number of types in growing corpora with reduced cost-accuracy trade-off. Journal of Child Language 43(1), 107-134. doi:10.1017/S0305000915000094 (online 24 Feb 2015).
   - [READ] full text from the author's site: https://www.jaist.ac.jp/~shhidaka/cv_publications/Hidaka2016JCL.pdf
   - Publisher page (paywalled): https://www.cambridge.org/core/journals/journal-of-child-language/article/estimating-the-latent-number-of-types-in-growing-corpora-with-reduced-costaccuracy-tradeoff/01BD3E62346E8CDCFC26CB917A099F68
   - Extraction caveat: the PDF's text layer drops all digits. I read the main text as text and re-read the key pages (114-116, 118-123, 128-129, 132-134) as page images to recover numbers. Numbers quoted below come from those images; numbers on pages I did not image are not quoted.
3. Author's project page (short summary only): https://www.jaist.ac.jp/~shhidaka/computational_cognition_lab/index.php?VocabSizeEstimation

There is no PLoS ONE paper on this. The child-language application is the 2016 Journal of Child Language paper. (Hidaka's 2013 PLoS ONE paper is about age-of-acquisition modelling, not type-token estimation; [ABSTRACT] via search listing only.)

### Model and assumptions (Biometrika 2014) [READ]

- Tokens X_1, ..., X_M are independent and identically distributed draws from a fixed discrete distribution over N types, p = (p_1, ..., p_N), p_i > 0, sum p_i = 1. This is plain multinomial sampling with replacement.
- The vocabulary is fixed (N finite, constant during sampling). No growth, no topical burstiness, no speaker or session effects.
- The word probabilities are latent, not known in advance: "the potential types are unknown a priori". The identity of words plays no role; only the vector of probabilities matters.
- For estimation, p is restricted to a parametric family indexed by N. The paper uses Zipf, p_k proportional to k^(-a), k = 1..N, so the unknowns are (a, N).

### Main results as formulas [READ]

Exact probability that the set of types observed in M tokens is exactly s (inclusion-exclusion), with pr(s) = sum_{i in s} p_i:

    pr(s | M, p) = sum_{k=0}^{|s|-1} (-1)^k  sum_{t subset of s, |t| = k}  pr(s \ t)^M            (eq. 1)

Exact distribution of the number of observed types K (the "type-token distribution"):

    pr(K | M, p) = sum_{k=1}^{K} (-1)^(K-k) * C(N-k, N-K) * sum_{s subset of {1..N}, |s| = k} pr(s)^M      (eq. 3)

where C(n, r) is the binomial coefficient. Moment generating function (Lemma 1):

    M_P(t) = sum_{k=1}^{N}  sum_{|s| = k}  pr(s)^M  e^(kt) (1 - e^t)^(N-k)

Asymptotic approximation (Theorem 1). Define, for each type i,

    q_{M,i} = 1 - (1 - p_i)^M          (probability type i appears at least once in M tokens)

and the Poisson-binomial distribution (number of successes in N independent Bernoulli trials with unequal probabilities q_{M,i}):

    Q(K | M, p) = sum_{s subset of {1..N}, |s| = K}  prod_{i in s} q_{M,i}  prod_{j not in s} (1 - q_{M,j})      (eq. 4)

Theorem 1: for fixed p, lim_{M -> infinity} max_K | pr(K | M, p) - Q(K | M, p) | = 0.

The paper does not write out the expectation, but it follows directly [INFERENCE, elementary]:

    E[K | M, p] = sum_{i=1}^{N} ( 1 - (1 - p_i)^M )
    Var_Q[K | M, p] = sum_{i=1}^{N} q_{M,i} (1 - q_{M,i})

The mean is exact under the multinomial model too (linearity of expectation); only the variance and shape rely on the approximation, which treats "type i occurred" as independent across types. Under the true multinomial model these indicators are negatively dependent, so the Poisson-binomial variance should be slightly too large. [INFERENCE]

Discrepancy to be aware of [READ + INFERENCE]: the 2016 JCL paper reprints the exact distribution (its eq. 1, in main text and Appendix 1) with the coefficient (2N-K-k)! / ((N-k)! (N-K)!) instead of the Biometrika coefficient (N-k)! / ((N-K)! (K-k)!). I checked N = 2 by hand: the Biometrika form gives pr(K=1) = p_1^M + p_2^M and pr(K=2) = 1 - p_1^M - p_2^M, which is correct; the JCL form gives 2(p_1^M + p_2^M) for K=1, which is wrong. Treat the JCL version as a typo and use the Biometrika form.

### Estimator of vocabulary size [READ]

- Data: n pairs (K_i, M_i) of type and token counts. Likelihood (eq. 5):

      L(p) = prod_{i=1}^{n} Q(K_i | M_i, p)

  maximised over a parametric family of p; the estimate of N is the support size of the maximiser. The paper calls the result the "Poisson-binomial estimator".
- Stated property: consistency. The argument is a short law-of-large-numbers sketch (as M -> infinity the likelihood tends to 1 at the true distribution and 0 elsewhere), from which the paper concludes the maximisation "may be restricted to any family of distributions in which, for any positive integer N, there is at least one distribution with N types". No finite-sample bias or variance formula, no rate, no confidence-interval theory is given.
- Practical recipe (supplement): the pairs are not independent samples. From one text of M tokens, take nested prefixes D_i = first floor(M/n)*i tokens, i = 1..n, and multiply their likelihoods as if independent. The supplement acknowledges "these data sets would not be independent as required by most estimators" and says only that n is chosen "so that the overlap between data sets does not impede estimation".
- Optimisation: continuous search over the Zipf exponent a, brute-force grid over N (N <= 2000 in the simulations). For the Alice analysis N is made smooth by treating N as Poisson(lambda) and maximising L(a, lambda) by EM; the estimate is lambda-hat.
- Inputs needed: only the type-token curve of the sample itself (K at several M). It does NOT take a reference frequency distribution as input. The reference-like ingredient is the assumed parametric shape (Zipf), whose parameters are fitted to the same curve.

Validation in the Biometrika supplement [READ]:
- Simulation: N = 1000 true types; (a) M = 1000, 1500, 2000 with a = 1; (b) M = 2000 with a = 0, 0.5, 1; 100 datasets each; prefixes every 50 tokens. Reported qualitatively from a figure: mean Poisson-binomial estimates "consistently reflect the true number of types"; Good-Turing and Horvitz-Thompson are more biased, increasingly so as a grows. No numeric bias/RMSE table. Note the fitted family equals the generating family in this test.
- Comparators as defined there: N_GT = f_1 + K (this is not the usual Good-Turing richness estimator; see Part 2) and N_HT = sum_{k>=1} f_k / (1 - (1 - k/M)^M), i.e. Horvitz-Thompson with inclusion probabilities estimated from the sample's own relative frequencies k/M.
- Alice in Wonderland: 24,168 tokens, 4,920 types as counted there. N_GT = 8346, N_HT = 6988.8, Poisson-binomial estimate 41,647.128 with "standard error 191.748", using n = 48 nested prefixes.

### Application to child language (JCL 2016) [READ]

Method changes relative to Biometrika:
- Frequency family extended to a "second-order Zipf" distribution: p_i proportional to exp( -a_1 log(i) - a_2 log(i)^2 ), i = 1..N (three unknowns: N, a_1, a_2). Justification: on log-log plots the children's ~100 most frequent words fall below the Zipf line (consistent with Pine et al. 2013); by AIC the second-order form beat first-order in 198 of 214 Brown transcripts.
- Appendix 1 describes the fit with first-order Zipf, exponent by MATLAB fminsearch, and a grid over N = 1, 2, ..., 3000 (a hard upper bound "greater than the range of the number of words for the targeted age range"). The main text and Appendix 3 say the second-order version was the one used. Input per transcript is "a series of the numbers of types and tokens" (the within-transcript type-token curve) over CLAN-extracted word stems (go/goes/went collapse to "go").

Simulations (Appendices 2-3): same design as the Biometrika supplement plus a modified Waring-Herdan estimator, N_WH = K + f_1 / ( K/M + 2 (1 - f_1/K) ) as printed (I read this from the text layer where the layout is garbled; check the original before using). Appendix 3: N = 1000, M = 1000-3000, data generated from first-order Zipf (a = 0.924) and second-order Zipf (a_1 = 0.345, a_2 = 0.066), parameters averaged from the Brown children. Read from Fig. A2 (approximate, my reading of a bar chart): Good-Turing about 800, Horvitz-Thompson about 700, Waring-Herdan about 770; type-token estimator with a first-order family about 1050 on first-order data but about 810 on second-order data; with the second-order family about 1040 on both. Error bars on the type-token estimators are wide (roughly +/- 200 on the well-specified cases). So the estimator is close to unbiased when the family is right, visibly biased when it is not, and has much larger variance than the frequency-spectrum estimators.

Study 1, longitudinal [READ]: Brown (1973) corpus in CHILDES. Adam (55 sessions, 27.1-60.4 months, 60 min), Eve (20 sessions, 18-27 months, 60 min), Sarah (139 sessions, 27.2-61.2 months, 30 min). Explicit aim: relative change, not absolute vocabulary ("our goal here is not to evaluate the absolute number of types"). Criterion: correlation of the per-session measure with the cumulative number of types observed up to that age. Raw per-session type counts: not significant for Adam and Sarah (p = .27, p = .06), significant for Eve (p = .01). Latent estimates: R > .65, p < .01 for all three, and significantly higher than the raw-count correlation in each case (p < .01).

Study 2, cross-sectional [READ]: 916 CHILDES transcripts (retrieved October 2009) with at least 1,500 child word tokens, child aged 4;2 or younger. Compared with (i) MCDI norms (652 words as counted there; 50th-percentile curve, 1;4-2;6) and (ii) counts of words below a given age in Kuperman et al. (2012) AoA ratings. Findings: for the 49 transcripts from children 2;6 or younger, latent estimates correlate 0.459 (p < .01) with the MCDI 50th-percentile curve versus 0.275 (p = .06) for raw counts; a binomial likelihood comparison also favours the latent estimate. Against AoA-based counts, neither measure predicts the mean-AoA curve; the latent estimate predicts the lower-bound (mean minus 1 SD) AoA curve (t(188) = 3.109, p = .002) and raw counts do not. The latent-minus-counted gap grows with age (R = .521, p < .001). In Fig. 4 the latent estimates run roughly 400-1300 for 2-4 year olds versus roughly 250-500 counted types (my reading of the figure).
- Internal inconsistency I could not resolve: the text gives 916 transcripts in the Method, "191 CHILDES transcripts" for the AoA regression, and "N = 135" for "all the transcripts on children aged 4;2 or younger" in the age-gap analysis.

Proposed sampling scheme: one or a few dense "reference" samples (for example days of transcripts once a year) to anchor absolute size, interpolated with cheap sparse samples (about an hour a month) whose latent estimates track relative change.

### Limitations

Stated by the author [READ]:
- A single short session reflects "only those [words] related to the particular context", not the child's whole vocabulary; hence the focus on relative change and the need for an external reference point for absolute size.
- The estimator is safe "unless the assumed class of the word frequency distribution is clearly wrong"; the family was chosen and checked post hoc, and misspecification biases the estimate (Appendix 3). Adaptive or hierarchical selection of the frequency family is left as future work.
- Children's distributions depart from Zipf at the head.
- CHILDES transcripts differ in situation, duration and task, with no principled normalisation.
- Exact distribution is intractable for large N; the nested sub-samples are not independent.

Not stated by the author; my assessment [INFERENCE]:
- Theorem 1 is an M -> infinity statement for fixed N, the regime in which K -> N and both distributions degenerate. It gives no rate and no guarantee in the sparse regime (M comparable to or smaller than N, many types with M p_i << 1) that matters for child samples. The mean is exact regardless, so the approximation is probably fine in practice, but that is not what the theorem shows.
- Treating overlapping prefixes as independent inflates the apparent information. The Alice standard error (about 192 on an estimate of 41,647, i.e. under 0.5%) is not credible as a measure of uncertainty about an extrapolation to 8.5 times the observed type count.
- Identifiability is weak. Under a flexible family, N enters only through where the fitted curve's tail is truncated; a type-token curve from a sparse sample is nearly uninformative about types with M p_i << 1. The estimate of N is therefore largely determined by the assumed tail shape. The JCL grid cap of 3000 is also a hard prior.
- The child-language validation is entirely correlational and relative. There is no case where estimated N is compared with a known true vocabulary for a real child.
- The method uses no word identities and no external frequency information, so it cannot say which words are missing, and it cannot be restricted to a word class (such as verbs) except by re-running on the verb tokens alone, with a correspondingly smaller sample and no evidence that the Zipf family suits a single word class.

How the framework could use a reference distribution [INFERENCE]: the formula E[K | M] = sum_i (1 - (1 - p_i)^M) and the Poisson-binomial likelihood accept any p. With an external per-word frequency distribution one can replace the Zipf family by "the reference distribution restricted to the child's known words and renormalised", which turns the problem into estimating which (or how many) reference words are known. That is a different and better-identified estimator than Hidaka's, and is closer to the Horvitz-Thompson and occupancy-detection approaches below. Hidaka does not do this.

---

## Part 2. Alternatives

Unless tagged otherwise, items in this part are [RECALLED]; URLs are the standard locations of the sources and were not all opened in this session.

### Good-Turing (Good 1953)
- Assumes multinomial/Poisson sampling from a fixed distribution; nonparametric. Estimates the probability mass of unseen types, not their number: P_0-hat = f_1 / M, sample coverage C-hat = 1 - f_1/M. Nearly unbiased for the missing mass at any sample size.
- Missing mass does not determine the number of missing types (a small mass can be split among arbitrarily many types), so Good-Turing alone cannot give N. "Good-Turing richness" estimators such as K / C-hat (which assumes equal probabilities; Chao and Lee 1992 add a coefficient-of-variation correction, giving ACE) are biased low under Zipf-like skew. Hidaka's "N_GT = f_1 + K" is a non-standard ad hoc version.
- Cannot use a reference distribution. Source: Good, Biometrika 40:237-264, https://doi.org/10.1093/biomet/40.3-4.237 ; Gale and Sampson 1995, https://doi.org/10.1080/09296179508590051

### Good-Toulmin (1956)
- Same assumptions. Predicts the number of new types U(t) that would appear in a further t*M tokens:  U-hat(t) = - sum_{k>=1} (-t)^k f_k = t f_1 - t^2 f_2 + t^3 f_3 - ...
- Nearly unbiased for t <= 1 (doubling the sample). For t > 1 the terms grow geometrically and the variance explodes. Answers "how many more would I see", not "how many exist". No use of reference distributions.
- Source: Good and Toulmin, Biometrika 43:45-63, https://doi.org/10.1093/biomet/43.1-2.45

### Efron and Thisted (1976)
- Poisson model per type with an arbitrary mixing distribution of rates (empirical Bayes). Uses the Good-Toulmin series with Euler-transform smoothing to push beyond t = 1, plus linear-programming lower bounds. Shakespeare: 884,647 tokens, 31,534 types; lower bound of roughly 35,000 additional words he knew but did not use.
- Gives lower bounds only; the total is not identifiable without tail assumptions; unstable for large t. No reference distribution.
- Source: Biometrika 63:435-447, https://doi.org/10.1093/biomet/63.3.435

### Chao1 and Chao-Jost
- Chao1 (Chao 1984): N-hat = K + f_1^2 / (2 f_2); bias-corrected form K + f_1 (f_1 - 1) / (2 (f_2 + 1)). Derived from a Cauchy-Schwarz inequality, so it is a nonparametric lower bound on N in expectation, tight only when the unseen and rare types have roughly equal probabilities. Under a long Zipf tail it is badly low, and it keeps rising as M grows. With-replacement assumption; the bound can fail when the sample is a large fraction of a finite population. [The with/without-replacement caveat was also noted in a secondary source seen this session: https://www.karsdorp.io/posts/20220323122150-estimating_richness_under_sampling_without_replacement/ , ABSTRACT]
- Chao-Jost (2012) and iNEXT (Chao et al. 2014): compare samples at equal coverage rather than equal size, with rarefaction/extrapolation curves anchored on the Chao1 asymptote; extrapolation is recommended only to about double the sample size. Good for fair comparison across children or sessions with unequal M; not an estimator of total N beyond the Chao1 bound.
- Neither uses a reference distribution.
- Sources: Chao 1984, Scand. J. Statist. 11:265-270, https://www.jstor.org/stable/4615964 ; Chao and Jost 2012, Ecology 93:2533-2547, https://doi.org/10.1890/11-1952.1 ; Chao et al. 2014, Ecol. Monogr. 84:45-67, https://doi.org/10.1890/13-0133.1

### Orlitsky, Suresh and Wu (2016)
- [ABSTRACT, arXiv abstract read this session] Multinomial, Poisson, hypergeometric and Bernoulli-product sampling; no distributional assumption. Estimates U(t), the number of new types in t*n further samples, by "smoothed Good-Toulmin" linear estimators. Guarantees hold uniformly over all distributions for t up to order log n, which is shown to be the best possible range; mean-square error optimal up to constants for every t.
- [RECALLED] Form: U-hat = - sum_{k>=1} (-t)^k P(L >= k) f_k, where L is an independent random truncation point (Poisson or binomial with parameters depending on n and t). I have not reproduced the tuning constants; take them from the paper.
- Consequence: with n tokens you can predict types in a sample about log n times larger and no further without assumptions; the total N (t -> infinity) is not estimable in the worst case. For a few thousand child tokens, log n is about 7-9. No reference distribution.
- Sources: PNAS 113(47):13283-13288, https://doi.org/10.1073/pnas.1607774113 ; arXiv https://arxiv.org/abs/1511.07428 ; follow-up with multiplicity (Hao and Li, NeurIPS 2020) https://proceedings.neurips.cc/paper/2020/hash/618790ae971abb5610b16c826fb72d01-Abstract.html

### LNRE models (Baayen 2001; Evert 2004; zipfR)
- Parametric population model: a type density g(pi) over type probabilities; tokens sampled independently (Poisson/binomial). Expectations:
      E[V(M)]   = integral (1 - e^(-M pi)) g(pi) d pi
      E[V_m(M)] = integral ((M pi)^m / m!) e^(-M pi) g(pi) d pi
      S = integral g(pi) d pi   (population vocabulary size; may be infinite)
  Zipf-Mandelbrot (ZM): g(pi) = C pi^(-alpha-1) on 0 < pi <= B, 0 < alpha < 1, S infinite. Finite ZM (fZM): adds a lower cutoff A > 0, making S finite and estimable. GIGP (Sichel): generalised inverse Gauss-Poisson mixing density, three parameters. Parameters are fitted to the observed spectrum (f_1, f_2, ...).
- Fails when: the estimate of S is driven by the assumed tail (ZM cannot give a finite S at all; fZM's cutoff is weakly identified from small samples); goodness-of-fit to the observed spectrum does not imply good extrapolation [ABSTRACT, Evert and Baroni's extrapolation paper via search summary]; real text violates randomness (burstiness, topic), which biases fits; small M gives unstable fits.
- Hidaka's estimator is in the same family in spirit (parametric Zipf population, expected-V curve) but fits the type-token curve rather than the frequency spectrum.
- Reference distribution: not as shipped, but g can in principle be taken from an external corpus rather than fitted. [INFERENCE]
- Sources: Baayen, Word Frequency Distributions (Kluwer 2001), https://doi.org/10.1007/978-94-010-0844-0 ; Evert 2004, "A simple LNRE model for random character sequences" (JADT), https://zipfr.r-forge.r-project.org/ ; Evert and Baroni 2007, zipfR, https://aclanthology.org/P07-2008/ ; zipfR manual https://cran.r-project.org/web/packages/zipfR/ ; Bhat and Sproat 2009, "Knowing the Unseen" (nonparametric LNRE-style estimator; reports Good-Turing underestimating) https://aclanthology.org/P09-1013.pdf [ABSTRACT]

### Horvitz-Thompson with detection probabilities
- General form: N-hat = sum over observed types i of 1 / pi_i, where pi_i = P(type i is observed at least once) = 1 - (1 - p_i)^M under multinomial sampling. Unbiased for N when the pi_i are known and all positive. Variance = sum over all N types of (1 - pi_i) / pi_i, so it is dominated by, and explodes with, types that have tiny pi_i.
- Sample-plug-in version (Chao and Shen 2003 style; this is what Hidaka benchmarks): pi_i-hat = 1 - (1 - k_i/M)^M from the type's own count k_i. This is no longer unbiased; singletons get pi-hat of about 1 - 1/e = 0.63, so each adds only about 1.6 types, and N is underestimated under heavy tails.
- With an external reference distribution [INFERENCE]: this is the natural estimator when per-word detection probabilities are known in advance. For child vocabulary the estimand is N = number of known words = sum_i z_i (z_i = 1 if the child knows word i), and N-hat = sum over observed words of 1/pi_i is unbiased if pi_i is the probability the child produces word i in a sample of this size given that the child knows it. Problems to plan for: (a) pi_i must be the child's production probability, not the adult corpus frequency; restricting a reference distribution to known words requires renormalising by the unknown known-set mass, which is circular and needs iteration or a joint model; (b) a single observed rare word with pi_i = 0.01 contributes 100 to the estimate, so truncation, Hajek-type ratio forms, or frequency-bin stratification are needed; (c) words the child knows whose pi_i is effectively 0 are invisible in principle; (d) if knowing a word and its frequency are correlated (they are), a model-based alternative is to fit P(z_i = 1) as a function of reference frequency with detection probability 1 - (1 - c p_i)^M, i.e. an occupancy-detection (zero-inflated) model as in MacKenzie et al. 2002, which also pools across sessions.
- Sources: Horvitz and Thompson 1952, JASA 47:663-685, https://doi.org/10.1080/01621459.1952.10483446 ; Chao and Shen 2003, Environ. Ecol. Stat. 10:429-443, https://doi.org/10.1023/A:1026096204727 ; MacKenzie et al. 2002, Ecology 83:2248-2255, https://doi.org/10.1890/0012-9658(2002)083[2248:ESORWD]2.0.CO;2

### Work specific to children's productive vocabulary
- Hidaka 2016 (above) [READ]: the only published application I found of an unseen-types estimator to child transcripts with validation against CDI norms.
- Mayor and Plunkett 2011 [ABSTRACT]: statistical model mapping a raw CDI score to total vocabulary by modelling shared knowledge (words on the list) and idiosyncratic knowledge (words off the list); the correction is non-linear and largest at older ages and high CDI scores; provides revised norms and a conversion table. Uses CDI norming data (item-level acquisition proportions) as its reference, not word frequency and not transcripts. It corrects for the checklist's ceiling, not for sparse sampling. I did not read the full text and do not reproduce its formulas. https://doi.org/10.1111/j.1467-7687.2010.01024.x ; open copy listed at https://archive-ouverte.unige.ch/unige:17945 ; related proceedings paper https://escholarship.org/uc/item/6pm270z0 ; a 2014 follow-up by the same authors extends it to vocabulary overlap between children (seen in search summary only).
- Robinson and Mervis 1999 (CDI versus systematic diary; CDI under-counts as vocabulary grows) https://doi.org/10.1017/S0305000998003663 ; Tomasello and Stahl 2004 (how much sampling is enough; rare items need dense sampling) https://doi.org/10.1017/S0305000903005944 ; Rowland and Fletcher 2006 (sampling effects on error-rate and lexical-specificity estimates) https://doi.org/10.1017/S0305000906007537 . [RECALLED; all three are cited by Hidaka 2016]
- Lexical diversity measures (vocd-D, MTLD, HD-D; Malvern and Richards; McCarthy and Jarvis 2010 https://doi.org/10.3758/BRM.42.2.381): sample-size-corrected diversity indices, not vocabulary size estimates. [RECALLED]
- Segbers and Schroeder 2017, "How many words do children know? A corpus-based estimation of children's total vocabulary size" (Language Testing): school-age German, test-plus-corpus extrapolation; seen in a search listing only, not read. https://doi.org/10.1177/0265532216641152
- Wordbank (Frank, Braginsky, Yurovsky and Marchman 2017, https://doi.org/10.1017/S0305000916000209 ) and IRT models of CDI items (Kachergis et al. 2022, Behav. Res. Methods, on computerised adaptive CDIs) give per-word difficulty parameters and per-child ability estimates from parent report; these could supply P(child knows word i | ability) as a prior in a transcript-based model. [RECALLED for the IRT paper; the combination with transcripts is INFERENCE]
- Newer work: my searches found no published, validated method (through 2026) that formally combines transcript-based unseen-type estimation with CDI report, and no child-language application of Chao or Orlitsky-type estimators beyond an unpublished project proposal (https://sashacui.com/assets/pdf/01_LanguageAcquisition.pdf , seen in search summary only). The search was not exhaustive, so this is absence of evidence only.

### Which approaches can exploit an external reference frequency distribution

| Approach | Uses external per-word frequencies? |
|---|---|
| Good-Turing, Good-Toulmin, Efron-Thisted, Chao1, Chao-Jost, Orlitsky et al. | No. They use only the sample's frequency spectrum and ignore word identity. |
| LNRE (ZM, fZM, GIGP) | Not as implemented; the population density is parametric and fitted to the sample. Could be replaced by an externally derived density. [INFERENCE] |
| Hidaka 2014/2016 | Not as published (Zipf family fitted to the sample's own type-token curve). The underlying formulas accept any p, so a reference-based family is a direct modification. [INFERENCE] |
| Horvitz-Thompson with known detection probabilities | Yes; this is the estimator designed for it. Unbiased given correct probabilities, high variance from rare words. |
| Occupancy-detection / zero-inflated models with frequency as covariate | Yes; they separate "knows the word" from "produced it in this sample", pool sessions, and give per-word posteriors. [INFERENCE that this fits the problem; not found applied to child vocabulary] |
| Mayor and Plunkett 2011; CDI IRT | Use CDI norming data as the reference (acquisition order/difficulty), not corpus frequency. |

Bottom line [INFERENCE]: the distribution-free estimators give lower bounds or short-range extrapolations and are biased low exactly in the low-frequency tail. Hidaka's estimator removes that bias only by assuming a tail shape, with large variance and no use of word identity. Having a reference distribution changes the problem from "unseen species" to "detection with known probabilities", for which Horvitz-Thompson weighting or a model-based occupancy/detection likelihood (which can reuse Hidaka's expectation formula sum_i z_i (1 - (1 - p_i)^M)) is the appropriate family; the main risk moves from tail-shape assumptions to how well the reference frequencies represent the individual child's production probabilities.
