from functools import lru_cache
from itertools import islice


@lru_cache()
def locations():
    # todo import directly from google? not sure
    from my.location import iter_locations
    # todo islice something earlier?
    return list(iter_locations())


@lru_cache()
def locations_dataframe(limit=None):
    import pandas as pd # type: ignore
    locs = locations()
    idf = pd.DataFrame(islice((l._asdict() for l in locs), 0, limit))
    df = idf.set_index('dt')
    return df
