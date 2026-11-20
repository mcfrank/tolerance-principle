# Handoff: paired CDI and verb-count data from BabyView

This note is for a session that has access to the protected BabyView
transcripts. The goal is to send the analysis session **aggregate verb counts
and CDI responses only**, so that no transcript text leaves the protected
server.

## Why we need this

We are testing Yang's Tolerance Principle (a rule over N items is productive
when its exceptions number at most N / ln N) against children's acquisition of
the English past tense. The test needs, for each child, the number of verbs
known (N) and the number of irregular verbs known (e) around the time they
start overregularising ("goed", "falled").

Transcripts alone cannot give N. In CHILDES, the number of distinct verbs seen
in a fixed 1,000 verb tokens is about 115 at every age from 18 to 42 months,
so raw counts measure how much speech was recorded, not vocabulary. Verbs
learned later are too rare to show up reliably.

Children with **both** a CDI and recordings fix this. For the 103 verbs on the
CDI checklist, the parent tells us whether the child knows each one,
independent of sampling. We can then measure how often a known verb actually
appears in m recorded tokens, and use that to correct the counts for verbs
that are not on the checklist. See `sims/paired_calibration.py`.

## What to send

Six files. Use the same de-identified `child_id` in all of them.

### From the transcripts (produced by the export script)

| File | Columns | Contents |
|---|---|---|
| `child_verb_counts.csv` | `child_id, age_month, lemma, n` | Target child's verb tokens, by verb lemma and month of age |
| `child_verb_forms.csv` | `child_id, age_month, form, lemma, n` | Surface forms of irregular verbs only: correct forms (went, fell) and overregularisations (goed, falled) |
| `child_totals.csv` | `child_id, age_month, n_tokens_all, n_verb_tokens, n_verb_tokens_whitelist, n_recordings` | Sample size per child-month |
| `input_verb_counts.csv` | `child_id, lemma, n` | Verb tokens from everyone else in the recordings (optional but useful) |
| `manifest.json` | | How the export was made |

`age_month` is `floor(age_in_days / 30.44)`.

### From the CDI records (prepared by hand; format below)

`cdi_items.csv`, one row per child, administration and item:

| Column | Meaning |
|---|---|
| `child_id` | Same ID as above |
| `age_month` | Child's age at this administration |
| `form` | `WS`, `WG`, or the short-form name |
| `item_kind` | Wordbank naming if possible: `word`, `word_forms_verbs`, `word_endings_verbs`, `word_endings` |
| `category` | For `word` items, the CDI section (we need `action_words`; sending all words is fine) |
| `item_definition` | The item as printed, e.g. `go`, `went`, `goed`, `ed` |
| `value` | The response: `produces` / blank, or `not yet` / `sometimes` / `often` |

Essential: the action-word (verb) checklist. Valuable: the irregular verb
forms (`word_forms_verbs`), the overregularised verb forms
(`word_endings_verbs`) and the `ed` word-ending question, which give onset of
overregularisation by parent report. Also send total production score per
administration if it is to hand (`cdi_admins.csv`: `child_id, age_month, form,
production`).

Recording duration per child-month (`hours`) is welcome as an extra column in
`child_totals.csv` if it is easy to add.

## How to produce the transcript files

Run `docs/babyview_export.py` on the protected server. It needs a token-level
table (CSV or parquet), one row per word, with at least child ID, child age in
days, speaker, and the word. Lemma and part of speech are strongly preferred.

```
python docs/babyview_export.py tokens.parquet --out export/ \
    --child child_id --age-days age_days \
    --speaker speaker --target-child-value CHI \
    --word word --lemma lemma --pos upos --recording recording_id
```

It needs three public reference files that sit beside it in `docs/`:

- `verb_lexicon.csv`: the 1,653 verb lemmas we count, with input frequency
  from CHILDES, an irregular flag and a CDI-checklist flag.
- `verb_form_lemma.csv`: surface form to lemma, from CHILDES, used when the
  tokens have no lemma.
- `overreg_forms.csv`: overregularised forms attested in CHILDES.

Notes on running it:

- **Part of speech matters.** Our CHILDES counts use childes-db's tags
  (`verb` and `aux`). If the BabyView tokens have a UD-style tag, pass it with
  `--pos`; `VERB` and `AUX` are both counted. Without it the script falls back
  to matching surface forms, which over-counts words like "play" and "drink"
  that are also nouns. The manifest records which mode was used.
- **Speaker labels.** `--target-child-value` is whatever marks the target
  child in the speaker column. If speaker attribution is automatic and
  uncertain, say so; child counts are only as good as the diarisation.
- **Age.** If only recording dates are available, compute age in days from
  date of birth on the protected side.
- The script was tested on a small synthetic table, not on real BabyView data.
  Check the manifest totals against what you expect.

## Privacy properties of the export

- Only lemmas in `verb_lexicon.csv` are written. A name, place or any other
  word outside that list is dropped even if a tagger calls it a verb.
- Surface forms are written only for irregular verbs, and only if the form is
  a known verb form or a known or rule-generated overregularisation.
- Nothing is written at the level of an utterance, a recording or a date:
  the finest grain is child by month of age.
- The CDI file is item-level by design. If month of age together with other
  fields could identify a child in your setting, coarsen or drop fields before
  sending and tell us what changed.

Whether these aggregates may leave the protected server at all, and by what
route, is for the data owner to decide. Do **not** commit them to this
repository unless the owner says so: `data/babyview/` is git-ignored for that
reason, and the analysis scripts will look for the files there.

## What would be informative

- Even 5 to 10 children with a CDI within about two months of at least 2,000
  recorded verb tokens gives a first look at the real detection curve.
- Children with a CDI Words & Sentences form between 18 and 36 months are the
  most useful, because the verb checklist is not at ceiling and
  overregularisation typically starts in that range.
- More children matters more than more hours per child, once a child has a few
  thousand verb tokens.

## State of the project (for orientation)

Branch `claude/yang-tolerance-principle-kwewwv`.

| Path | What it is |
|---|---|
| `sims/tp_checks.py` | Yang's cost equation solved exactly; effect of frequent exceptions |
| `sims/learnability.py`, `sims/bayes_rule.py`, `sims/fragment.py`, `sims/mdl.py` | Candidate derivations of the principle. Summary: N / ln N appears only when each exception carries a fixed, unshared cost of about ln N |
| `notes/tp_evidence.md` | Compiled empirical record for the principle |
| `notes/vocab_estimators.md` | Notes on Hidaka's type-token estimator and alternatives |
| `data/wb.py`, `data/pull_*.py` | Pulls from Wordbank and childes-db on Redivis (needs `REDIVIS_API_TOKEN`) |
| `data/first_look.py`, `data/tail_model.py` | English Wordbank: checklist counts and a frequency-based tail model (not constraining) |
| `data/norwegian_look.py` | Norwegian Wordbank: longitudinal onset; children overregularise with a minority suffix |
| `data/estimators.py`, `data/zip_irt.py` | Transcript-only estimators of verb vocabulary. Stable under thinning but do not track growth; not valid for N |
| `data/composition.py` | Shows type counts and their make-up are flat with age at fixed sample size |
| `data/onset.py` | First overregularisation per child in CHILDES; depends on the estimator above, so verdicts are not yet trustworthy |
| `sims/paired_calibration.py` | The estimator the BabyView data is for, tested on simulated data |

Derived data files (`data/*.csv`) are not committed; rerun the pull scripts to
regenerate them.
