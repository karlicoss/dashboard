'''
Correlations, etc., combined from multiple data sources (haven't come up with a better name yet)
'''

from datetime import timedelta

import pandas as pd

from .core import tab
from .core.analysis import deseasonalize
from .core.bokeh import scatter_matrix


class CE:
    dt = 'dt'
    volume = 'volume'


class CS:
    sleep_start = 'sleep_start'
    sleep_end = 'sleep_end'
    date = 'date'


# FIXME error handling
def _plot_sleep_vs_exercise(edf):
    # TODO compute some automatic holiday/weekend correlation
    # maybe, e.g. 'days off within the last 5 days'? or some sort of discounting?
    from .data import sleep_dataframe as SDF

    # TODO shorter horizons would also be useful? e.g. what if I exercised in the morning vs evening?
    # TODO not sure about longer horizons? maybe make them adjustable
    # horizon=None: up to the prev sleep. otherwise interpret as timedelta?
    # although still set max delta to maybe 30 hours? would handle missed night of sleep?
    sdf = SDF()
    sdf = sdf.sort_values(by=CS.sleep_start)

    def exercise_within(fr, to):
        return edf[edf[CE.dt].between(fr, to)]

    from more_itertools import windowed

    # TODO maybe use some namedtuply thing for column names?...
    has_date = sdf[CS.sleep_start].notna() & sdf[CS.sleep_end].notna()
    sdf = sdf[has_date]

    sdf = sdf.set_index('date')
    sdf.index = pd.to_datetime(sdf.index)
    sdf = sdf[~sdf.index.duplicated(keep=False)]

    # todo other rows?
    notna = sdf['avg_hr'].dropna()
    dhr = deseasonalize(notna).reindex_like(notna)  # TODO reindex internally?
    sdf['avg_hr_no_seasons'] = dhr
    sdf = sdf.reset_index()  # meh

    # todo would be nice to preserve column types from sdf?
    rows = []

    # todo drop emfit, handle coverage??
    # assert wit is not None # make mypy happy
    for [(i1, row1), (i2, row2)] in windowed(sdf.iterrows(), 2):  # type: ignore[misc]  # noqa: B007
        # TODO check no exercise overlaps?
        # todo error handling
        to = row2[CS.sleep_start]
        fr = row1[CS.sleep_end]
        # if the sleep is missing, assume 'day' lasted 30 hours
        fr = max(fr, to - timedelta(hours=30))
        ex = exercise_within(fr, to)
        # TODO add some assumption about base level
        # TODO need to handle walks etc
        volume = ex[CE.volume].sum()
        # FIXME not sure about that... otherwise end up with 0.0 which basically skews the whole plot
        if volume == 0.0:
            volume = None
        r = row2.drop([CS.date, CS.sleep_start, CS.sleep_end])
        rows.append(dict(volume=volume, **r))

    df = pd.DataFrame(rows)
    sm = scatter_matrix(df, xs=[CE.volume], width=1000, height=1000)
    return sm


# TODO FIXME need some jitter... otherwisethe integer points (e.g. HR get grouped and it's hard to see clusters)
# e.g. when exercise is 0


@tab
def plot_sleep_vs_cardio():
    from .data import cardio_dataframe as CDF

    cdf = CDF()
    cdf[CE.volume] = cdf['kcal']
    cdf[CE.dt] = cdf['start_time']
    return _plot_sleep_vs_exercise(cdf)


@tab
def plot_sleep_vs_strength():
    from .data import manual_exercise_dataframe as SDF

    sdf = SDF()
    sdf[CE.volume] = sdf['volume']
    # todo could interpolate time to average? prob. doesn't really matter
    sdf[CE.dt] = sdf['dt']
    return _plot_sleep_vs_exercise(sdf)


# todo pass title


# todo use a helper for combined fake data?
def plot_sleep_vs_exercise_fake():
    from .data import fake_endomondo, fake_sleep

    with fake_endomondo(count=100), fake_sleep():
        return plot_sleep_vs_cardio()


from .core.tests import make_test

test_sleep_vs_exercise = make_test(plot_sleep_vs_exercise_fake)

# TODO for notebook: set package name 'dashboard'?
