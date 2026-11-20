# Empirical evidence base for Yang's Tolerance Principle (TP)

TP: a rule over N items is productive iff the number of exceptions e <= theta_N = N / ln N.
Compiled 2026-11-20. Question: how tightly do the data constrain the form N/ln N, as opposed to a fixed-proportion threshold or simple majority?

## Provenance tags (every number carries one)

- **[V]** verified: I read the number in the primary source text during this session (PDF text extracted and read directly).
- **[Vs]** verified via a summarising fetch tool that read the full text of the primary source for me (I did not see the raw text; small risk of transcription error).
- **[2nd]** secondhand: number reported by a different source that I did read (the reporting source is named).
- **[calc]** my own arithmetic from tagged inputs (theta = N/ln N to 2 d.p.; percentages).
- **not found**: I could not retrieve it. Nothing is filled in from memory.

Sources I read in full or in the relevant parts: Yang 2016 book (PoLP), Yang 2018 User's Guide, Yang 2023 reply to Enger, Yang 2016 "next number" ms., Schuler/Yang/Newport 2016, Hernandez/Floyd/Goldberg 2019, Ma/Chodorow/Valian 2022, Björnsdóttir 2021 (tables), van Tuijl thesis (TP sections), Jarosz et al. 2025 preprint (TP sections), Friedman/Harnad/Shi 2026 (intro). Shi & Emond 2023 and Newport 2019 were read through the summarising tool.

Sources I could NOT read (paywall / 403): Schuler 2017 dissertation, Koulaguina & Shi 2019, Yang & Montrul 2017, Kodner 2020 dissertation and Kodner 2022 (Latin), Sneller/Fruehwald/Yang 2019 (abstract only), Kapatsinski 2018, Goldberg 2018, Wittenberg & Jackendoff commentary, Enger 2022, Lawrence 2023 thesis, Gorman & Yang 2019, Belth et al. 2021 beyond abstract-level text. Nothing by Ambridge that directly tests TP was found.

## Table: one row per empirical test

"Excl. prop." = e/N. "theta/N" is the TP-tolerated proportion at that N, shown so the row can be compared with a fixed-proportion rule.

### A. Controlled experiments (N and e set by the experimenter)

| # | Source | Phenomenon / population | N | e | theta_N (theta/N) | e/N | TP predicts | Observed | How N, e counted |
|---|---|---|---|---|---|---|---|---|---|
| A1 | Schuler, Yang & Newport 2016, CogSci. https://escholarship.org/uc/item/1cn5n52p | Artificial plural marker *ka*, children, 5R/4E | 9 [V] | 4 [V] | 4.096 [V] (45.5% [calc]) | 44.4% [calc] | Productive | Children used *ka* on 91.7% of novel-noun trials [V]; 6 of 7 children at 100% [V] | Types fixed by design; each exception noun has its own marker; see section 4 |
| A2 | same | same, children, 3R/6E | 9 [V] | 6 [V] | 4.096 [V] | 66.7% [calc] | Unproductive | *ka* on 16.9% of trials [V]; 1 of 8 children at 100% [V] | same |
| A3 | same | same, adults, 5R/4E and 3R/6E | 9 [V] | 4 / 6 [V] | 4.096 [V] | 44.4% / 66.7% | Productive / unproductive | 65.0% and 51.7% *ka* [V]; no reliable condition difference (t=0.89, p=.39) [V]; matches token frequency of *ka* (75%, 58.3%) [V]. TP pattern absent in adults | same; adults on Mechanical Turk [V] |
| A4 | Hernandez, Floyd & Goldberg 2019, CogSci (preregistered). https://escholarship.org/uc/item/2sq0r49x | Novel plural/classifier on 9 familiar nouns, 4-6-year-olds, 5R/4E where the 4 exceptions share ONE competing form | 9 [V] | 4 [V] | 4.096 | 44.4% | Fully productive (TP and Sufficiency both satisfied) | Dominant form M = .625 [V]; only 14 of 31 children used it consistently, 5 used the minority form consistently, 12 mixed [V]. Not categorical | Domain of 9 counted aloud by each child; one exposure per item [V] |
| A5 | same | same children, 3R/0E (3 of 9 items attested with the form, 6 unattested) | 9 [V] | 0 attested; M = 3 [V] | Sufficiency needs M >= 5 [V] | n/a | Unproductive (Sufficiency Principle fails) | Productive use M = .935; 29 of 32 children fully productive [V]. Opposite to prediction (condition effect p = .0035 [V]) | same |
| A6 | Shi & Emond 2023, Frontiers in Psychology. https://www.frontiersin.org/articles/10.3389/fpsyg.2023.1251124/full | Word-order shift rule in Russian sentences, 14-month-olds, head-turn looking time; Condition 1 | 16 [Vs] | 5 [Vs] | 5.77 [Vs] (36.1% [calc]) | 31.25% [calc] | Productive | Generalised: M = 2.3 s, t(23) = 2.816, p = .005 [Vs] | Types = base sentences; "exceptions" are singleton sentences that never appear in shifted order (non-application, not overt counter-forms) [Vs] |
| A7 | same | Condition 2 | 16 [Vs] | 6 [Vs] | 5.77 [Vs] | 37.5% [calc] | Unproductive | No generalisation: M = 0.54 s, t(23) = 0.975, p = .17 [Vs]. Between-condition t(46) = 1.785, p = .04, d = 0.515, Bayes factor 2.067 ("weak") [Vs]; p-values look one-tailed (tool's observation) | same; 24 infants per condition inferred from df [Vs] |
| A8 | Koulaguina & Shi 2019, Language Acquisition (not read). DOI 10.1080/10489223.2019.1572148 | Same paradigm, 14-month-olds, 80% rule | 10 [2nd, Shi & Emond] | 2 [2nd] | 4.34 [2nd] | 20% | Productive | Generalised, M = 1.64 s [2nd] | As A6. Token frequency reported not to matter [2nd, Friedman et al. 2026] |
| A9 | same | 50% rule | 16 [2nd] | 8 [2nd] | 5.77 [2nd] | 50% | Unproductive | No generalisation, M = -0.47 s [2nd] | same |
| A10 | Jarosz et al. 2025, J. Memory & Language 144:104666 (preprint read). https://osf.io/preprints/psyarxiv/mbp24_v2 | Two lexically arbitrary plural suffixes, adults, Zipfian tokens, Exp. 1 | 24 [V] | 6 / 9 / 12 [V] | 7.55 [V] (31.5% [calc]) | 25% / 37.5% / 50% [V] | Categorical rule at 25%; chance at 37.5% and 50% | Gradient frequency matching; no step. Log-likelihoods: frequency matching -14.3, TP -17.1 [V]. "Not compatible with the predictions of the Tolerance Principle" [V] | Fixed by design; participants included only if they learned 23/24 items so that individual N is known [V] |
| A11 | same | Exp. 2, lower exception rates, all below threshold | 24 [V] | all < 7.55 [V]; exact values not found | 7.55 [V] | below 31.5% | No effect of condition (all categorical) | Significant gradient effect of exception rate (beta = 1.45, z = 9.34) [V]; frequency matching -13.5 vs TP -17.1 [V] | same |
| A12 | Lawrence 2023, PhD, Royal Holloway (not read; 403) | Artificial orthography, adults and children aged 9-10 | not found | not found | not found | not found | not found | Search snippet only: adult generalisation "moderated by increasing the relative frequency of irregular items" [2nd, search result] | not found |
| A13 | Schuler 2017, PhD, Georgetown (not found) | Further artificial-language tests incl. individual-level N and e | not found | not found | not found | not found | not found | Described by Yang 2018 as allowing "individualized calculation of productivity and subsequent verification"; no numbers [2nd] | not found |

### B. Corpus / developmental analyses (N and e chosen by the analyst)

| # | Source | Phenomenon / language | N | e | theta_N (theta/N) | e/N | TP predicts | Observed (and evidence type) | How N, e counted |
|---|---|---|---|---|---|---|---|---|---|
| B1 | Yang 2016 (PoLP) ch. 4. https://www.ling.upenn.edu/courses/ling5700/pop.pdf | English past tense -ed, terminal state | 1,022 [V] | 127 [V] | 147 [V] (14.4%) | 12.4% [calc] | Productive | -ed is the productive default (uncontroversial) | Verbs occurring in past tense in 5M words of child-directed N. American English, CHILDES [V] |
| B2 | same | same, COBUILD check | 1,062 [V] | 137 [V] | 152 [V] | 12.9% [calc] | Productive | same | Verbs with past tense >= 1 per million in 452M-word COBUILD [V] |
| B3 | same, Table 4.1 | -ed by frequency rank (simulated vocabulary growth) | 100 / 200 / 300 / 500 / 800 / 1,022 [V] | 54 / 76 / 92 / 103 / 121 / 127 [V] | 22 / 37 / 52 / 80 / 119 / 147 [V] | 54% / 38% / 30.7% / 20.6% / 15.1% / 12.4% [calc] | Unproductive until about 823 verbs with 122 irregulars [V] | No direct test of the 823 figure. Contradicted in spirit by B4-B6: children overregularise with far fewer verbs | Top-k most frequent past-tense verbs in the CHILDES input corpus [V] |
| B4 | same, sec. 4.1.2 | Adam, at first overregularisation (2;11) | 300 [V] | 57 [V] | 53 [V] (52.6 [calc]) | 19% [calc] | Unproductive (by 4) | Rule productive (first overregularisation). MISS, attributed by Yang to undersampling of regulars [V] | All verb stems in Adam's transcripts to 2;11, whether or not attested in past tense [V] |
| B5 | same | Eve, at first overregularisation (Yang: 1;10) | 163 [V] | 49 [V] | 32 [V] | 30.1% [calc] | Unproductive (by 17) | Rule productive. MISS, attributed to undersampling [V] | Verb stems in Eve's transcripts to 1;10 [V] |
| B6 | Ma, Chodorow & Valian 2022, CogSci. https://escholarship.org/uc/item/9f75m0p4 | 8 children at first overregularisation. Adam 306/62, Eve 93/36, Sarah 189/48, Peter 424/67, Naomi 128/43, Allison 88/36, April 50/19, Fraser 371/78 (N/e) [V] | 50-424 [V] | 19-78 [V] | 53.5, 20.5, 36.1, 70.1, 26.4, 19.7, 12.8, 62.7 [V] | 20.3%, 38.7%, 25.4%, 15.8%, 33.6%, 40.9%, 38.0%, 21.0% [calc] | Unproductive for 7 of 8 (e > theta); productive only for Peter | All 8 had produced an overregularisation. TP wrong for 7 of 8 [V]; same with the exact (harmonic-number) threshold [V] | All verb types in the child's own production up to the first overregularisation file; NLTK extraction, hand-checked [V]. Sample density varies (2 to 90 files) [V] |
| B7 | Yang 2016 ch. 4 | fly-flew irregular class among top-100 verbs | 8 [V] | 3 [V] | 3 [V] (3.85 [calc]) | 37.5% | Briefly productive | No attested overgeneralisation (e.g. lie-lew) [V]. Acknowledged miss, explained as too brief to observe | Verbs fitting the structural description among the 100 most frequent [V] |
| B8 | same | same class, larger vocabulary | 11 [V] | 5 [V] | 4 [V] (4.59 [calc]) | 45.5% | Unproductive | Unproductive | same |
| B9 | same | -ing verbs (sing/sang, sting/stung, wing/winged) | 14 [V] | majority pattern has 7 of 14 [V] | 5 [V] | 50% | No pattern productive | Rare *brang/swang* errors only (Xu & Pinker, [2nd via Yang]) | All -ing verbs in corpus; class membership by analyst [V] |
| B10 | Schuler et al. 2016 citing Yang | ing -> ang class | 8 [V] | 5 [V] | 3 [V] | 62.5% | Unproductive | Unproductive | CHILDES input corpus [V] |
| B11 | Yang 2016 ch. 4 | German participle -t | 1,900 [V] | 200 [V] | 252 [V] | 10.5% | Productive | -t is default | CELEX monomorphemic verbs (Smolka et al. 2007) [V] |
| B12 | same, sec. 4.2 | English stress, early vocabulary: "stress the initial syllable" | 402 in text [V] (420 words in the set description [V]) | 10 [V] | 67 [V] | 2.5% | Productive | Toddlers show an initial-stress/trochaic stage (Kehoe 1997, Fikkert 1994, [2nd via Yang]) | Words with frequency >= 1 per 10,000 in child-directed English [V] |
| B13 | same | English stress, larger vocabulary: initial-stress rule | 5,763 [V] | 803 [V] | 666 [V] (11.5%) | 13.9% [calc] | Unproductive, although the rule covers 86% [V] | English ends up quantity-sensitive; evidence is the adult grammar and reported stage transitions, not a targeted test | Nouns and verbs >= 1 per million in child-directed English; "lexically and prosodically distinct words" [V] |
| B14 | same, sec. 4.3 | English nominalisers as a single global default (-er most frequent) | 478 [V] | 124 if -er/or (354) is the rule [calc] | 77 [V] | 25.9% [calc] | No global default | Suffixes are conditioned by base category (consistent) | Derived nominals in corpus; suffix type counts 6/22/24/27/45/354 [V] |
| B15 | same | -ness on adjectives | 22 [V] | 2 [V] | 7 [V] | 9.1% | Productive | Productive | "Exception" = semantically unrelated to stem (goodness, witness); analyst judgment [V] |
| B16 | same | -ment on verbs | 45 [V] | 5 [V] | 11 [V] | 11.1% | Productive | Productive | same criterion [V] |
| B17 | same | -age | 24 [V] | 10 [V] | 7 [V] (7.55 [calc]) | 41.7% | Unproductive | Unproductive | Semantic transparency judged by analyst; Yang calls the judgment "subtle" [V] |
| B18 | same | -er/-or agentive | 354 [V] | 40 [V] | 60 [V] | 11.3% | Productive | Productive | Non-compositional items (banner, cellar...) as exceptions [V] |
| B19 | same | -ity, all stems | 27 [V] | 8 [V] | 8 [V] (8.19 [calc]) | 29.6% | Productive, "just on the cusp" [V] | Productive but late acquired (around age 10, [2nd via Yang]) | Analyst judgment of semantic relatedness [V] |
| B20 | same | -ity restricted to adjectival stems in -ible/-ic/-al | 21 [V] | 3 [V] | 6 [V] | 14.3% | Productive | Productive | Re-partitioned by analyst [V] |
| B21 | same, sec. 4.4; also Yang 2018 Table 3. https://lingbuzz.net/lingbuzz/004146/v2.pdf | German noun plurals, any single global suffix | 458 [V] | 286 if -(e)n (172) is the rule [calc] | 74 [V] | 62% | No global default | Consistent with literature (no majority default) | About 450 frequent noun plurals in child-directed German, classified by hand [V] |
| B22 | same | -(e)n for feminine nouns | 166 [V] | 20 [V] | 32 [V] | 12.0% | Productive | Children overuse -(e)n (Elsen 2002 etc., [2nd via Yang]) | Child-directed sample [V] |
| B23 | same | -(e)n for feminine nouns, TIGER corpus | 1,549 [V] | 103 [V] | 210 [V] | 6.6% | Productive | same | TIGER newspaper corpus [V] |
| B24 | same | non-feminine nouns, any single suffix | 292 [V] | not given per suffix | 51 [V] | not found | None productive | Motivates further partition | same |
| B25 | same | non-feminine, reduced final syllable -> zero plural | 83 [V] | 6 [V] | 18 [V] | 7.2% | Productive | Assumed productive | Phonological class defined by analyst [V] |
| B26 | same | non-feminine, final schwa -> -n | 97 [V] | 13 [V] | 21 [V] | 13.4% | Productive | Assumed productive | same |
| B27 | same | remaining non-feminine nouns -> -e | 198 [V] | 55 [V] | 37 [V] (18.9%) | 27.8% [calc] | Unproductive, although -e covers 72% [V] | Not tested directly; triggers a further split by gender | Residue after removing B25 and B26 [V] |
| B28 | same | masculine residue -> -e | 129 [V] | at most 22 [V] | 26 [V] (20.6%) | 17.1% | Productive | Assumed (Wiese's default) | same; compounds arguably miscounted [V] |
| B29 | same | neuter residue -> -e | 69 [V] | 33 [V] | 16 [V] | 47.8% | Unproductive | Leads to a further split | same |
| B30 | same | neuter monosyllables -> -er plus umlaut | 22 [V] | 6 [V] | 7 [V] (7.12 [calc]) | 27.3% | Productive (by 1) | Assumed | Subclass found by analyst [V] |
| B31 | same | remaining neuters -> -e | 46 [V] | 16 [V] | 12 [V] | 34.8% | "Just short of productivity" [V] | Further subregularities invoked | same |
| B32 | same, ch. 5 | Russian 1sg non-past, 2nd-conjugation t-stems: t -> č | 59 [V] | 22 [V] | 14 [V] (24.5%) | 37.3% [calc] | No productive alternation, hence gaps | Paradigm gaps are attested in this class (Halle 1973 etc.) | Stems attested in a Russian corpus above a frequency floor; 37 follow the majority [V] |
| B33 | same | same, all stems regardless of frequency | 66 [V] | 22 [V] | 16 [V] | 33.3% | same | same | No frequency cutoff [V] |
| B34 | same | Spanish 3rd-conjugation stem alternations | 35 [V] | no process reaches 25 [V]; exact counts not cleanly extracted | 10 [V] | at least 29% | No productive process, hence gaps | Gaps in the 3rd conjugation; 1st and 2nd have 91% and 85% no-change, productive [V] | Verb counts by conjugation from corpus [V] |
| B35 | same | Polish masc. gen. sg. -a vs -u (Dąbrowska sample) | 58 [V] | 18 [V] | 14 [V] | 31.0% | No productive suffix | Adult uncertainty reported; consistent | 40 -a, 18 -u in Dąbrowska & Szczerbiński 2006 [V] |
| B36 | same | Polish masc. gen. sg., CHILDES | 1,353 [V] | 516 [V] | 188 [V] (13.9%) | 38.1% [calc] | No productive suffix, although -a is 62% | Child error rates very low on both suffixes: 1.28% and 0.24% [V] (little overgeneralisation) | Masculine nouns in child-directed Polish, classified by one native speaker with dictionaries [V] |
| B37 | same | Polish masc. gen. pl. -ów | 612 [V] | 61 [V] | 95 [V] | 10.0% | Productive | Children overgeneralise -ów: 15.53% error on -y/-i nouns vs 0.41% on -ów nouns [V] | same |
| B38 | same, sec. 5.3 | Icelandic oblique subjects, themes: ACC vs DAT | 33 [V] | 14 [V] (ACC 14, DAT 19) | 9 [V] | 42.4% | Neither productive; levelling goes to nominative | Nominative Substitution attested | Verb counts adapted from Eythórsson 2002 dictionary-based list [V] |
| B39 | same | Icelandic experiencers: dative as rule | 264 [V] | 37 [V] | 47 [V] | 14.0% | Productive | Dative Substitution ("dative sickness") attested | same |
| B40 | same | Same rule, IcePaHC 1725-1791 and 1830-1882, just before the change | 80 / 82 [V] | 22 [V] | 18 [V] | 27.5% / 26.8% | Not yet productive ("approach the threshold") | Change emerges shortly after; Yang notes the data are too sparse [V] | Verbs in 86,000- and 104,000-word historical texts [V] |
| B41 | same, ch. 6 | a-adjectives (Sufficiency Principle) | 12 [V] | 4 unattested; M = 8 [V] | 5 [V] | 33.3% | Generalise | Adults avoid attributive a-adjectives | Class membership and "attested with right-type adverbs" by analyst [V] |
| B42 | same | Double-object -> caused-possession semantics | 42 [V] | 4 [V] | 11 [V] | 9.5% | Productive | Consistent with consensus analysis | Double-object verbs in child-directed corpus [V] |
| B43 | same | Caused possession -> double object (CHILDES vocabulary) | 49 [V] | 11 unattested; M = 38 [V] | needs M >= 37 [V] (theta 12.59 [calc]) | 22.4% | Productive, "barely cleared" [V] | Children overgeneralise (*I said them no*) | Semantic class membership decided by analyst [V] |
| B44 | Yang 2016; Yang 2018 Table 2 | Same, growing vocabulary: top 10 / 20 / 30 / 40 / 50 / 60 / 70 / 92 verbs | as listed [V] | 1 / 3 / 4 / 10 / 16 / 21 / 27 / 42 [V] | 4 / 7 / 9 / 11 / 13 / 15 / 16 / 20 [V] | 10% / 15% / 13% / 25% / 32% / 35% / 39% / 46% [calc] | Productive up to top 40, unproductive from top 50 | Retreat from overgeneralisation is the explanandum; no test tied to vocabulary size | Verb list bootstrapped from CHILDES into SUBTLEX, sorted by frequency; whether each verb "allows" double object set by analyst [V]. Row "80: 46 / 24" does not sum [V]; book text says M = 52 of 92, table says 50 [V] |
| B45 | Yang 2016 | Monosyllabic caused-possession verbs | 50 [V] | 8 [V] | 12-13 [V] | 16% | Productive | Matches the known Latinate/monosyllable restriction | same |
| B46 | same | Verbs of communication | 19 [V] | 11; M = 8 [V] | needs M >= 13 [V] | 57.9% | Unproductive | Consistent | same |
| B47 | same, ch. 7 | Determiner interchangeability (a/the), Adam's mother | 914 / 100 / 50 [V] | 637 [calc, from 277 of 914 paired with both] / 17 / 7 [V] | 134 / 22 / 12 [V] | 69.7% / 17% / 14% | Fails on full set, passes on top 50 and top 100 | Used to argue small vocabularies help; children are productive | Top-k nouns in one mother's speech [V] |
| B48 | Yang 2016 ms. "The linguistic origin of the next number". https://lingbuzz.net/lingbuzz/003824/v1.pdf | English count list | 73 [V] | 17 rote numerals [V] | 17.0 [calc] | 23.3% | Children who can count to about 73 become productive | Lipton & Spelke 2005: no child counted to 80 but not 100 [2nd via Yang]. Yang: 73 "can only be regarded as an approximation" [V] | Which numerals count as unpredictable is the analyst's call (17) [V] |
| B49 | same | Chinese count list | 46 [V] | 12 [V] | 12.0 [calc] | 26.1% | Tipping point about 46 | Chinese children count higher earlier (Miller & Stigler 1987, [2nd via Yang]) | "at most 12 exceptions" [V] |
| B50 | Björnsdóttir 2021, J. Child Language. https://doi.org/10.1017/S0305000920000732 | Icelandic gender: -r -> masc. | 70 [V] | 7 [V] | 16 [V] | 10% | Productive | Elicitation: children .99 masc. for -r/-i, adults 100% [Vs] | Nominative singular noun types in one caregiver's speech (478 types) [V] |
| B51 | same | -i -> masc. | 94 [V] | 12 [V] | 21 [V] | 12.8% | Productive | as above | same |
| B52 | same | -a -> fem. | 137 [V] | 4 [V] | 28 [V] | 2.9% | Productive | children .98, adults .99 [Vs] | same |
| B53 | same | No suffix -> neuter as default (child-directed speech) | 198 [V] | 64 [V] (neuter 134) | 37 [V] (18.9%) | 32.3% [calc] | No default gender, although neuter is 68% | Neuter given to novel suffixless nouns 29% by children (N = 26) and 48% by adults (N = 18) [Vs]; no categorical default | same |
| B54 | same | Same rule, child's own production | 121 [V] | 66 [V] (neuter 55) | 25 [V] | 54.5% | No default | same | 345 noun types in one child's speech [V] |
| B55 | same | Same rule, SUBTLEX sample | 214 [V] | 89 [V] (neuter 125) | 40 [V] | 41.6% | No default | same | 563 types in a 500,000-token random sample, >= 1 per million [Vs]/[V] |
| B56 | same (re-analysis of Spanish) | Spanish -o -> masc. | 115 [V] | 2 [V] | 24 [V] | 1.7% | Productive | Consistent with Spanish acquisition literature | Linaza corpus of child-directed Spanish [V] |
| B57 | van Tuijl thesis (Utrecht), basis of van Tuijl & Coopmans 2021, Linguistics in the Netherlands 38. https://www.ling.upenn.edu/courses/ling5700/vanTuijl2021.pdf | Dutch diminutive: -je as global default | 708 [V] | 317 stated in text; "708 - 309" as printed would be 399 [V] | 107 [V] | 45% or 56% | Unproductive | Leads to partition | Noun types in Dutch child-directed speech [V] |
| B58 | same | -je after obstruents | 399 [V] | 8 [V] | 66 [V] | 2% | Productive | Even the youngest children tested apply it [V] | same |
| B59 | same | -tje after sonorants, child-directed speech | 309 [V] | 84 [V] | 53 [V] (17.4%) | 27.2% [calc] | Unproductive | Leads to further split by vowel length | same |
| B60 | same | Same rule counted on SUBTLEX | 248 [V] | 38 [V] | 44 [V] | 15.3% [calc] | Productive. The verdict flips with the corpus | Author sets the SUBTLEX result aside ("I will ignore this for now") [V] | SUBTLEX-NL [V] |
| B61 | same | Sonorant + long vowel: -tje | 139 [V] | 12 [V] | 28 [V] | 8.6% | Productive | Wug-test broadly consistent (not examined in detail by me) | child-directed speech [V] |
| B62 | same | Sonorant + short vowel: -etje / homorganic | 170 [V] | 108 / 62 [V] | 33 [V] | 63.5% / 36.5% | Neither productive | Leads to further split | same |
| B63 | Yang 2016 ch. 3 | English -ic adjective derivation chain | 145 [V] | not found | 29 [V] | not found | not found | not found | not found |
| B64 | Sneller, Fruehwald & Yang 2019, Language Variation and Change (abstract only). https://doi.org/10.1017/S0954394519000061 | Philadelphia /æ/ restructuring | not found | not found | not found | not found | Change plausible given about 40% input from nasal-system speakers [Vs, abstract] | Change is in progress [Vs, abstract] | not found |
| B65 | Kodner 2022, NLLT 41 (not read). https://link.springer.com/article/10.1007/s11049-022-09553-2 | Latin past participles | not found | not found | not found | not found | "-itus" unproductive despite high frequency [2nd, search snippet] | not found | Perseus corpus [2nd, search snippet] |
| B66 | Belth, Payne, Beser, Kodner & Yang 2021, CogSci. https://arxiv.org/abs/2105.05790 | Automated recursive TP learner: English past tense, German plurals | not found (per-rule counts not extracted) | not found | not found | not found | Model reproduces developmental order and wug-test behaviour (abstract) | Not an independent test of the threshold form | Child-directed corpora; removes hand-partitioning |
| B67 | Yang & Montrul 2017, Second Language Research 33 (not read). DOI 10.1177/0267658316673686 | English datives, L1/L2/attrition | not found | not found | not found | not found | not found; presumably the B43-B46 counts | not found | CHILDES input analysis (abstract, [2nd]) |
| B68 | Gorman & Yang 2019 "When nobody wins" (not found) | Polish, Russian, Spanish gaps | not found | not found | not found | not found | Presumably B32-B37 | not found | not found |

## 1. Which cases discriminate N/ln N from a fixed-proportion threshold

A fixed-proportion rule ("productive iff exceptions under p") and TP disagree in two zones:

- Zone L (larger N): 1/ln N < e/N < p. TP says unproductive, the fixed rule says productive. For p = 45% this opens once N exceeds about 9; for p = 30% once N exceeds about 28.
- Zone S (small N): p < e/N <= 1/ln N. TP says productive, the fixed rule says no. Only relevant for p below about 45% and N below about 28.

### Cases in a discriminating zone, and which way they came out

Controlled experiments:

| Case | Zone | Outcome for N/ln N |
|---|---|---|
| A1 Schuler children 5R/4E (N 9, 44.4%) | S for p < 44%; does not separate TP from majority or from p = 45% | FOR (n = 7 children) |
| A4 Hernandez 5R/4E (N 9, 44.4%) | same | AGAINST (not categorical; 14 of 31) |
| A6 Shi & Emond 11/5 (N 16, 31.25%) | S for p < 31% | FOR, weakly (Bayes factor 2.07) |
| A7 Shi & Emond 10/6 (N 16, 37.5%) | L for p > 37.5%; also against majority | FOR (a null result, p = .17) |
| A10 Jarosz adults (N 24; 25%, 37.5%) | 25% is in S for p < 25%; 37.5% is in L for p > 37.5% | AGAINST: gradient, no step anywhere |
| A11 Jarosz adults Exp. 2 | all below threshold | AGAINST: graded effect where TP predicts none |
| A3 Schuler adults | not in a zone | AGAINST (probability matching) |

Corpus cases in zone L where there is some independent behavioural outcome:

| Case | e/N vs theta/N | Outcome for N/ln N |
|---|---|---|
| B4 Adam (N 300) | 19% vs 17.5% | AGAINST (rule productive although e > theta); near-threshold |
| B5 Eve, Yang's count (N 163) | 30% vs 19.6% | AGAINST |
| B6 Ma et al., 7 of 8 children (N 50-371) | 20-41% vs 17-26% | AGAINST. A fixed rule "exceptions under 45%" or simple majority fits all 8 children; TP fits 1 |
| B36 Polish gen. sg. (N 1,353) | 38% vs 13.9% | FOR vs majority and vs p = 45% (children do not overgeneralise -a). Not informative vs p = 30% |
| B53 / B55 Icelandic suffixless nouns (N 198 / 214) | 32% / 42% vs 19% | FOR vs majority and p = 45%; borderline vs p = 30% (32%). Adults pick neuter 48% of the time, children 29%: no default |
| B32 / B33 Russian t-stems (N 59 / 66) | 37% / 33% vs 24% | FOR vs majority (gaps exist). Not informative vs p = 30% |
| B48 / B49 number words | 23% and 26% at the tipping point | Weakly FOR: location of the claimed jump (about 73, about 46) fits; p = 30% would put it near 57 and 40, p = 45% near 38 and 27 [calc]. Developmental data are coarse and secondhand |

Corpus cases in zone L with no independent test (the "observation" is the linguist's own analysis, or a further partition):

- B13 English stress (13.9% vs 11.5%; the rule covers 86% yet is declared unproductive). This is the cleanest example of TP diverging from every fixed proportion above 14%, but the evidence is that adult English is quantity-sensitive, not a behavioural test at that vocabulary size.
- B27 German non-feminine -e (27.8% vs 18.9%), B31 German neuter -e (34.8% vs 26%), B59 Dutch -tje (27.2% vs 17.4%), B44 datives top-50 to top-70 (32-39% vs 23-26%), B40 Icelandic historical datives (27% vs 22%), B14 nominalisers (26% vs 16%).
- B3 past tense at 300, 500, 800 verbs (30.7%, 20.6%, 15.1% vs 17.5%, 16.1%, 15.0%): TP says -ed is not yet productive at 500 verbs. This is the prediction B4-B6 speak against.

Near-threshold cases at any N:

| Case | Margin | Verdict vs outcome |
|---|---|---|
| A1/A2 Schuler | 4 vs 4.096 (design straddles: 4 and 6, 5 untested) | FOR in children |
| A6/A7 Shi & Emond | 5 and 6 vs 5.77 | FOR, weak statistics |
| B4 Adam | 57 vs 53 | AGAINST (explained post hoc) |
| B6 Peter | 67 vs 70.1 | FOR |
| B6 April | 19 vs 12.8; Fraser 78 vs 62.7; Adam 62 vs 53.5 | AGAINST |
| B19 -ity | 8 vs 8.19 | FOR (productive; late) |
| B30 German neuter -er | 6 vs 7.12 | assumed FOR, untested |
| B31 German neuter -e | 16 vs 12 | untested |
| B43 datives | M 38 vs required 37 | FOR (children overgeneralise) |
| B44 top-40 vs top-50 datives | 10 vs 11; 16 vs 13 | untested |
| B7 fly-flew | 3 vs 3.85 | AGAINST (predicted productivity never observed) |
| B40 Icelandic | 22 vs 18 | ambiguous (just before the change) |
| B60 vs B59 Dutch | 38 vs 44 on one corpus, 84 vs 53 on another | verdict depends on corpus |

### What follows

1. The two child experiments jointly do exclude any single fixed proportion, which is the strongest point in favour of N-dependence: 4 of 9 exceptions (44.4%) were tolerated at N = 9 (A1), but 6 of 16 (37.5%) were not at N = 16 (A7). No fixed p satisfies both [calc]. Caveats: different labs, ages (5-8 years vs 14 months), tasks (production vs looking time), and exception types (overt idiosyncratic markers vs mere non-application); A7 is a null result; A4 did not reproduce categorical productivity at 5/4 when the exceptions shared a form.
2. Each experiment alone is compatible with a fixed threshold: Schuler with any p between 44.4% and 66.7%, Shi & Emond with any p between 31.25% and 37.5%.
3. Experiments cannot separate ln N from the harmonic number H_N of the actual derivation. Yang 2018 states that the exact derivation gives theta = 3 at N = 9, so 4 exceptions "should" not be tolerated [V]. At N = 16, 16/H_16 = 4.73 [calc], so 5 exceptions should not be tolerated either. Children's behaviour matches the cruder ln N approximation, not the efficiency calculation it is derived from. Yang 2018: "an idealized model of the reality does better than reality itself" [V].
4. In zone L at N of 50 to 424, the only data set with an independent, pre-specified behavioural marker of productivity (first overregularisation; B4-B6) goes against N/ln N in 7 of 8 children and is fitted by simple majority.
5. The zone-L successes (Polish, Russian, Icelandic gender) discriminate TP from simple majority and from p = 45%, but hardly from p of about 30%. They show that "majority is not enough"; they do not pin down the curvature.
6. No data set tests the specific decline of theta/N with N (45% at N = 9, 22% at N = 100, 14% at N = 1,000) with behavioural outcomes at two or more N for the same rule type.

## 2. Range of N covered, and where the evidence is thin

- Experiments: N = 9 (A1-A5), 10 (A8), 16 (A6, A7, A9), 24 (A10, A11; adults only). Nothing above 24. Child experiments stop at 16.
- At N = 9 to 24, theta/N runs from 45.5% to 31.5% [calc], so the experimental range is exactly where N/ln N is hardest to tell apart from "about 35-45%" or, at N = 9, from majority.
- Corpus analyses: N from 8 to 5,763. Most rows sit between 20 and 500. Above 1,000 there are five rows (B1, B2, B11, B23 with e/N at 6-13%, clearly productive under any rule; B36 at 38%, clearly unproductive under any p up to 38%) plus B13.
- B13 (English stress, N = 5,763, 13.9% vs 11.5%) is the only large-N case lying between theta/N and 30%, and it has no behavioural test.
- Thin or empty regions:
  - Controlled tests with N of 30 to 200 and e/N between 1/ln N and 40%. None exist.
  - Children at N = 24 or more. None.
  - Parametric designs holding e/N fixed while N varies (e.g. 37.5% at N = 8, 16, 32). None found. This is the design that would test the functional form directly.
  - Exact straddles of the threshold with adjacent integers: only A6/A7 (5 vs 6 at N = 16). Schuler used 4 vs 6, not 4 vs 5.
  - Replications: A1/A2 have 7 and 8 children per cell; the journal version (cited as Schuler, Yang & Newport 2021 by Ma et al.) was not found. A4 is a partial non-replication with a design change.
  - Token-frequency manipulations in children: only claimed secondhand for Koulaguina & Shi 2019.

## 3. Reported failures, null results and criticisms

Empirical failures or non-support:

- **Ma, Chodorow & Valian 2022** (B6): e > theta at first overregularisation for 7 of 8 CHILDES children, with either the ln N or the exact threshold [V]. Computing the TP's own processing-time quantities from each child's actual frequencies, T_rule < T_norule for only 1 of 8 (April) [V]. They also report that Yang miscounted Eve (first overregularisation at 1;8, not 1;10) [V].
- **Yang's own near-misses**: Adam 57 vs 53 and Eve 49 vs 32, both attributed to undersampling of regular verbs in transcripts [V]. The undersampling argument is not quantified into a corrected estimate.
- **Hernandez, Floyd & Goldberg 2019** (A4, A5): preregistered; 5R/4E with a shared exception form was not categorical; 3R/0E was productive against the Sufficiency Principle [V]. They also argue that Schuler's result is equally predicted by an interference/accessibility account [V].
- **Adults**: Schuler 2016 adults probability-match [V]; Jarosz et al. 2025, three experiments, find gradient frequency matching and independent type and token effects, "not compatible" with TP [V]. TP's defenders treat it as a theory of child learners, so these bound its scope more than refute it.
- **fly-flew** (B7): predicted transient productivity with no attested errors [V].
- **Small language models**: Friedman, Harnad & Shi 2026 report that BabyBERTa's learning does not follow TP [V]. Not human evidence.
- **Lawrence 2023**: adult generalisation in artificial orthography is sensitive to the relative frequency of irregulars [2nd, search snippet only]. Details not found.

Internal / derivational criticisms:

- **Approximation**: Yang 2018 Table 4 shows theta from H_N is lower than from ln N at every N (3 vs 4 at N = 9; 20 vs 22 at N = 100; 134 vs 145 at N = 1,000) [V]. Ma et al. solve the unsimplified inequality numerically and get 4.53, 23.24, 152.77 at N = 10, 100, 1,000 against 4.34, 21.71, 144.76 [V]. So "N/ln N" is one of at least three thresholds derivable from the same model.
- **Rank dependence**: Ma et al. show that with real frequencies the efficiency comparison depends on where the regulars sit in the frequency ranking; with N = 10 and 7 exceptions, a rule is "more efficient" if the regulars rank 2nd, 5th, 6th and not if they rank 8th-10th [V]. The inequality is quadratic and also licenses a rule with 97 exceptions in 100 [V].
- **Yang's own admission**: in one Schuler 5R/4E condition the five regulars were the five most frequent nouns, so full listing is actually faster than rule plus exceptions, yet children formed the rule [V]. Koulaguina & Shi used uniform, not Zipfian, frequencies, violating the derivation's assumption, yet the prediction held [V, as reported by Yang 2018]. The principle is supported where its rationale does not apply. Yang: "Use it until it breaks" [V].
- **Commentaries not read** (existence confirmed, content secondhand): Kapatsinski 2018 "On the intolerance of the Tolerance Principle" (LAB 8:6, 738-742); Goldberg 2018 "The sufficiency principle hyperinflates the price of productivity" (LAB 8:6, 727-732), which per Hernandez et al. argues the Sufficiency Principle demands unrealistically many rule-following cases [2nd]; Gries, Lidz & Perkins, Rowland, Biberauer (supportive) in the same issue [2nd, search listing]; Wittenberg & Jackendoff, cited by Yang 2023 as "conceptual" critics [2nd]; Enger 2022 (PBB 144:2), who per Yang 2023 argues TP wrongly rules out productive minority patterns and that gender cannot be a precondition for German plural learning [2nd]. Yang's replies: 2018 LAB 8:6 797-809 (not read) and Yang 2023 (read).
- **Ambridge, Dutch failures**: nothing found that reports a direct TP test. The Dutch work found (van Tuijl & Coopmans) is supportive.

Analyst degrees of freedom in counting N and e (all documented in the sources read):

1. **Which corpus**. Child-directed vs adult corpora flip the verdict for Dutch -tje (B59 vs B60) [V]. Yang 2018 argues the ratio is scale-invariant across corpora in "the best case" [V].
2. **Frequency cutoff / vocabulary size**. N is set by top-k or per-million thresholds chosen by the analyst (1 per 10,000 for early stress, 1 per million for late stress; top 40 vs top 50 datives). Verdicts change with k by construction (B3, B44, B47), and this is used as an explanatory resource (early productivity, later retreat) without independent measurement of each child's vocabulary.
3. **Input vs child production; which items count toward N**. B1 counts verbs attested in the past tense in input; B4-B6 count all verb stems the child produced.
4. **What counts as an exception**. Semantic opacity for -ness/-ment/-age/-ity (Yang calls these judgments "subtle" [V]); unattested vs counter-attested forms (Sufficiency vs Tolerance); non-application singletons in the infant studies; compounds counted or not in German.
5. **Rule formulation and recursive partitioning**. When a rule fails, the set is subdivided (gender, final schwa, syllable count, stem type, semantic class) until subsets pass. Failure at one level is absorbed by moving to another, so most "unproductive" verdicts in zone L (B27, B29, B31, B59, B62) are never tested as predictions. Belth et al. 2021 automate the partitioning, which reduces but does not remove the choice of feature space.
6. **Post hoc slack**. Misses are attributed to sampling (Adam, Eve), brevity (fly-flew), sparse data (Icelandic historical).
7. **Bookkeeping errors in the record**. Yang 2018 Table 2 row "80: 46 / 24" does not sum to 80 [V]; PoLP gives M = 52 of 92 in text and 50 in the table [V]; PoLP Table 3.1 gives theta_100 = 23 but the text uses 22 [V]; stress set is 420 words in the text and theta_402 in the calculation [V]; van Tuijl gives 317 exceptions as "708 - 309" [V]; Eve's counts differ between Yang (163/49) and Ma et al. (93/36) [V].

## 4. Schuler, Yang & Newport 2016 in detail

All numbers below are [V] from the CogSci paper unless marked.

- **Language**: 9 nonsense nouns; rule "add *ka* to make a noun plural". All sentences begin with the nonsense verb *gentif*. Singular: gentif + NOUN. Plural: gentif + NOUN + MARKER.
- **Conditions** (between subjects):
  - 5R/4E: 5 nouns take *ka*, 4 nouns are exceptions. TP: 4 <= 4.096, productive.
  - 3R/6E: 3 nouns take *ka*, 6 are exceptions. TP: 6 > 4.096, unproductive.
  - No 4R/5E condition, so the design does not straddle the threshold with adjacent integers.
- **Exception forms**: exception markers listed as "po, tay, lee bae, muy, or woo" (as printed; six markers if "lee, bae" are two). The paper does not state the noun-to-marker mapping. Hernandez et al. 2019 [V] and Yang 2016/2018 [V] both describe each exception noun as having its own idiosyncratic marker (5R/1-1-1-1E and 3R/1-1-1-1-1-1E). So in 3R/6E *ka* is still the single most frequent marker by type (3 nouns vs 1 each).
- **Exposure**: 72 sentences (24 singular, 48 plural), random order, each repeated aloud by the participant; break every 18 trials. Plural pictures show 2, 4 or 6 objects.
- **Token frequencies**: noun frequency "Zipfian", with *ka* nouns the most frequent in both conditions. The text describes each noun as half as frequent as the one before (which is geometric, not Zipfian). *ka* accounts for 75% of plural exposure sentences in 5R/4E and 58.3% in 3R/6E, i.e. 36 and 28 of 48 [calc]. Per-noun token counts: not found.
- **Test**: wug-style production, 12 trials (2 for each of 6 novel nouns), pictures of 3 or 5 objects; then a rating test of trained items.
- **Participants**: 15 children, mean 7.48 years, range 5.08-8.92; a further 3 did not finish and 4 were excluded for failing the task. Table 1 implies 7 children in 5R/4E and 8 in 3R/6E. 20 adults on Mechanical Turk; adult n per condition not found.
- **Child results**:
  - 5R/4E: *ka* on 91.7% of novel plurals; not different from 100% (one-tailed t = 1.00, p = .18); 6 of 7 children at 100%.
  - 3R/6E: *ka* on 16.9%; different from 100% (t = 6.81, p < .0001); 1 of 8 children at 100%.
  - Conditions differ (t = 4.91, p < .001).
  - Against token frequency: above 75% in 5R/4E (t = 2.00, p < .05); below 58.3% in 3R/6E (t = 3.40, p < .01).
- **Adult results**: 65.0% in 5R/4E (differs from 100%, t = 3.23, p < .01) and 51.7% in 3R/6E (t = 4.59, p < .001); conditions do not differ (t = 0.89, p = .39); both match token frequency (t = 0.92, p = .19; t = 0.63, p = .27).
- **Analysis caveat**: productivity in 5R/4E is inferred from failing to reject 100% with n = 7; the tests are one-tailed.

Does simple majority predict the same pattern?

- **Type majority** (productive iff more than half of the noun types follow the rule): 5 of 9 = 55.6% gives productive; 3 of 9 = 33.3% gives unproductive. Identical to TP. The design does not discriminate TP from type majority, nor from any fixed exception threshold between 44.4% and 66.7% [calc].
- **Token majority**: *ka* is 75% and 58.3% of plural tokens, so productive in both. Refuted by the children in 3R/6E, matched (in graded form) by adults.
- **Plurality / most frequent marker by type**: *ka* is the most frequent marker in both conditions, so productive in both. Refuted by the children in 3R/6E. This is the contrast the authors and Yang emphasise ("despite the statistical dominance of the regular suffix"); it rules out plurality and token-based accounts, not type majority.
- **Exact TP derivation**: with the harmonic number, the threshold at N = 9 is 3, so 5R/4E should be unproductive [V, Yang 2018]. Children's behaviour fits ln N and type majority, not the exact efficiency calculation.
- Goldberg's group adds that an interference account also predicts the pattern, and that 5R/4E productivity is not robust when the four exceptions share a form (A4).

Bottom line for Schuler et al.: a clean demonstration that children (unlike adults) make a near-categorical, type-based decision and ignore token dominance. It is not evidence for the N/ln N form over simple type majority.
