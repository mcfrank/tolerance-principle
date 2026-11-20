"""Aggregate diagnostics for key-child (KCHI) contamination in the BabyView 2026.1 transcripts.

Run on ccn2 after 02_build_tokens.py (uses its id_key.csv). Prints aggregates only.

  A. Age floor: KCHI verb rate by month of age. Verbs before ~14 months should be near zero,
     so whatever remains there is a floor on contamination + hallucination.
  B. ASR word score: does the young-age verb rate fall with a score cut?
  C. Utterance mixing: KCHI tokens inside utterances that are mostly another speaker.
  D. Speaker-cluster agreement: KCHI tokens whose speaker_id cluster is mostly adult.
  E. Utterance length of KCHI utterances by age.
  F. Audio: which of these recordings have an mp3 on ccn2.
"""

import argparse
import glob
import os

import numpy as np
import pandas as pd

BV = "/ccn2a/dataset/babyview"
pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    a = ap.parse_args()

    key = pd.read_csv(os.path.join(a.work, "id_key.csv"))
    subj = set("S" + key.subject_num.astype(str).str.zfill(8))
    lex = set(pd.read_csv(os.path.join(a.work, "verb_lexicon.csv")).lemma)

    cols = ["video_id", "utterance_id", "token_id", "token_start_time", "token_end_time", "speaker",
            "score", "speaker_id", "spacy_token_lemma", "spacy_pos", "spacy_is_punct"]
    t = pd.read_csv(f"{BV}/2026.1/outputs/merged_transcripts_parsed.csv", usecols=cols, dtype=str)
    t = t[t.spacy_is_punct.str.lower() != "true"]
    t["subject_id"] = t.video_id.str.split("_").str[0]
    t = t[t.subject_id.isin(subj)].copy()
    d = pd.read_csv(f"{BV}/demogs.csv", encoding="utf-8-sig")
    dob = dict(zip(d.subject_id, pd.to_datetime(d.date_birth_rounded)))
    t["age_month"] = ((pd.to_datetime(t.video_id.str.split("_").str[1], errors="coerce") - t.subject_id.map(dob))
                      .dt.days / 30.44)
    t = t[t.age_month.notna()].copy()
    t["age_month"] = np.floor(t.age_month).astype(int)
    t["score"] = pd.to_numeric(t.score, errors="coerce")
    t["verb"] = t.spacy_pos.isin(["VERB", "AUX"]) & t.spacy_token_lemma.str.lower().isin(lex)
    t["band"] = pd.cut(t.age_month, [0, 14, 18, 22, 26, 40], right=False,
                       labels=["<14", "14-17", "18-21", "22-25", "26+"])
    k = t[t.speaker == "KCHI"]
    print(f"tokens={len(t):,}  KCHI={len(k):,}  speakers={t.speaker.value_counts(normalize=True).round(3).to_dict()}")

    print("\nA. KCHI by age band: tokens, share of all tokens, verb rate (whitelisted verbs / KCHI tokens)")
    A = t.groupby("band", observed=True).agg(all_tok=("verb", "size"),
                                             kchi_share=("speaker", lambda s: (s == "KCHI").mean()))
    A["kchi_tok"] = k.groupby("band", observed=True).size()
    A["kchi_verb_rate"] = k.groupby("band", observed=True).verb.mean()
    A["adult_verb_rate"] = t[t.speaker.isin(["FEM", "MAL"])].groupby("band", observed=True).verb.mean()
    A["n_kids"] = t.groupby("band", observed=True).subject_id.nunique()
    print(A.round(3))

    print("\nB. ASR word score: KCHI score quantiles by band, and verb rate by score quartile")
    print(k.groupby("band", observed=True).score.describe(percentiles=[.1, .25, .5, .75, .9]).round(3))
    k = k.assign(sq=pd.qcut(k.score, 4, labels=["q1", "q2", "q3", "q4"]))
    print(k.pivot_table(index="band", columns="sq", values="verb", aggfunc="mean", observed=True).round(3))

    print("\nC. Utterance mixing: share of tokens in each utterance labelled KCHI")
    u = t.groupby(["video_id", "utterance_id"]).agg(n=("speaker", "size"),
                                                  kfrac=("speaker", lambda s: (s == "KCHI").mean()))
    print("utterances with >1 speaker label:", round(float(
        t.groupby(["video_id", "utterance_id"]).speaker.nunique().gt(1).mean()), 3))
    k = k.merge(u, left_on=["video_id", "utterance_id"], right_index=True)
    k["mixed"] = pd.cut(k.kfrac, [0, .5, .999, 1.0], labels=["minority", "majority", "pure"])
    print(k.groupby(["band", "mixed"], observed=True).agg(n=("verb", "size"), verb_rate=("verb", "mean"))
          .unstack().round(3))

    print("\nD. Cluster agreement: majority voice type of each speaker_id cluster (per video)")
    cl = t.groupby(["video_id", "speaker_id"]).speaker.agg(lambda s: s.value_counts().idxmax()).rename("cl_major")
    k = k.merge(cl, left_on=["video_id", "speaker_id"], right_index=True, how="left")
    print(k.groupby(["band", "cl_major"], observed=True).agg(n=("verb", "size"), verb_rate=("verb", "mean"))
          .unstack().round(3))

    print("\nE. KCHI utterance length (tokens) by band, pure-KCHI utterances only")
    pu = u[u.kfrac == 1].reset_index()
    pu = pu.merge(t.drop_duplicates(["video_id", "utterance_id"])[["video_id", "utterance_id", "band"]])
    print(pu.groupby("band", observed=True).n.describe(percentiles=[.5, .9]).round(2))

    print("\nF. Audio on ccn2 for these recordings")
    vids = t.video_id.unique()
    stems = {}
    for root in [f"{BV}/2026.1/mp3", f"{BV}/2025.2/mp3"]:
        stems[root] = {os.path.basename(p)[:-4].replace("_rotated", "")
                       for p in glob.glob(f"{root}/*/*.mp3")}
    base = pd.Series(vids).str.replace("_rotated", "")
    for root, s in stems.items():
        print(f"  {root}: {base.isin(s).sum()} / {len(vids)} recordings")
    print(f"  either: {(base.isin(stems[f'{BV}/2026.1/mp3']) | base.isin(stems[f'{BV}/2025.2/mp3'])).sum()}")
    tk = t.groupby("video_id").size()
    have = base.isin(set().union(*stems.values())).values
    print(f"  share of tokens in recordings with audio: {tk[vids[have]].sum() / tk.sum():.3f}")


if __name__ == "__main__":
    main()
