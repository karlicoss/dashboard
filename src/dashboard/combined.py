'''
Correlations, etc., combined from multiple data sources (haven't come up with a better name yet)
'''
from datetime import timedelta

from bokeh.models import HoverTool

from .core.bokeh import scatter_matrix

def _plot_sleep_vs_exercise(df):
    import holoviews as hv

    # todo copy pasted, use a generic function
    hover = HoverTool(
        tooltips=[(x, f'@{x}') for x in df.columns],
    )
    tools = [hover, 'box_select', 'lasso_select', 'tap']
    sm = scatter_matrix(df, width=2000, height=2000).opts(
        # todo make it deafult in scatter_matrix??
        hv.opts.Scatter  (tools=tools),
        hv.opts.Histogram(tools=tools),
    #    # opts.Layout(width=2000, height=2000), # -- doesn't seem to do anything?
    )
    return hv.render(sm)

class C:
    sleep_start = 'sleep_start'
    sleep_end   = 'sleep_end'


# FIXME error handling
# todo add sleepiness, mental state and dreams (I guess to the main sleep df)
def plot_sleep_vs_exercise():
    # TODO compute some automatic holiday/weekend correlation
    # maybe, e.g. 'days off within the last 5 days'? or some sort of discounting?
    from .data import sleep_dataframe  as SDF
    from .data import cardio_dataframe as CDF
    # TODO shorter horizons would also be useful? e.g. what if I exercised in the morning vs evening?
    # TODO not sure about longer horizons? maybe make them adjustable
    # horizon=None: up to the prev sleep. otherwise interpret as timedelta?
    # although still set max delta to maybe 30 hours? would handle missed night of sleep?
    sdf = SDF()
    cdf = CDF()

    sdf = sdf.sort_values(by='sleep_start')

    def exercise_within(fr, to):
        return cdf[cdf['start_time'].between(fr, to)]

    from more_itertools import windowed

    # TODO maybe use some namedtuply thing for column names?...
    has_date = sdf[C.sleep_start].notna() & sdf[C.sleep_end].notna()
    sdf = sdf[has_date]

    # todo would be nice to preserve column types from sdf?
    rows = []

    # todo drop emfit, handle coverage??
    # assert wit is not None # make mypy happy
    for [(i1, row1), (i2, row2)] in windowed(sdf.iterrows(), 2): # type: ignore[misc]
        # TODO check no exercise overlaps?
        # todo error handling
        to = row2[C.sleep_start]
        fr = row1[C.sleep_end]
        # if the sleep is missing, assume 'day' lasted 30 hours
        fr = max(fr, to - timedelta(hours=30))
        ex = exercise_within(fr, to)
        # TODO add some assumption about base level
        # TODO need to handle walks etc
        volume = ex['kcal'].sum()
        r = row2.drop(['date', 'sleep_end', 'sleep_start'])
        rows.append(dict(volume=volume, **r))

    import pandas as pd
    df = pd.DataFrame(rows)

    return _plot_sleep_vs_exercise(df)


def plot_sleep_vs_exercise_fake():
    from .data import fake_sleep, fake_endomondo
    with fake_endomondo(count=100), fake_sleep():
        return plot_sleep_vs_exercise()


def test_sleep_vs_exercise():
    from .core.test_core import save_plot
    f = plot_sleep_vs_exercise_fake()
    save_plot(f, name='sleep_vs_exercise.html')


# TODO for notebook: set package name 'dashboard'?
