# input data for the dashboard
# ideally here we keep this file as decoupled from the presentation as possible
# so it's possible to use with any rendering framework, or even without rendering

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


# todo just use directly?
@lru_cache()
def emfit_dataframe():
    import my.emfit as emfit
    return emfit.dataframe()


@lru_cache()
def blood_dataframe():
    import my.body.blood as B
    return B.dataframe()
