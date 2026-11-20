"""Hours of recording per English target child at 18-42 months, from utterance media timestamps."""
import redivis
import pandas as pd

ds = redivis.organization("datapages").dataset("childes-db")
SQL = """
WITH t AS (
  SELECT target_child_id, transcript_id, ANY_VALUE(media_unit) AS unit,
         MIN(media_start) AS t0, MAX(media_end) AS t1, COUNT(*) AS utts,
         COUNTIF(media_end IS NOT NULL) AS timed
  FROM utterance
  WHERE collection_name IN ('Eng-NA','Eng-UK') AND target_child_age BETWEEN 548 AND 1280
  GROUP BY 1, 2
)
SELECT target_child_id, COUNT(*) AS transcripts, COUNTIF(timed > 0) AS timed_transcripts,
       SUM(CASE WHEN timed > 0 THEN t1 - t0 ELSE 0 END) AS media_total,
       ANY_VALUE(unit) AS unit, SUM(utts) AS utterances
FROM t GROUP BY 1
"""
if __name__ == "__main__":
    h = ds.query(SQL).to_pandas_dataframe(progress=False)
    d = pd.read_csv("data/childes_density.csv").merge(h, on="target_child_id")
    d["hours"] = d.media_total / 3600
    d["tokens_per_hour"] = d.tokens_18_42mo / d.hours.where(d.hours > 0)
    d.to_csv("data/childes_hours.csv", index=False)
    pd.set_option("display.width", 220)
    print(d.unit.value_counts(dropna=False).to_string())
    top = d.sort_values("tokens_18_42mo", ascending=False).head(25)
    print(top[["corpus", "target_child_name", "transcripts", "timed_transcripts", "hours",
               "tokens_18_42mo", "tokens_per_hour"]].round(0).to_string(index=False))
