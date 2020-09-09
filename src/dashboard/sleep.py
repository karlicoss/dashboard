from datetime import timedelta, time

from .misc import add_daysoff
from .core.bokeh import rolling, date_figure


from bokeh.models import ColumnDataSource as CDS # type: ignore
from bokeh.models import LinearAxis, Range1d # type: ignore
import pandas as pd # type: ignore


def _sleep_df(df):
    # TODO if there are Nans, it fails to plot anything?? handle in a generic way, add warnings
    df = df[df['error'].isnull()]
    df = df.set_index('date')

    # todo make index??
    # mean = cs.rolling(f'{d}D').mean()

    # TODO ugh. figure out how pandas determines the index type..
    # todo not sure if I need this all?
    df.index = pd.to_datetime(df.index, utc=True)

    return df


def plot_sleep(df):
    df = _sleep_df(df)
    dates = df.index

    # TODO reuse functions for adding moving averages? Perhaps they should operate on dataframes to be framework independent?
    p = date_figure()
    add_daysoff(p, dates=dates)

    # TODO https://github.com/bokeh/bokeh/blob/master/examples/app/sliders.py

    # todo naming: plot vs figure vs graph?
    [g, g7, g30] = rolling(plot=p, x='date', y='avg_hr', df=df, color='blue', legend_label='HR')
    g7 .glyph.line_width = 2
    g30.glyph.line_color = 'lightblue'
    g30.glyph.line_width = 2


    p.extra_y_ranges = {'resp': Range1d(start=10, end=25)}
    # Addi the second axis to the plot.
    p.add_layout(LinearAxis(y_range_name='resp'), 'right')
    rolling(plot=p, x='date', y='respiratory_rate_avg', df=df, color='orange', legend_label='Respiration', avgs=['7D'], y_range_name='resp')

    # todo make it default, I always want this
    p.legend.click_policy = 'hide'
    return p

# todo always set output_file("xx.html")? so the latest html is always dumped?


# todo what's the benefit of having date index at all?
# todo think of better naming
def plot_sleep_hrv(df):
    df = _sleep_df(df)
    dates = df.index

    # TODO some hrv evening points are right at zero? careful, maybe worth filtering..
    p2 = date_figure()
    [g, g7, g30] = rolling(plot=p2, x='date', y='hrv_morning', df=df, color='green' )
    g7 .glyph.line_dash = 'dashed'
    g30.glyph.line_width = 2
    [g, g7, g30] = rolling(plot=p2, x='date', y='hrv_evening', df=df, color='purple')
    g7.glyph.line_dash = 'dashed'
    g30.glyph.line_width = 2
    add_daysoff(p2, dates=dates)

    p2.legend.click_policy = 'hide'
    return p2


def _mins(tt):
    # TODO shit. would just use time() but time doesn't allow wrapping around 24 hours
    # and timedelta is not serializable by plotly...
    mm = tt.hour * 60 + tt.minute
    if tt.hour < 16:
        mm += 24 * 60
    # TODO also careful about utc..
    return mm


def plot_sleep_intervals(df):
    df = _sleep_df(df)
    dates = df.index

    ints  = df[['sleep_start', 'sleep_end']].applymap(lambda dt: _mins(dt.time()))
    # todo maybe instead plot angled lines? then won't need messing with minutes at all? Although still useful to keep
    p = date_figure()
    mint = _mins(time(22, 0))
    maxt = _mins(time(11, 0))
    add_daysoff(p, bottom=mint, top=maxt, dates=dates)
    p.vbar(source=CDS(ints), x='date', width=timedelta(1), bottom='sleep_start', top='sleep_end', color='black', alpha=0.1)

    from bokeh.models import FuncTickFormatter, FixedTicker # type: ignore
    p.yaxis.ticker = FixedTicker(ticks=list(range(mint, maxt, 30)))
    p.yaxis.formatter = FuncTickFormatter(code="""
        var hh = Math.floor(tick / 60 % 24).toString()
        var mm = (tick % 60).toString()
        if (hh.length == 1) hh = "0" + hh;
        if (mm.length == 1) mm = "0" + mm;
        return `${hh}:${mm}`
    """)
    p.legend.click_policy = 'hide'

    return p


def plot_sleep_bedtime(df):
    df = _sleep_df(df)
    dates = df.index

    p = date_figure()
    [g, g7, g30] = rolling(plot=p, x='date', y='bed_time', df=df, color='green' )
    g7 .glyph.line_dash = 'dashed'
    g30.glyph.line_width = 2
    add_daysoff(p, dates=dates)

    # todo how to make this a default?
    p.legend.click_policy = 'hide'

    return p


# todo woudl be nice to hightlight hovered datapoints??
def plot_all_sleep(df):
    # TODO meh
    dates = _sleep_df(df).index

    from bokeh.layouts import gridplot
    from .core.bokeh import date_slider

    p1 = plot_sleep_bedtime(df=df)
    p1.legend.orientation = "horizontal"
    p1.legend.location = "top_left"
    # todo ok, this is nice.. maybe make it the default somehow?

    # breakpoint()

    p2 = plot_sleep(df=df)
    p2.legend.orientation = "horizontal"
    p2.legend.location = "top_left"
    p2.x_range = p1.x_range

    # TODO filter non-nan values??
    p3 = plot_sleep_hrv(df=df)
    p3.legend.orientation = "horizontal"
    p3.legend.location = "top_left"
    p3.x_range = p1.x_range


    p4 = plot_sleep_intervals(df=df)
    # todo toggle between 'absolute/relative' length
    p4.legend.orientation = "horizontal"
    p4.legend.location = "top_left"
    p4.x_range = p1.x_range


    # todo embedding bokeh server is probably not too bad
    # @gsteele13 show with notebook handles is for one-way Python->JS updates only. If you want to have bi-directional updates back to Python, you would need to embed a Bokeh server app in the notebook.
    DS = date_slider

    # todo set default slider range to start of year?
    return gridplot([
        [DS(p1, date_column='date')],
        [p1],
        [p2],
        [p3],
        [p4],
    ], sizing_mode='stretch_width')
    # todo scatter: maybe only display few latest points? not sure how easy it is to achieve?

    # TODO more frequent date ticks?
    # todo interactive scaling??
    # TODO not sure if holiday 'background' is that visually useful? perhaps different colours/extra highlight would be better after all. or both?
    # or just divide by holiday vs non-holiday and dynamically redraw sliding averages?
    # yeah.. visually figuring out the holiday-non holiday difference is impossible
