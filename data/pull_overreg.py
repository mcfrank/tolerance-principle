"""Candidate past-tense overregularisations by target children (Eng-NA, Eng-UK).
Pulls every child token ending in -ed that either has a transcriber replacement
or is lemmatised to an irregular verb; classification happens locally."""
import sys
import redivis
sys.path.insert(0, "data")
from tail_model import IRREGULAR

ds = redivis.organization("datapages").dataset("childes-db")
irr = ", ".join(f"'{v}'" for v in sorted(IRREGULAR))
SQL = f"""
SELECT target_child_id, CAST(FLOOR(target_child_age / 30.44) AS INT64) AS month,
       LOWER(gloss) AS gloss, LOWER(stem) AS stem, LOWER(replacement) AS replacement,
       part_of_speech, COUNT(*) AS n
FROM token
WHERE collection_name IN ('Eng-NA','Eng-UK') AND language = 'eng' AND speaker_role = 'Target_Child'
  AND target_child_age BETWEEN 365 AND 1826 AND LOWER(gloss) LIKE '%ed'
  AND ((replacement IS NOT NULL AND replacement != '') OR LOWER(stem) IN ({irr}))
GROUP BY 1,2,3,4,5,6
"""
if __name__ == "__main__":
    d = ds.query(SQL).to_pandas_dataframe(progress=False)
    d.to_csv("data/overreg_candidates.csv", index=False)
    print(len(d), "rows;", d.n.sum(), "tokens;", d.target_child_id.nunique(), "children")
    g = d.groupby(["gloss", "stem", "replacement"], dropna=False).n.sum().sort_values(ascending=False)
    print(g.head(70).to_string())
