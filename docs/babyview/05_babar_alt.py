"""Run BabAR on segments other than VTC 2.0's own KCHI segments.

Run on ccn2 with BabAR's venv, after src/pipeline.py has written <work>/vtc2/rttm/.
Two extra passes over the same wavs:
  orig   the existing transcript's KCHI stretches (consecutive KCHI tokens within one
         utterance -> one segment), to test the labels our verb counts came from
  adult  VTC 2.0's FEM and MAL segments, as a control: BabAR is meant to output nothing
         for adult speech
Both are written as RTTMs whose target label is KCHI (BabAR's speaker filter), then
transcribed with BabAR's run_single. Output: <work>/babar_{orig,adult}/<video_id>.csv.
Segment provenance is kept in <work>/rttm_{orig,adult}/.

Usage (from the BabAR repo root):
  .venv/bin/python <this> --work /data2/mcfrank/tp_babyview/pilot --babar /data2/mcfrank/BabAR
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

TRANSCRIPT = "/ccn2b/dataset/babyview/2026.1/outputs/merged_transcripts_parsed.csv"


def rttm_line(vid, onset, dur, label="KCHI"):
    return f"SPEAKER {vid} 1 {onset:.3f} {dur:.3f} <NA> <NA> {label} <NA> <NA>\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--babar", type=Path, required=True)
    ap.add_argument("--device", default="cuda")
    a = ap.parse_args()
    sys.path.insert(0, str(a.babar / "src"))
    from babar.infer import load_model, run_single

    vids = pd.read_csv(a.work / "list.tsv", sep="\t").video_id.tolist()
    wav = a.work / "wav"

    # orig: KCHI stretches from the existing transcript
    t = pd.read_csv(TRANSCRIPT, usecols=["video_id", "utterance_id", "token_num", "token_start_time",
                                         "token_end_time", "speaker"], dtype=str)
    t = t[t.video_id.isin(vids)].copy()
    for c in ["token_start_time", "token_end_time", "token_num"]:
        t[c] = pd.to_numeric(t[c], errors="coerce")
    t = t.dropna(subset=["token_start_time", "token_end_time"]).sort_values(
        ["video_id", "token_start_time"])
    t["is_k"] = t.speaker == "KCHI"
    # new run whenever speaker flips or utterance changes
    t["run"] = ((t.is_k != t.is_k.shift()) | (t.utterance_id != t.utterance_id.shift())
                | (t.video_id != t.video_id.shift())).cumsum()
    seg = (t[t.is_k].groupby(["video_id", "run"])
           .agg(onset=("token_start_time", "min"), offset=("token_end_time", "max"),
                n_tok=("speaker", "size")).reset_index())
    seg = seg[seg.offset > seg.onset]
    d_orig = a.work / "rttm_orig"
    d_orig.mkdir(exist_ok=True)
    seg.to_csv(a.work / "orig_segments.csv", index=False)
    for vid, g in seg.groupby("video_id"):
        with open(d_orig / f"{vid}.rttm", "w") as f:
            for r in g.itertuples():
                f.write(rttm_line(vid, r.onset, r.offset - r.onset))

    # adult: VTC 2.0 FEM/MAL segments relabelled as the target label
    d_adult = a.work / "rttm_adult"
    d_adult.mkdir(exist_ok=True)
    for p in sorted((a.work / "vtc2" / "rttm").glob("*.rttm")):
        with open(p) as f, open(d_adult / p.name, "w") as g:
            for line in f:
                parts = line.split()
                if len(parts) >= 8 and parts[7] in ("FEM", "MAL"):
                    g.write(rttm_line(parts[1], float(parts[3]), float(parts[4])))

    model = load_model(a.babar / "weights" / "best.ckpt",
                       a.babar / "weights" / "vocab-phoneme-tinyvox.json", device=a.device)
    model = model.to(a.device)
    if a.device != "cpu":
        model = model.half()
    for name, d in [("orig", d_orig), ("adult", d_adult)]:
        out = a.work / f"babar_{name}"
        out.mkdir(exist_ok=True)
        for p in sorted(d.glob("*.rttm")):
            if (out / f"{p.stem}.csv").exists() or p.stat().st_size == 0:
                continue
            w = wav / f"{p.stem}.wav"
            if not w.exists():
                continue
            df = run_single(model=model, audio_path=w, rttm_path=p, device=a.device,
                            batch_size=32, num_workers=4, speaker_filter=["KCHI"], max_utt_dur=30.0)
            if df is None:
                df = pd.DataFrame(columns=["filename", "onset", "offset", "speaker", "phonemes"])
            df.to_csv(out / f"{p.stem}.csv", index=False)
        print(name, "done", flush=True)


if __name__ == "__main__":
    main()
