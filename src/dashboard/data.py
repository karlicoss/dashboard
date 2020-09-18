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
def sleep_dataframe():
    # TODO this should be done within HPI
    import my.emfit as E
    edf =  E.dataframe()

    import my.jawbone as J
    jdf =  J.dataframe()

    # TODO add back 'src'??
    import pandas as pd
    mdf = pd.concat([jdf, edf])

    return mdf


@lru_cache()
def blood_dataframe():
    import my.body.blood as B
    return B.dataframe()


# TODO figure out when I need caching and when I don't. ideally, HPI can take care of it
@lru_cache()
def weight_dataframe():
    # import my.body.weight as W
    # TODO use an overlay instead. also document how to do this?
    import my.private.weight as W # type: ignore
    return W.dataframe()


@lru_cache()
def endomondo_dataframe():
    import my.endomondo as E
    return E.dataframe()


@lru_cache()
def cardio_dataframe():
    import my.body.exercise.cardio as E
    return E.dataframe()


@lru_cache()
def cross_trainer_dataframe():
    import my.body.exercise.cross_trainer as E
    return E.dataframe()


@lru_cache
def rescuetime_dataframe():
    import my.rescuetime as R
    return R.dataframe()
