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

## Publishing

The book is published at <https://mcfrank.quarto.pub/tolerance-principle/>. `_publish.yml`
records the site, so re-publishing updates the same address:

```
./render.sh
quarto publish quarto-pub --no-render --no-prompt
```

This needs a Quarto Pub token (`QUARTO_PUB_AUTH_TOKEN`, or a stored login). If the tool's
uploads fail behind a network proxy, `python3 publish_curl.py` makes the same API calls
with curl.

The address is public. The book contains no participant data: the corpus and BabyView
analyses live in `../data/` and are not part of it. Keep it that way, or get the data
owner's clearance before publishing a chapter that changes this.
