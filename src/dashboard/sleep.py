from datetime import timedelta, time

from .misc import add_daysoff
from .core.bokeh import rolling, date_figure


from bokeh.models import ColumnDataSource as CDS
from bokeh.models import LinearAxis, Range1d
import pandas as pd


def _sleep_df(df):
    df = df.set_index('date')

    # todo make index??
    # mean = cs.rolling(f'{d}D').mean()

    # TODO ugh. figure out how pandas determines the index type..
    # todo not sure if I need this all?
    df.index = pd.to_datetime(df.index, utc=True)

    return df


# TODO def need to run tests against sleep frames
def plot_sleep(df):
    df = _sleep_df(df)
    dates = df.index

    # TODO https://github.com/bokeh/bokeh/blob/master/examples/app/sliders.py

    # todo naming: plot vs figure vs graph?
    r = rolling(x='date', y='avg_hr', df=df, color='blue', legend_label='HR')
    [g, g7, g30] = r
    g7 .glyph.line_width = 2
    g30.glyph.line_color = 'lightblue'
    g30.glyph.line_width = 2

    p = r.figure
    # TODO not sure about adding before vs after
    add_daysoff(p, dates=dates)

    p.extra_y_ranges = {'resp': Range1d(start=10, end=25)}
    # Addi the second axis to the plot.
    p.add_layout(LinearAxis(y_range_name='resp'), 'right')

    # todo make it default, I always want this
    p.legend.click_policy = 'hide'

    # TODO FIXME sigh. bring it back..
    # TODO shit. need it to reuse the figure somehow??
    # todo eh?
    # ERROR:bokeh.core.validation.check:E-1027 (REPEATED_LAYOUT_CHILD): The same model can't be used multiple times in a layout: Column(id='76726', ...)
    rolling(
        df=df,
        x='date', y='respiratory_rate_avg',
        color='orange',
        legend_label='Respiration',
        avgs=['7D'],
        y_range_name='resp',
        context=r,
    )
    # TODO hmm, it appends error twice? not sure about it...
    return r

# todo always set output_file("xx.html")? so the latest html is always dumped?


# todo what's the benefit of having date index at all?
# todo think of better naming
def plot_sleep_hrv(df):
    df = _sleep_df(df)
    dates = df.index

    # TODO some hrv evening points are right at zero? careful, maybe worth filtering..
    rm = rolling(df=df, x='date', y='hrv_morning', color='green' )
    [g, g7, g30] = rm
    g7 .glyph.line_dash = 'dashed'
    g30.glyph.line_width = 2
    re = rolling(df=df, x='date', y='hrv_evening', color='purple', context=rm)
    g7.glyph.line_dash = 'dashed'
    g30.glyph.line_width = 2

    r = rm
    add_daysoff(r.figure, dates=dates)

    r.figure.legend.click_policy = 'hide'
    return r


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

    ints  = df[['sleep_start', 'sleep_end']].applymap(lambda dt: None if pd.isnull(dt) else _mins(dt.time()))
    # todo maybe instead plot angled lines? then won't need messing with minutes at all? Although still useful to keep
    p = date_figure()
    mint = _mins(time(22, 0))
    maxt = _mins(time(11, 0))
    add_daysoff(p, bottom=mint, top=maxt, dates=dates)
    # TODO need to handle nans/errors?
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

    r = rolling(df=df, x='date', y='bed_time', color='green' )
    [g, g7, g30] =r
    g7 .glyph.line_dash = 'dashed'
    g30.glyph.line_width = 2
    add_daysoff(r.figure, dates=dates)

    # todo how to make this a default?
    r.figure.legend.click_policy = 'hide'

    # TODO crap. at the moment, the return type isn't compatible with show()
    # use the same delegate trick as with setting __dict__??
    return r


# todo woudl be nice to hightlight hovered datapoints??
def plot_all_sleep(df):
    # TODO meh
    dates = _sleep_df(df).index

    from .core.bokeh import date_slider

    r1 = plot_sleep_bedtime(df=df)
    p1 = r1.figure
    p1.legend.orientation = "horizontal"
    p1.legend.location = "top_left"
    # todo ok, this is nice.. maybe make it the default somehow?

    r2 = plot_sleep(df=df)
    p2 = r2.figure
    p2.legend.orientation = "horizontal"
    p2.legend.location = "top_left"
    p2.x_range = p1.x_range

    # TODO filter non-nan values??
    r3 = plot_sleep_hrv(df=df)
    p3 = r3.figure
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

    # todo merge_tools=False? might make more sense

    # todo set default slider range to start of year?
    from bokeh.layouts import column
    return column([
        DS(p1, date_column='date'),
        # todo display date slider for every layout?
        r1.layout,
        r2.layout,
        r3.layout,
        p4,
    ], sizing_mode='stretch_width')
    # todo scatter: maybe only display few latest points? not sure how easy it is to achieve?

    # TODO more frequent date ticks?
    # todo interactive scaling??
    # TODO not sure if holiday 'background' is that visually useful? perhaps different colours/extra highlight would be better after all. or both?
    # or just divide by holiday vs non-holiday and dynamically redraw sliding averages?
    # yeah.. visually figuring out the holiday-non holiday difference is impossible


def plot_sleep_correlations(df):
    # todo add holiday/non-holiday? or days from holiday? could be interesting
    # TODO remove hardcoding
    # TODO seems that is simply omits non-numeric columns?? check the dimension of grid and warn
    # df['something'] = 'alala'
    cols = ['date', 'coverage', 'avg_hr', 'hrv_change'] # , 'bed_time', 'recovery', 'respiratory_rate_avg']
    df = df[cols]

    from bokeh.models import HoverTool
    # todo uhoh. I guess the other fields won't be available for hover?
    hover = HoverTool(
        tooltips=[(x, f'@{x}') for x in df.columns],
        #formatters={
        #    '@date'        : 'datetime', # use 'datetime' formatter for '@date' field
        #},
        # display a tooltip whenever the cursor is vertically in line with a glyph
        # not sure about that here
        # not sure if it even works??
        # mode='vline'
    )


    # todo reuse/determine width
    # hmm, didn't manage to quickly google how to do this
    # todo chart_opts in hvplot.scatter_matric?
    tools = [hover, 'box_select', 'lasso_select', 'tap']
    from .core.bokeh import scatter_matrix
    import holoviews as hv
    sm = scatter_matrix(df, width=2000, height=2000).opts(
        # todo make it deafult in scatter_matrix??
        hv.opts.Scatter  (tools=tools),
        hv.opts.Histogram(tools=tools),
    #    # opts.Layout(width=2000, height=2000), # -- doesn't seem to do anything?
    )

    # TODO autodetect and have a global render() function that can handle anything?
    return hv.render(sm)

    # TODO add tools for vertical projections?
    # ugh. https://github.com/holoviz/hvplot/blob/ab43c4f68aa7e485326dea567a348b96d24ebf60/hvplot/plotting/scatter_matrix.py#L45 not sure if the needed parameters are passed?..
    # gridmatrix code? https://github.com/holoviz/holoviews/blob/5deb4a7b7f04f989fcc39bb06e657e8b6dfb4ea2/holoviews/operation/element.py#L997
    # TODO date slider? to hightligh changes over dates E.g. left-right
    # TODO show dates on tooltips
