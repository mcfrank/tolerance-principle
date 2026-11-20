"""Norwegian WS: per-administration verb counts by past-tense class, and overregularisations by suffix.

Classes (Bokmal): W1 weak -et/-a (kaste-kastet), W2 weak -te (kjope-kjopte),
W3 weak -de/-dde (prove-provde, kle-kledde), S strong or otherwise irregular.
Classification by hand; multi-word items are classed by their verb.
"""
import sys
sys.path.insert(0, "data")
import pandas as pd
from wb import query

CLASS = {
 "W1": """jobbe danse dytte elske fange forte hate hente hoppe huske kaste klappe klatre koste kysse
          lage putte lukke mate miste passe plaske puste riste rydde slikke slutte snakke sparke stoppe
          tegne tørke vaske vente velte våkne ønske åpne""",
 "W2": """blåse bråke dele gjemme helle høre kile kjøpe kjøre klemme leke lese like male reparere røre
          skynde smake smile spille spise svømme søle tenke vise""",
 "W3": "bygge prøve kle",
 "S":  """bite bære drikke falle finne få gi gjøre gli gråte gå ha hjelpe holde følge late legge løpe ri
          rive se sette si sitte skjære skli skrive slå sove stikke stå synge ta treffe dra være ødelegge""",
}
VERB2CLASS = {v: c for c, vs in CLASS.items() for v in vs.split()}


def head(item):
    return item.replace(" (action)", "").split()[0]


if __name__ == "__main__":
    items = query("""SELECT item_id, item_kind, item_definition FROM items
                     WHERE language='Norwegian' AND form='WS'
                       AND ((item_kind='word' AND lexical_category='verbs')
                            OR item_kind IN ('word_endings_verbs','word_forms_verbs','word_endings'))""")
    verbs = items[items.item_kind == "word"].copy()
    verbs["cls"] = verbs.item_definition.map(lambda s: VERB2CLASS.get(head(s)))
    print("unclassified:", verbs[verbs.cls.isna()].item_definition.tolist())
    print(verbs.cls.value_counts().to_string())
    over = items[items.item_kind == "word_endings_verbs"].copy()
    over["suffix"] = over.item_definition.map(lambda s: "et" if s.endswith("et") else ("te" if s.endswith("te") else "de"))
    print(over.suffix.value_counts().to_string())

    resp = query("""SELECT r.data_id, r.item_id, r.value FROM item_responses r
                    JOIN items i ON i.item_id=r.item_id AND i.language=r.language AND i.form=r.form
                    WHERE r.language='Norwegian' AND r.form='WS' AND r.value IS NOT NULL
                      AND ((i.item_kind='word' AND i.lexical_category='verbs')
                           OR i.item_kind IN ('word_endings_verbs','word_forms_verbs','word_endings'))""")
    print(resp.value.value_counts().head(8).to_string())
    resp = resp[resp.value.isin(["produces", "sometimes", "often", "sometimes/often"])]
    resp = resp.merge(items, on="item_id")
    resp = resp.merge(verbs[["item_id", "cls"]], on="item_id", how="left").merge(over[["item_id", "suffix"]], on="item_id", how="left")
    resp["key"] = resp.cls.fillna("") + resp.suffix.map(lambda s: f"over_{s}" if isinstance(s, str) else "")
    resp.loc[resp.item_kind == "word_forms_verbs", "key"] = "strong_past"
    resp.loc[resp.item_kind == "word_endings", "key"] = "ending_q"
    wide = resp[resp.key != "ending_q"].pivot_table(index="data_id", columns="key", values="item_id", aggfunc="count", fill_value=0)
    adm = query("""SELECT data_id, child_id, age, production, dataset_name FROM administrations
                   WHERE language='Norwegian' AND form='WS'""")
    d = adm.merge(wide, on="data_id", how="left").fillna(0)
    d.to_csv("data/norwegian_ws.csv", index=False)
    print(len(d), "administrations;", d.child_id.nunique(), "children")
    print(d.drop(columns=["data_id", "child_id"]).describe().T[["mean", "max"]].round(1).to_string())
