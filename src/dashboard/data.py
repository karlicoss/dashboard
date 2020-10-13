# input data for the dashboard
# ideally here we keep this file as decoupled from the presentation as possible
# so it's possible to use with any rendering framework, or even without rendering

from contextlib import contextmanager
from functools import lru_cache
from itertools import islice
from pathlib import Path


@lru_cache()
def locations():
    import my.location.google as G
    # todo islice something earlier?
    return list(G.locations())


@lru_cache()
def locations_dataframe(limit=None):
    import pandas as pd # type: ignore
    locs = locations()
    idf = pd.DataFrame(islice((l._asdict() for l in locs), 0, limit))
    df = idf.set_index('dt')
    return df


@lru_cache()
def sleep_dataframe():
    import my.body.sleep.main as S
    return S.dataframe()


@lru_cache()
def sleepiness_dataframe():
    import my.body.sleep.sleepiness as S
    df = S.dataframe()
    # TODO not sure if should do it here?
    # TODO stick nans closer to the original positions?
    df = df.set_index('dt').sort_index()
    return df


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


@lru_cache()
def manual_exercise_dataframe():
    import my.body.exercise.manual as M
    return M.dataframe()


@lru_cache
def rescuetime_dataframe():
    import my.rescuetime as R
    return R.dataframe()

@lru_cache
def bluemaestro_dataframe():
    import my.bluemaestro as B
    return B.dataframe()

# kwargs are attributes
def hack_config(name: str, **kwargs):
    # todo ugh. annoying that we need this boilerplate..
    # otherwise it would fail when the module is imported
    # todo document that in the github issue?
    from my.cfg import config
    class user_config:
        pass
    for k, v in kwargs.items():
        setattr(user_config, k, v)
    # need to check.. othewise it will overwrite the actual config..
    if not hasattr(config, name):
        setattr(config, name, user_config)


@contextmanager
def no_bluemaestro():
    # todo add some data later
    hack_config('bluemaestro', export_path='')
    yield


@contextmanager
def no_tz():
    # todo use something more meaningful?
    hack_config('google'  , takeout_path='')
    hack_config('location', home=(51.5074, 0.1278))
    yield


@contextmanager
def fake_rescuetime(*args, **kwargs):
    hack_config('rescuetime', export_path=[])

    import my.rescuetime as M
    with M.fake_data(*args, **kwargs), no_tz():
        yield


@contextmanager
def fake_emfit(*args, **kwargs):
    import pytz
    # todo get rid of timezone
    # todo get rid of excluded_sids, that should be hacked via the config
    hack_config('emfit', export_path=[], timezone=pytz.timezone('Europe/London'), excluded_sids=[])

    import my.emfit as M
    with M.fake_data(*args, **kwargs):
        yield

@contextmanager
def fake_jawbone(*args, **kwargs):
    # todo eh, it's using something else?
    hack_config('jawbone', export_path=[], export_dir=Path('/whatever'))

    import my.jawbone as M
    try:
        M.load_sleeps = lambda: []
        yield
    finally:
        from importlib import reload
        # that way we revert tmp config change?
        reload(M)


@contextmanager
def fake_sleep(*args, **kwargs):
    with fake_emfit(nights=1000), fake_jawbone(), no_bluemaestro(), no_tz():
        yield


@contextmanager
def fake_endomondo(*args, **kwargs):
    # todo hmm, when using export_path=[] here, getting
    # had an error ValueError: mutable default <class 'list'> for field export_path is not allowed: use default_factory
    hack_config('endomondo', export_path=())

    import my.endomondo as M
    with M.fake_data(*args, **kwargs):
        yield

# todo maybe this ^^ also belongs to HPI?
