# BabyView export: how it was made

*Scripts and this note drafted with Claude Opus 5.5; not yet reviewed by a human.*

This answers `docs/HANDOFF.md`. The protected transcripts stayed on ccn2; only the
files below were produced from them. They live in `data/babyview/` (git-ignored).

## Pipeline

1. `01_cdi_items.R` (run locally on the webCDI exports, `data_june_2026`): wide
   exports → long item file. Keeps subject number, age, form and item responses
   only. Background/demographic columns and free-text sentence examples are dropped.
2. `02_build_tokens.py` (ccn2): reads the BabyView **2026.1**
   `merged_transcripts_parsed.csv` (spaCy tokens, punctuation dropped), takes the child
   from the `video_id` prefix and the recording date from its second field, and computes age
   from `demogs.csv` `date_birth_rounded`. Keeps children with **≥ 100,000 words (all
   speakers)** who also have a CDI, assigns random pseudonyms (`bv01`…; the key stays on
   ccn2), and writes the token table and pseudonymised CDI files.
3. `docs/babyview_export.py` (unchanged), run with
   `--speaker speaker --target-child-value KCHI --word spacy_token_text
   --lemma spacy_token_lemma --pos spacy_pos --recording video_id`.
4. Recording hours (`hours_lb`) were added to `child_totals.csv`, and children without
   transcript ages were removed from the CDI files.

## What came out

- 51 children have 2026.1 transcripts, 33 have a CDI, and 24 have both a CDI and at least
  100k words. One of the 24 (`bv13`) has no birth date in `demogs.csv`, so their
  transcripts can't be given ages. They were dropped, leaving **23 children**.
- 124 CDI administrations: 51 WG at 9–16 months and 73 WS at 17–32 months. 34 of them
  have at least 2,000 target-child verb tokens within ±2 months.
- 902k target-child tokens, of which 168k are whitelisted verb tokens. `hours_lb` totals
  about 2,128 h.
- Disclosure check: every lemma is in `verb_lexicon.csv`. Every surface form is in
  `verb_form_lemma.csv` or `overreg_forms.csv`, except one rule-generated form (`casted`).

## Caveats

- **Speaker labels are automatic diarisation.** `KCHI` (key child) vs `OCH` (other child)
  vs `FEM`/`MAL` is model output, so child counts include attribution errors. About 13% of
  all tokens are `unknown`; they count as "input" (not the target child) in
  `input_verb_counts.csv`.
- **ASR, not hand transcription.** Child speech, especially at young ages, is
  under-recognised and sometimes normalised toward adult forms. That could suppress
  overregularisations like *goed*.
- **Age** is accurate to about ±1 week, because DOB is rounded to the 1st or 15th.
  `age_month = floor(age_days / 30.44)`. CDI `age_month` is the webCDI age at
  administration.
- `hours_lb` sums each recording's last-word end time, so it is a lower bound on
  recorded time.
- `n_tokens_all` in `child_totals.csv` counts target-child tokens only, as the export
  script defines it. `child_summary.csv` gives all-speaker and `KCHI` word totals per
  child.
- CDI `value`: `produces` / `understands` (WG) / blank for checklist items;
  `not yet` / `sometimes` / `often` for the `word_endings` questions. Only
  completed English administrations are included.
