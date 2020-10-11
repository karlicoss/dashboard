import datetime

from bokeh.layouts import column
from bokeh.models import ColumnDataSource as CDS

from .core.bokeh import rolling, date_slider as DS
from .core import tab


def _plot_environment(df):
    # todo disable g by default
    # TODO need to agree on more consistent colors..
    # todo should be fixed/asserted in hpi?
    df = df.sort_index()
    rt = rolling(x='dt', y='temp'    , df=df, color='red' , legend_label='Temperature', avgs=['10min', '1D'])
    [g, g1h, g1d] = rt.plots
    g.glyph.marker = 'dot'
    g1h.glyph.line_width = 1
    g1d.glyph.line_color = 'darkred'
    g1d.glyph.line_width = 1

    rp = rolling(x='dt', y='pressure', df=df, color='grey', legend_label='Pressure'  , avgs=['10min', '1D'])
    [g, g1h, g1d] = rp.plots
    g.glyph.marker = 'dot'
    g1h.glyph.line_width = 1
    g1d.glyph.line_color = 'black'
    g1d.glyph.line_width = 1

    rh = rolling(x='dt', y='humidity', df=df, color='blue', legend_label='Humidity'  , avgs=['10min', '1D'])
    [g, g1h, g1d] = rh.plots
    g.glyph.marker = 'dot'
    g1h.glyph.line_width = 1
    g1d.glyph.line_color = 'darkblue'
    g1d.glyph.line_width = 1

    # todo make it default, I always want this
    rt.figure.legend.click_policy = 'hide'
    rp.figure.legend.click_policy = 'hide'
    rh.figure.legend.click_policy = 'hide'

    return column([
        # todo display date slider for every layout?
        DS(rt.figure, date_column='dt'),
        rt.layout,
        rp.layout,
        rh.layout,
    ], sizing_mode='stretch_width')


# TODO highlight different days?
# TODO holidays/non-home timezones would def be nice

@tab
def plot_environment():
    from .data import bluemaestro_dataframe as DF
    df = DF()
    return _plot_environment(df)

# TODO plot frequency of data?? could be even automatic (similar to hpi doctor/stat)
# TODO use repo with fake data?
#
# TODO for temp, maybe heatplot would make more sense? E.g. x axis days y axis time of day. although discontinuity at 0:00 is gonna be annoying.
# could group by weeks?
