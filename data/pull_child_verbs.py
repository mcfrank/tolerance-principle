"""English CHILDES (Eng-NA and Eng-UK), ages 18-48 months:
  child_verb_counts.csv  verb lemma counts per target child per month of age
  input_verb_counts.csv  verb lemma counts in speech by everyone else, per collection
  childes_density.csv    child token totals per target child
"""
import redivis

ds = redivis.organization("datapages").dataset("childes-db")
q = lambda s: ds.query(s).to_pandas_dataframe(progress=False)
BASE = """FROM token WHERE collection_name IN ('Eng-NA','Eng-UK') AND language = 'eng'
          AND target_child_age BETWEEN 548 AND 1461 AND stem IS NOT NULL AND stem != ''
          AND part_of_speech IN ('verb','aux')"""

if __name__ == "__main__":
    c = q(f"""SELECT target_child_id, CAST(FLOOR(target_child_age / 30.44) AS INT64) AS month,
                     LOWER(stem) AS stem, COUNT(*) AS n {BASE} AND speaker_role = 'Target_Child'
              GROUP BY 1, 2, 3""")
    c.to_csv("data/child_verb_counts.csv", index=False)
    print(len(c), "child rows;", c.target_child_id.nunique(), "children;", c.n.sum(), "verb tokens")
    i = q(f"""SELECT collection_name, LOWER(stem) AS stem, COUNT(*) AS n {BASE}
              AND speaker_role != 'Target_Child' GROUP BY 1, 2""")
    i.to_csv("data/input_verb_counts.csv", index=False)
    print(len(i), "input rows;", i.n.sum(), "verb tokens")
    d = q("""SELECT t.collection_name, c.name AS corpus, t.target_child_id, t.target_child_name,
                    SUM(t.num_tokens) AS tokens_18_42mo, ROUND(MIN(t.target_child_age)/30.44,1) AS age_min,
                    ROUND(MAX(t.target_child_age)/30.44,1) AS age_max
             FROM transcript_by_speaker t JOIN corpus c ON c.id = t.corpus_id
             WHERE t.speaker_role='Target_Child' AND t.collection_name IN ('Eng-NA','Eng-UK')
               AND t.target_child_age BETWEEN 548 AND 1280 GROUP BY 1,2,3,4""")
    d.to_csv("data/childes_density.csv", index=False)
    print(len(d), "children in density table")
