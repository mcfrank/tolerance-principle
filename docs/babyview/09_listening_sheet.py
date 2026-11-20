"""Build a stratified listening sheet so a human coder can validate the BabAR-based filters.

Run on ccn2 after 07/08 (needs word_scores.csv, token_flags.csv, irreg_scores.csv). Clips and
sheets contain protected audio and transcript words: they stay in --out on ccn2.

Strata (KCHI tokens unless noted):
  A_lt14_pass   <14 mo, child voice & no adult overlap & support >= 0.9   (the puzzle)
  B_lt14_fail   <14 mo, child voice & support < 0.5                       (should be invented)
  C_26_pass     26+ mo, child voice & no adult overlap & support >= 0.9
  D_26_fail     26+ mo, child voice & support < 0.5
  E_26_irreg    26+ mo irregular-verb tokens: half the most "overregularised-sounding"
                (regularised minus irregular log-lik), half random
  F_fem         FEM tokens with support >= 0.9 (coder sanity check: should be adult, match)

Outputs in --out:
  clips/<clip_id>.wav   target word with --ctx s of context on each side
  sheet.csv             coder-facing: clip_id, file, target window within clip, ASR word,
                        empty coding columns; shuffled; no stratum, age or scores
  key.csv               clip_id -> stratum, token, scores (do not show coders)
"""

import argparse
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--ctx", type=float, default=1.5)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--double", type=float, default=0.2, help="share of clips to double-code")
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)

    s = pd.read_csv(a.work / "word_scores.csv", keep_default_na=False, na_values=[""])
    s = s[s.support.notna()].merge(pd.read_csv(a.work / "token_flags.csv"), on="tok_id", how="left")
    for c in ["vtc_kchi", "heard", "adult_overlap"]:
        s[c] = s[c].fillna(False).astype(bool)
    k = s[s.speaker == "KCHI"]
    child = k.vtc_kchi & k.heard
    lt, old = k.band == "<14", k.band == "26+"

    def take(df, n, name):
        df = df.sample(min(n, len(df)), random_state=int(rng.integers(1e9)))
        return df.assign(stratum=name)

    ir = pd.read_csv(a.work / "irreg_scores.csv")
    piv = ir.pivot_table(index="tok_id", columns="kind", values="ll", aggfunc="max")
    piv["d_overreg"] = piv.get("overreg") - piv.get("irregular")
    e = k[old & k.tok_id.isin(piv.index)].merge(piv[["d_overreg"]], left_on="tok_id", right_index=True)
    e_top = e.dropna(subset=["d_overreg"]).nlargest(30, "d_overreg").assign(stratum="E_26_irreg_top")
    e_rand = take(e[~e.tok_id.isin(e_top.tok_id)], 30, "E_26_irreg_rand")

    picks = [take(k[lt & child & ~k.adult_overlap & (k.support >= 0.9)], 60, "A_lt14_pass"),
             take(k[lt & child & (k.support < 0.5)], 30, "B_lt14_fail"),
             take(k[old & child & ~k.adult_overlap & (k.support >= 0.9)], 50, "C_26_pass"),
             take(k[old & child & (k.support < 0.5)], 30, "D_26_fail"),
             e_top, e_rand,
             take(s[(s.speaker == "FEM") & (s.support >= 0.9)], 20, "F_fem")]
    p = pd.concat(picks, ignore_index=True).drop_duplicates("tok_id")
    p = p.sample(frac=1, random_state=a.seed).reset_index(drop=True)
    p["clip_id"] = [f"c{i:03d}" for i in range(1, len(p) + 1)]

    (a.out / "clips").mkdir(parents=True, exist_ok=True)
    p["clip_start"] = (p.token_start_time - a.ctx).clip(lower=0)
    p["clip_end"] = p.token_end_time + a.ctx
    for r in p.itertuples():
        subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y",
                        "-ss", f"{r.clip_start:.3f}", "-to", f"{r.clip_end:.3f}",
                        "-i", str(a.work / "wav" / f"{r.video_id}.wav"),
                        str(a.out / "clips" / f"{r.clip_id}.wav")], check=True)

    sheet = pd.DataFrame({
        "clip_id": p.clip_id,
        "file": "clips/" + p.clip_id + ".wav",
        "target_start_s": (p.token_start_time - p.clip_start).round(2),
        "target_end_s": (p.token_end_time - p.clip_start).round(2),
        "double_code": rng.random(len(p)) < a.double,
        "speaker": "", "speech_type": "",          # code these BEFORE reading asr_word
        "asr_word": p.word, "word_match": "", "irregular_form": "", "what_said": "",
        "coder": "", "notes": ""})
    sheet.to_csv(a.out / "sheet.csv", index=False)
    key = p[["clip_id", "stratum", "video_id", "tok_id", "band", "speaker", "word", "lemma", "verb",
             "support", "vtc_kchi", "heard", "adult_overlap", "token_start_time", "token_end_time"]]
    key = key.merge(e[["tok_id", "d_overreg"]], on="tok_id", how="left")
    key.to_csv(a.out / "key.csv", index=False)
    print(key.stratum.value_counts().sort_index().to_string())
    print("clips:", len(p), " double-coded:", int(sheet.double_code.sum()))


if __name__ == "__main__":
    main()
