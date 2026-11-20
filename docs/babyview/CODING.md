# BabyView listening check: coder instructions

*Drafted with Claude Opus 5.5; not yet reviewed by a human.*

You will hear short clips from BabyView home recordings, made by a camera worn by a young
child (the **target child**). Each clip is about 3 s long: a target word with 1.5 s of
context on either side. The sheet gives the target window as `target_start_s` /
`target_end_s` within the clip. Listen as many times as you need.

**Data rules:** BabyView audio is restricted. The clips and the sheet live on ccn2
(`/data2/mcfrank/tp_babyview/listening/`) and in the Stanford Google Drive folder
`babyview-babar-check`. Work from there. Don't copy them anywhere else, don't upload them
to any other service (including AI tools), and don't play them to anyone without BabyView
access. If you unzip the clips on your computer, delete them when you're done.

**On Drive:** the clips are in four zips (`clips_part1of3`, `clips_part2a_of3`, `clips_part2b_of3`,
`clips_part3of3`). Unzipped into one place, they give a `clips/` folder with `c001.wav` to
`c249.wav`, matching the sheet's `file` column. Code in the `coding_sheet` Google Sheet.

## For each row of the sheet (`coding_sheet` on Drive, `sheet.csv` on ccn2)

Code `speaker` and `speech_type` **before** you look at `asr_word`.

1. **`speaker`**: who is talking during the target window?
   - `CHI` target child (closest, loudest voice, usually)
   - `ADULT_F` / `ADULT_M` adult woman / man
   - `OTHER_CHILD` a different child
   - `OVERLAP_CHI_ADULT` target child and an adult at the same time
   - `MEDIA` TV, phone, toy, music
   - `NONE` no speech (noise, crying, laughing, breathing)
   - `UNCLEAR`
2. **`speech_type`** (only if speaker includes the target child):
   - `WORD` a recognisable word or words
   - `BABBLE` speech-like syllables, no recognisable word
   - `VOCAL` cry, laugh, squeal, grunt
   - `UNCLEAR`
3. Now read **`asr_word`** (what the automatic transcript says was said in the window).
   - **`word_match`**: `MATCH` (that word was said), `PARTIAL` (close, e.g. child form
     "dat" for "that"), `NO_MATCH`, or `UNCLEAR`. Judge whoever spoke, child or adult.
4. **`irregular_form`**: fill only if you hear, or the ASR word is, a form of an irregular
   verb (go, fall, eat, run, break, ...). Use `IRREG_PAST` (went, fell), `REGULARISED`
   (goed, falled, eated), `STEM` (go, fall), `OTHER` (going, goes, gone), or `UNCLEAR`.
5. **`what_said`** (optional): your best transcription of the target window, if it differs
   from `asr_word`.
6. Put your initials in **`coder`**. Rows with `double_code = TRUE` are coded
   independently by a second coder, who works in a separate copy of the sheet.

Expect about 250 clips, roughly 1.5–2 hours. A few clips are longer, up to about 17 s, when
the transcript's word timing is wide; code the target window only.
