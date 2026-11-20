"""Build the token table for babyview_export.py from the BabyView 2026.1 transcripts.

Run on ccn2, where the protected transcripts live. Everything this writes stays in --work
(a private directory) except what babyview_export.py and the CDI step later put in --work/export.

Steps
  1. Read the merged, spaCy-parsed 2026.1 transcript (one row per spaCy token).
  2. Child = video_id prefix (S00xxxxxx); recording date = second field of video_id.
     Age in days = recording date - date_birth_rounded (demogs.csv; DOB is rounded to the
     1st or 15th, so ages are accurate to about +/- 1 week).
  3. Keep children with >= --min-words non-punctuation tokens (all speakers) AND a CDI.
  4. Assign random pseudonyms (bv01, bv02, ...); the key stays in --work/id_key.csv.
  5. Write tokens.csv for the export script, and the pseudonymised CDI files to --work/export.

Usage
  python 02_build_tokens.py --work /data2/mcfrank/tp_babyview --min-words 100000
"""

import argparse
import json
import os

import numpy as np
import pandas as pd

BV = "/ccn2a/dataset/babyview"
TRANSCRIPT = f"{BV}/2026.1/outputs/merged_transcripts_parsed.csv"
DEMOGS = f"{BV}/demogs.csv"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--min-words", type=int, default=100_000)
    ap.add_argument("--seed", type=int, default=20261120)
    a = ap.parse_args()
    out = os.path.join(a.work, "export")
    os.makedirs(out, exist_ok=True)

    cols = ["video_id", "speaker", "spacy_token_text", "spacy_token_lemma", "spacy_pos",
            "spacy_is_punct", "token_end_time"]
    t = pd.read_csv(TRANSCRIPT, usecols=cols, dtype=str)
    t = t[t.spacy_is_punct.str.lower() != "true"].copy()
    parts = t.video_id.str.split("_", expand=True)
    t["subject_id"] = parts[0]
    t["rec_date"] = pd.to_datetime(parts[1], errors="coerce")

    d = pd.read_csv(DEMOGS, encoding="utf-8-sig")
    dob = dict(zip(d.subject_id, pd.to_datetime(d.date_birth_rounded)))
    t["age_days"] = (t.rec_date - t.subject_id.map(dob)).dt.days

    cdi_items = pd.read_csv(os.path.join(a.work, "cdi_items_raw.csv"), dtype={"value": str})
    cdi_admins = pd.read_csv(os.path.join(a.work, "cdi_admins_raw.csv"))
    t["subject_num"] = t.subject_id.str.lstrip("S").astype(int)

    per = t.groupby("subject_num").agg(n_words_all=("speaker", "size"),
                                       n_words_kchi=("speaker", lambda s: (s == "KCHI").sum()),
                                       n_videos=("video_id", "nunique"),
                                       age_na=("age_days", lambda s: s.isna().mean()))
    per["has_cdi"] = per.index.isin(cdi_admins.subject_num)
    keep = per[(per.n_words_all >= a.min_words) & per.has_cdi].index

    rng = np.random.default_rng(a.seed)
    order = rng.permutation(sorted(keep))
    key = pd.DataFrame({"subject_num": order,
                        "child_id": [f"bv{i + 1:02d}" for i in range(len(order))]})
    key.to_csv(os.path.join(a.work, "id_key.csv"), index=False)
    m = dict(zip(key.subject_num, key.child_id))

    # recording hours per child-month: sum over videos of last token end time (a lower bound
    # on recording length, since silence after the last word is not counted)
    tk = t[t.subject_num.isin(keep) & t.age_days.notna()].copy()
    tk["child_id"] = tk.subject_num.map(m)
    tk["age_days"] = tk.age_days.astype(int)
    tk["age_month"] = (tk.age_days / 30.44).astype(int)
    hrs = (tk.assign(end=pd.to_numeric(tk.token_end_time, errors="coerce"))
           .groupby(["child_id", "age_month", "video_id"]).end.max()
           .groupby(["child_id", "age_month"]).sum() / 3600).rename("hours_lb").reset_index()
    hrs.to_csv(os.path.join(a.work, "hours.csv"), index=False)

    tk[["child_id", "age_days", "speaker", "spacy_token_text", "spacy_token_lemma", "spacy_pos",
        "video_id"]].to_csv(os.path.join(a.work, "tokens.csv"), index=False)

    ci = cdi_items[cdi_items.subject_num.isin(keep)].copy()
    ci.insert(0, "child_id", ci.subject_num.map(m))
    ci.drop(columns="subject_num").to_csv(os.path.join(out, "cdi_items.csv"), index=False)
    ca = cdi_admins[cdi_admins.subject_num.isin(keep)].copy()
    ca.insert(0, "child_id", ca.subject_num.map(m))
    ca.drop(columns="subject_num").to_csv(os.path.join(out, "cdi_admins.csv"), index=False)

    # child-level summary (pseudonymised) for the analysis session
    s = per.loc[keep].reset_index()
    s.insert(0, "child_id", s.subject_num.map(m))
    s = s.drop(columns=["subject_num", "has_cdi", "age_na"]).sort_values("child_id")
    s.to_csv(os.path.join(out, "child_summary.csv"), index=False)

    summary = dict(
        n_children_transcripts=int(len(per)),
        n_children_with_cdi=int(per.has_cdi.sum()),
        n_children_ge_min_words=int((per.n_words_all >= a.min_words).sum()),
        n_children_selected=int(len(keep)),
        min_words=a.min_words,
        frac_tokens_missing_age=float(t.age_days.isna().mean()),
        words_all_quantiles=per.n_words_all.quantile([0, .25, .5, .75, 1]).round().tolist(),
        cdi_children_below_threshold_words=sorted(per[per.has_cdi & (per.n_words_all < a.min_words)]
                                                  .n_words_all.astype(int).tolist()),
    )
    json.dump(summary, open(os.path.join(a.work, "build_summary.json"), "w"), indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
