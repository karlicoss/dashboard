'''
Non-cardio exercise: resistance/strength training, etc
'''
from itertools import cycle, chain

from bokeh.models import ColumnDataSource as CDS
from bokeh.palettes import Category20 as palletes
from bokeh.layouts import column
from bokeh.transform import jitter

from .core import tab
from .core.bokeh import date_figure, plot_multiple, rolling
from .core.pandas import unlocalize


def _plot_manual_exercise(df):
    pallete = palletes[max(palletes)] # get last

    # todo one axis for count, one for seconds? although not really gonna work for
    # maybe on separate plots?
    has_err = df['error'].notna()
    errs = df[has_err].copy()
    errs['reps'] = 1 # meh
    some_dt = df['dt'].dropna().iloc[-1]
    errs['dt'].fillna(some_dt, inplace=True)
    # not sure? some errs have reps.. errs['reps'].fillna(-5) # meh
    df  = df[~has_err]
    # TODO would be nice to reuse stuff to display errors as a table

    # FIXME handle none carefully here, otherwise they aren't displayed
    plots = []
    # todo hmm, reuse group hints somehow? not sure..

    # TODO helper groupby to check for None (to make sure they are handled)
    groups = list(df.groupby('kind'))
    # sort by the most recent
    groups = list(sorted(groups, key=lambda kind_d: max(unlocalize(kind_d[1]['dt'])), reverse=True))

    kinds = [kind for kind, _ in groups]
    # make colors stable
    colors = {kind: c for kind, c in zip(kinds, cycle(pallete))}
    colors['errors'] = 'red'

    x_range = None
    for k, edf in chain(
            [('errors', errs)],
            groups,
    ):
        color = colors[k]
        # todo add some x jitter to declutter?
        # need to preserve the order though? I guess need to group
        p = date_figure(df, height=150, x_range=x_range)
        p.scatter(x='dt', y='reps', source=CDS(edf), legend_label=k, color=color)
        p.legend.click_policy = 'hide'
        p.y_range.start = 0

        if x_range is None:
            x_range = p.x_range
        plots.append(p)
        # TODO not sure if I want sliding averages?
    # FIXME tooltips -- dt displayed as milliseconds
    return column(plots)


def _plot_strength_volume(df):
    # TODO make a single point through which the errors get?
    # general pattern:
    # a) make sure the lowest level stuff is paranoid and dumps warnings/exception/spams on plot
    # b) helpers for split_errors
    # b) static analysis to check unused stuff
    df['dt'] = unlocalize(df['dt'])
    df = df.set_index('dt')

    has_err = df['error'].notna()
    # todo split_by helper??
    errs = df[has_err].copy()
    df = df[~has_err]
    # todo what happens to errors??
    df = df.resample('D').sum()
    # todo do not display '0' here? special option??
    # FIXME add mixed timezones to rolling tests

    # TODO color different points as exercise kinds?
    res = rolling(x='dt', y='volume', df=df, avgs=['30D'])
    return res.figure


# todo add cardio here as well? should be the summary of all exercise?
@tab
def plot_manual_exercise():
    from .data import manual_exercise_dataframe as DF
    return _plot_manual_exercise(DF())

@tab
def plot_strength_volume():
    from .data import manual_exercise_dataframe as DF
    return _plot_strength_volume(DF())

# TODO reuse same thingie for grouping stuff?
