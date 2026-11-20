"""Pick pilot recordings for BabAR: the selected children's recordings at <14 and >=26 months.

Run on ccn2 (needs id_key.csv from 02_build_tokens.py). Writes pilot/list.tsv
(video_id, band, mp3) in --work. Up to --per-kid recordings per child per band, chosen
at random among recordings with at least --min-kchi KCHI tokens.
"""

import argparse
import os

import pandas as pd

BV = "/ccn2b/dataset/babyview/2026.1"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--per-kid", type=int, default=3)
    ap.add_argument("--min-kchi", type=int, default=20)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()

    key = pd.read_csv(os.path.join(a.work, "id_key.csv"))
    subj = set("S" + key.subject_num.astype(str).str.zfill(8))
    t = pd.read_csv(f"{BV}/outputs/merged_transcripts_parsed.csv", usecols=["video_id", "speaker"], dtype=str)
    t = t[t.video_id.str.split("_").str[0].isin(subj)]
    v = t.groupby("video_id").agg(n=("speaker", "size"), kchi=("speaker", lambda s: (s == "KCHI").sum()))
    v = v.reset_index()
    v["subject_id"] = v.video_id.str.split("_").str[0]
    d = pd.read_csv("/ccn2a/dataset/babyview/demogs.csv", encoding="utf-8-sig")
    dob = dict(zip(d.subject_id, pd.to_datetime(d.date_birth_rounded)))
    v["age_month"] = (pd.to_datetime(v.video_id.str.split("_").str[1], errors="coerce")
                      - v.subject_id.map(dob)).dt.days / 30.44
    v["mp3"] = [f"{BV}/mp3/{s}/{vid}.mp3" for s, vid in zip(v.subject_id, v.video_id)]
    v["has_mp3"] = v.mp3.map(os.path.exists)
    print(f"recordings: {len(v)}  with mp3 at expected path: {v.has_mp3.sum()} "
          f"({v.loc[v.has_mp3, 'n'].sum() / v.n.sum():.3f} of tokens)")
    v["band"] = pd.cut(v.age_month, [0, 14, 26, 99], right=False, labels=["<14", "14-25", "26+"])
    pool = v[v.has_mp3 & (v.kchi >= a.min_kchi) & v.band.isin(["<14", "26+"])]
    pick = (pool.sample(frac=1, random_state=a.seed)
            .groupby(["subject_id", "band"], observed=True).head(a.per_kid))
    print(pick.groupby("band", observed=True).agg(recs=("video_id", "size"), kids=("subject_id", "nunique"),
                                                  kchi_tok=("kchi", "sum")))
    os.makedirs(os.path.join(a.work, "pilot"), exist_ok=True)
    pick[["video_id", "band", "mp3"]].to_csv(os.path.join(a.work, "pilot", "list.tsv"), sep="\t", index=False)


if __name__ == "__main__":
    main()
