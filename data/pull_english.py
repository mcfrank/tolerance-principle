"""Per-administration verb counts and overregularisation reports, English (American) WS."""
import sys
sys.path.insert(0, "data")
from wb import query

# Checklist verbs whose past tense is not stem + -ed (46 of the 103).
IRREGULAR = """bite blow break bring build buy catch cut draw drink drive eat fall feed find fit get
give go have hear hide hit hold make put read ride run say see shake sing sit sleep slide stand
sweep swim swing take tear think throw wake write""".split()

irr_sql = ", ".join(f"'{v}'" for v in IRREGULAR)
SQL = f"""
WITH r AS (
  SELECT r.data_id, i.item_kind, i.lexical_category, i.item_definition,
         r.value IN ('produces','sometimes','often','sometimes/often') AS yes, r.value
  FROM item_responses r
  JOIN items i ON i.item_id = r.item_id AND i.language = r.language AND i.form = r.form
  WHERE r.language = 'English (American)' AND r.form = 'WS'
)
SELECT a.data_id, a.child_id, a.age, a.production, a.dataset_name,
  SUM(CASE WHEN item_kind='word' AND lexical_category='verbs' AND yes THEN 1 ELSE 0 END) AS n_verbs,
  SUM(CASE WHEN item_kind='word' AND lexical_category='verbs' AND yes
            AND REGEXP_REPLACE(item_definition, r' \\(.*\\)', '') IN ({irr_sql}) THEN 1 ELSE 0 END) AS n_irreg,
  SUM(CASE WHEN item_kind='word_endings_verbs' AND yes THEN 1 ELSE 0 END) AS n_overreg,
  SUM(CASE WHEN item_kind='word_endings_verbs' THEN 1 ELSE 0 END) AS n_overreg_items,
  SUM(CASE WHEN item_kind='word_forms_verbs' AND yes THEN 1 ELSE 0 END) AS n_irreg_past,
  MAX(CASE WHEN item_kind='word_endings' AND item_definition='ed' THEN value END) AS ed
FROM r JOIN administrations a ON a.data_id = r.data_id
GROUP BY 1,2,3,4,5
"""

if __name__ == "__main__":
    d = query(SQL)
    d.to_csv("data/english_ws.csv", index=False)
    print(len(d), "administrations;", d.child_id.nunique(), "children")
    print(d.describe().T[["count", "mean", "min", "max"]])
    print(d.ed.value_counts(dropna=False))
