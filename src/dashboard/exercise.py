'''
Non-cardio exercise: resistance/strength training, etc
'''
from itertools import cycle, chain

from bokeh.models import ColumnDataSource as CDS
from bokeh.palettes import Category20 as palletes
from bokeh.layouts import column

from .core import tab
from .core.bokeh import date_figure, plot_multiple


def _plot_manual_exercise(df):
    pallete = palletes[max(palletes)] # get last

    # todo one axis for count, one for seconds? although not really gonna work for
    # maybe on separate plots?
    has_err = df['error'].notna()
    errs = df[has_err].copy()
    errs['reps'] = 1 # meh
    # not sure? some errs have reps.. errs['reps'].fillna(-5) # meh
    df  = df[~has_err]

    plots = []
    # todo hmm, reuse group hints somehow? not sure..
    # TODO helper groupby to check for None?
    for color, (k, edf) in chain(
            [('red'           , ('errors', errs))],
            zip(cycle(pallete), df.groupby('name')),
    ):
        # todo add some x jitter to declutter?
        p = date_figure(df, height=150)
        p.scatter(x='dt', y='reps', source=CDS(edf), legend_label=k, color=color)
        p.legend.click_policy = 'hide'
        p.y_range.start = 0
        plots.append(p)
        # TODO not sure if I want sliding averages?
    return column(plots)


@tab
def plot_manual_exercise():
    from .data import manual_exercise_dataframe as DF
    return _plot_manual_exercise(DF())

# TODO reuse same thingie for grouping stuff?
