"""Turn protected transcripts into aggregate verb counts that are safe to share.

Run this where the transcripts live. It reads a token-level table and writes
only counts of verbs from a fixed public whitelist (docs/verb_lexicon.csv),
per child and month of age. No utterances, no free text, and no word outside
the whitelist or the list of known overregularised forms ever leaves.

Input: a CSV or parquet file with one row per word token. Column names are
set with the flags below. Required: child id, child age in days, speaker,
word. Optional: lemma and part of speech (strongly preferred), recording id.

Example
    python docs/babyview_export.py tokens.parquet --out export/ \
        --child child_id --age-days age_days --speaker speaker --target-child-value CHI \
        --word word --lemma lemma --pos upos --recording recording_id

Output files (all CSV) in --out:
    child_verb_counts.csv   child_id, age_month, lemma, n
    child_verb_forms.csv    child_id, age_month, form, lemma, n   (irregular verbs and -ed errors only)
    child_totals.csv        child_id, age_month, n_tokens_all, n_verb_tokens, n_verb_tokens_whitelist, n_recordings
    input_verb_counts.csv   child_id, lemma, n                    (everyone except the target child)
    manifest.json           how the export was made
"""

import argparse
import json
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
VERB_POS = {"verb", "aux", "VERB", "AUX", "v", "V"}
BLOCK = set("bed seed need weed feed shed wed lied fed led bled bred fled sped".split())


def read(path):
    return pd.read_parquet(path) if path.endswith(".parquet") else pd.read_csv(path)


def overreg_candidates(irregular_lemmas):
    """Regular-rule past forms of irregular verbs: goed, runned, buyed, maked ..."""
    out = {}
    for s in irregular_lemmas:
        forms = {s + "ed"}
        if s.endswith("e"):
            forms.add(s + "d")
        if s.endswith("y"):
            forms.add(s[:-1] + "ied")
        if len(s) > 2 and s[-1] not in "aeiouwy" and s[-2] in "aeiou":
            forms.add(s + s[-1] + "ed")
        for f in forms:
            out[f] = s
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tokens")
    ap.add_argument("--out", required=True)
    ap.add_argument("--child", default="child_id")
    ap.add_argument("--age-days", default="age_days")
    ap.add_argument("--speaker", default="speaker")
    ap.add_argument("--target-child-value", default="CHI")
    ap.add_argument("--word", default="word")
    ap.add_argument("--lemma", default=None)
    ap.add_argument("--pos", default=None)
    ap.add_argument("--recording", default=None)
    a = ap.parse_args()

    lex = pd.read_csv(os.path.join(HERE, "verb_lexicon.csv"))
    fmap = pd.read_csv(os.path.join(HERE, "verb_form_lemma.csv")).sort_values("n", ascending=False)
    fmap = fmap.drop_duplicates("form").set_index("form").lemma
    over = pd.read_csv(os.path.join(HERE, "overreg_forms.csv")).sort_values("n_childes", ascending=False)
    over = over.drop_duplicates("form").set_index("form").lemma.to_dict()
    whitelist = set(lex.lemma)
    irregular = set(lex.lemma[lex.irregular == 1])
    # Attested child errors (from CHILDES) always count as errors. Generated candidates
    # count only if they are not also a real word form.
    real = (set(fmap.index) - set(over)) | BLOCK
    generated = {f: l for f, l in overreg_candidates(irregular).items() if f not in real}
    over = {**generated, **over}
    fmap = fmap[~fmap.index.isin(over)]
    legit = set(fmap.index)                      # real verb forms

    t = read(a.tokens)
    t = t[t[a.age_days].notna() & t[a.word].notna()].copy()
    t["child_id"] = t[a.child]
    t["age_month"] = (t[a.age_days] / 30.44).astype(int)
    t["form"] = t[a.word].astype(str).str.lower().str.strip()
    t["is_child"] = t[a.speaker].astype(str) == a.target_child_value

    use_pos = a.lemma is not None and a.pos is not None
    if use_pos:
        t["is_verb"] = t[a.pos].isin(VERB_POS)
        t["lemma"] = t[a.lemma].astype(str).str.lower()
        # an overregularised form is a verb whatever the tagger made of it
        err = t.form.isin(over)
        t.loc[err, "lemma"] = t.loc[err, "form"].map(over)
        t.loc[err, "is_verb"] = True
    else:
        t["lemma"] = t.form.map(fmap)
        err = t.form.isin(over)
        t.loc[err, "lemma"] = t.loc[err, "form"].map(over)
        t["is_verb"] = t.lemma.notna()
    t["ok"] = t.is_verb & t.lemma.isin(whitelist)

    os.makedirs(a.out, exist_ok=True)
    ch = t[t.is_child]
    key = ["child_id", "age_month"]
    ch[ch.ok].groupby(key + ["lemma"]).size().rename("n").reset_index() \
        .to_csv(os.path.join(a.out, "child_verb_counts.csv"), index=False)

    forms = ch[ch.ok & ch.lemma.isin(irregular) & (ch.form.isin(legit) | ch.form.isin(over))]
    forms.groupby(key + ["form", "lemma"]).size().rename("n").reset_index() \
        .to_csv(os.path.join(a.out, "child_verb_forms.csv"), index=False)

    tot = ch.groupby(key).agg(n_tokens_all=("form", "size"), n_verb_tokens=("is_verb", "sum"),
                              n_verb_tokens_whitelist=("ok", "sum"))
    tot["n_recordings"] = ch.groupby(key)[a.recording].nunique() if a.recording else pd.NA
    tot.reset_index().to_csv(os.path.join(a.out, "child_totals.csv"), index=False)

    other = t[~t.is_child & t.ok]
    other.groupby(["child_id", "lemma"]).size().rename("n").reset_index() \
        .to_csv(os.path.join(a.out, "input_verb_counts.csv"), index=False)

    manifest = dict(n_children=int(ch.child_id.nunique()), n_child_tokens=int(len(ch)),
                    n_child_verb_tokens_whitelist=int(ch.ok.sum()),
                    part_of_speech_used=bool(use_pos),
                    note=("verbs identified by tagger part of speech" if use_pos else
                          "no part of speech given: verbs identified by surface form only, so "
                          "noun/verb-ambiguous words (play, drink, brush) are over-counted"))
    json.dump(manifest, open(os.path.join(a.out, "manifest.json"), "w"), indent=2)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
