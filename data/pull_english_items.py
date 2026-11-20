"""For English WS: how many children at each checklist verb count produce each checklist verb."""
import sys
sys.path.insert(0, "data")
from wb import query

SQL = """
WITH r AS (
  SELECT r.data_id, REGEXP_REPLACE(i.item_definition, r' \\(.*\\)', '') AS verb,
         CASE WHEN r.value = 'produces' THEN 1 ELSE 0 END AS yes
  FROM item_responses r
  JOIN items i ON i.item_id = r.item_id AND i.language = r.language AND i.form = r.form
  WHERE r.language = 'English (American)' AND r.form = 'WS'
    AND i.item_kind = 'word' AND i.lexical_category = 'verbs'
), a AS (SELECT data_id, SUM(yes) AS n_verbs FROM r GROUP BY 1)
SELECT a.n_verbs, r.verb, SUM(r.yes) AS n_yes, COUNT(*) AS n_children
FROM r JOIN a USING (data_id) GROUP BY 1, 2
"""
if __name__ == "__main__":
    d = query(SQL)
    d.to_csv("data/english_verb_items.csv", index=False)
    print(len(d), "rows;", d.verb.nunique(), "verbs")
