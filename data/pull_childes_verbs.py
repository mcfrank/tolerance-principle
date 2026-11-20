"""Verb lemma frequencies in North American English CHILDES (children up to 48 months):
tokens addressed to the child (all non-child speakers) and tokens produced by the child."""
import redivis

SQL = """
SELECT LOWER(stem) AS stem, part_of_speech,
       SUM(CASE WHEN speaker_role != 'Target_Child' THEN 1 ELSE 0 END) AS n_input,
       SUM(CASE WHEN speaker_role  = 'Target_Child' THEN 1 ELSE 0 END) AS n_child,
       COUNT(DISTINCT CASE WHEN speaker_role = 'Target_Child' THEN target_child_id END) AS n_children
FROM token
WHERE collection_name = 'Eng-NA' AND language = 'eng' AND target_child_age < 1461
  AND stem IS NOT NULL AND stem != ''
  AND part_of_speech IN ('verb', 'aux')
GROUP BY 1, 2
"""

if __name__ == "__main__":
    ds = redivis.organization("datapages").dataset("childes-db")
    d = ds.query(SQL).to_pandas_dataframe(progress=False)
    d.to_csv("data/childes_verbs_raw.csv", index=False)
    print(len(d), "rows")
    print(d.groupby("part_of_speech")[["n_input", "n_child"]].sum().sort_values("n_input", ascending=False).head(15))
    v = d[d.part_of_speech == "verb"].sort_values("n_input", ascending=False)
    print(v.head(40).to_string())
    print((v.n_input >= 5).sum(), "verb stems with >= 5 input tokens;", (v.n_input >= 1).sum(), "with >= 1")
