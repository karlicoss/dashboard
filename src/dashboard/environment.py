import datetime

from bokeh.layouts import column
from bokeh.models import ColumnDataSource as CDS

from .core.bokeh import rolling, date_slider as DS


def _plot_environment(df):
    # todo should be fixed/asserted in hpi?
    df = df.sort_index()
    res = rolling(x='dt', y='temp', df=df, color='blue', legend_label='Temperature', avgs=['10min', '1D'])
    [g, g1h, g1d] = res.plots
    # todo disable g by default
    g.glyph.marker = 'dot'
    g1h.glyph.line_width = 1
    # TODO need to agree on more consistent colors..
    g1d.glyph.line_color = 'black'
    g1d.glyph.line_width = 1

    # todo make it default, I always want this
    res.figure.legend.click_policy = 'hide'

    return column([
        DS(res.figure, date_column='dt'),
        res.layout,
    ], sizing_mode='stretch_width')


# TODO highlight different days?
# TODO holidays/non-home timezones would def be nice

def plot_environment():
    from .data import bluemaestro_dataframe as DF
    df = DF()
    return _plot_environment(df)

# TODO plot frequency of data?? could be even automatic (similar to hpi doctor/stat)
# TODO use repo with fake data?
#
# TODO for temp, maybe heatplot would make more sense? E.g. x axis days y axis time of day. although discontinuity at 0:00 is gonna be annoying.
# could group by weeks?
