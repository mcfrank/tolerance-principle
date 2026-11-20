# The book

A Quarto book that writes up the theoretical side of the project: Yang's derivation of the
Tolerance Principle and the rational analyses that do and do not reproduce it. Every table
and figure is computed in the chapters from the code in `../sims/`.

Render one chapter or the whole book:

```
./render.sh 01-derivation.qmd
./render.sh
```

The rendered site goes to `_book/` (not committed). `_freeze/` holds cached cell outputs and
is committed, so unchanged chapters are not re-run. If the code in `../sims/` changes but a
chapter's source does not, delete that chapter's folder under `_freeze/` to force a re-run.

The book has not been published. It contains no participant data; the corpus and BabyView
analyses live in `../data/` and are not part of it.
