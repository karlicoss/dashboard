'''
Subjectiveness sleepiness, felt during the day
'''
from datetime import timedelta

from bokeh.layouts import column
from bokeh.models import CustomJSTickFormatter

import pandas as pd

from .core.bokeh import scatter_matrix, rolling, hhmm_formatter
from .core.pandas import unlocalize, lag_df
from .core import tab


def _sleepy_df():
    from .data import sleepiness_dataframe as SDF
    s = SDF()
    s = s[s['error'].isna()]
    # todo: need to be careful about nans in index?
    s.index = unlocalize(s.index)
    s['sleepy'] = 1
    return s


@tab
def plot_sleepiness_vs_exercise():
    # TODO strenght exercise
    from .data import cardio_dataframe as CDF

    c = CDF()
    c['dt'] = unlocalize(c['start_time'])
    c = c.set_index('dt').sort_index()
    c = c[c['error'].isna()]
    # FIXME error handling
    # todo for error handling, would be nice to have unused variable detection?

    s = _sleepy_df()
    c = c[c.index >= min(s.index)] # clip till the time we started collecting it

    deltas = [timedelta(hours=h) for h in range(-200, 200)]
    # we want to find out what predicts sleepiness..
    # so sleepiness is y and kcal is x
    ldf = lag_df(x=c['kcal'], y=s['sleepy'], deltas=deltas)

    # todo maybe rolling is a somewhat misleading name?
    f = rolling(x='lag', y='value', df=ldf, avgs=[]).figure
    f.xaxis.formatter = CustomJSTickFormatter(code=hhmm_formatter(unit=ldf.index.dtype))
    return f


@tab
def plot_sleepiness_vs_sleep():
    from .data import sleep_dataframe as DF
    sdf = DF()

    sdf = sdf[sdf['error'].isna()]
    # todo not sure... maybe sleep start/end would be better? or just median??
    sdf = sdf.set_index('date')
    sdf.index = pd.to_datetime(sdf.index)  # without it, getting TypeError: Cannot compare Timestamp with datetime.date.
    # sdf.index = unlocalize(sdf.index)  # TODO what was that for?

    s = _sleepy_df()
    sdf = sdf[sdf.index >= min(s.index)]

    deltas = [timedelta(hours=h) for h in range(-24 * 5, 24 * 5, 4)]
    # TODO need something similar to scatter matrix, but instead of scatter, covariance??
    # TODO unhardcode
    ress = []
    for col in ['bed_time', 'coverage', 'avg_hr', 'hrv_morning', 'hrv_evening']:
        ldf = lag_df(x=sdf[col], y=s['sleepy'], deltas=deltas)
        # TODO wtf?? so
        r = rolling(x='lag', y='value', df=ldf, avgs=[])
        r.figure.title.text = f'lag plot: sleepiness vs {col}'
        r.figure.xaxis.formatter = CustomJSTickFormatter(code=hhmm_formatter(unit=ldf.index.dtype))
        ress.append(r)
    # TODO maybe allow to yield plots? then just assume column layout
    return column([r.layout for r in ress])
    # TODO this doesn't make any sense... why lag always grows negative as the window size increases??
    # also probably doesn't make sense to make window bigger than the next sleep? dunno.
