"""Small helper for querying the Wordbank dataset on Redivis.
Needs REDIVIS_API_TOKEN in the environment."""
import redivis

DATASET = ("datapages", "wordbank:627v")


def query(sql):
    ds = redivis.organization(DATASET[0]).dataset(DATASET[1])
    return ds.query(sql).to_pandas_dataframe(progress=False)
