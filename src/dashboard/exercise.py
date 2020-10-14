'''
Non-cardio exercise: resistance/strength training, etc
'''
from itertools import cycle, chain

from bokeh.models import ColumnDataSource as CDS
from bokeh.palettes import Category20 as palletes
from bokeh.layouts import column
from bokeh.transform import jitter

from .core import tab
from .core.bokeh import date_figure, plot_multiple
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

    plots = []
    # todo hmm, reuse group hints somehow? not sure..

    # TODO helper groupby to check for None (to make sure they are handled)
    groups = list(df.groupby('name'))
    # sort by the most recent
    groups = list(sorted(groups, key=lambda name_d: max(unlocalize(name_d[1]['dt'])), reverse=True))

    names = [name for name, _ in groups]
    # make colors stable
    colors = {name: c for name, c in zip(names, cycle(pallete))}
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


@tab
def plot_manual_exercise():
    from .data import manual_exercise_dataframe as DF
    return _plot_manual_exercise(DF())

# TODO reuse same thingie for grouping stuff?
