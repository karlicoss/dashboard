from datetime import timedelta, time

from .misc import add_daysoff
from .core.bokeh import rolling, date_figure
from .core import tab


from bokeh.models import ColumnDataSource as CDS
from bokeh.models import LinearAxis, Range1d
import pandas as pd


def _sleep_df(df):
    df = df.set_index('date')

    # todo make index??
    # mean = cs.rolling(f'{d}D').mean()

    # TODO ugh. figure out how pandas determines the index type..
    # todo not sure if I need this all?
    # TODO should just unlocalize?
    df.index = pd.to_datetime(df.index, utc=True)
    return df


# TODO def need to run tests against sleep frames
def _plot_sleep(df):
    df = _sleep_df(df)

    # TODO https://github.com/bokeh/bokeh/blob/master/examples/app/sliders.py

    # todo naming: plot vs figure vs graph?
    r = rolling(x='date', y='avg_hr', df=df, color='blue', legend_label='HR')
    [g, g7, g30] = r
    g7 .glyph.line_width = 2
    g30.glyph.line_color = 'lightblue'
    g30.glyph.line_width = 2
    p = r.figure

    p.extra_y_ranges = {'resp': Range1d(start=10, end=25)}
    # Add the second axis to the plot.
    p.add_layout(LinearAxis(y_range_name='resp'), 'right')
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
    add_daysoff(p)
    return r

# todo always set output_file("xx.html")? so the latest html is always dumped?


# todo what's the benefit of having date index at all?
# todo think of better naming
def plot_sleep_hrv(df):
    df = _sleep_df(df)

    # TODO some hrv evening points are right at zero? careful, maybe worth filtering..
    rm = rolling(df=df, x='date', y='hrv_morning', color='green' )
    [g, g7, g30] = rm
    g7 .glyph.line_dash = 'dashed'
    g30.glyph.line_width = 2
    re = rolling(df=df, x='date', y='hrv_evening', color='purple', context=rm)
    g7.glyph.line_dash = 'dashed'
    g30.glyph.line_width = 2

    r = rm
    add_daysoff(r.figure)
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
    def prettify(start, end):
        assert (end - start).days == 0, (start, end) # just in case
        mins = lambda d: d.time().hour * 60 + d.time().minute

        if start.date() == end.date():
            return mins(start), mins(end)
        else:
            # meh. day boundary
            day = end.replace(hour=0, minute=0, second=0, microsecond=0)
            if day - start > end - day:
                return mins(start), mins(end) + 24 * 60 # meh
            else:
                return mins(start) - 24 * 60, mins(end)
    def aux(row):
        start = row['sleep_start']
        end   = row['sleep_end']
        if pd.isnull(start) or pd.isnull(end):
            return None
        (start, end) = prettify(start, end)
        return pd.Series([start, end]) # meh

    ints = df[['sleep_start', 'sleep_end']] .apply(aux, axis='columns')
    ints = ints.rename({0: 'sleep_start', 1: 'sleep_end'}, axis='columns')

    # todo maybe instead plot angled lines? then won't need messing with minutes at all? Although still useful to keep
    p = date_figure()
    # ugh. very messy
    mint = -24 * 60 - 10 * 60
    maxt =  24 * 60 + 10 * 60
    # TODO need to handle nans/errors?

    # TODO not convinced 'date' quite works here...
    p.vbar(source=CDS(ints), x='date', width=timedelta(1), bottom='sleep_start', top='sleep_end', color='black', alpha=0.1)

    from .core.bokeh import set_hhmm_axis
    # TODO also guess mint/maxt?
    set_hhmm_axis(p.yaxis, mint=mint, maxt=maxt)

    add_daysoff(p)
    return p


def plot_sleep_bedtime(df):
    df = _sleep_df(df)

    r = rolling(df=df, x='date', y='bed_time', color='green' )
    [g, g7, g30] =r
    g7 .glyph.line_dash = 'dashed'
    g30.glyph.line_width = 2
    add_daysoff(r.figure)
    # TODO crap. at the moment, the return type isn't compatible with show()
    # use the same delegate trick as with setting __dict__??
    return r


# todo woudl be nice to hightlight hovered datapoints??
def _plot_all_sleep(df):
    df = _fix_NaT_datetime(df)

    from .core.bokeh import date_slider

    r1 = plot_sleep_bedtime(df=df)
    p1 = r1.figure

    r2 = _plot_sleep(df=df)
    p2 = r2.figure
    p2.x_range = p1.x_range

    # TODO filter non-nan values??
    r3 = plot_sleep_hrv(df=df)
    p3 = r3.figure
    p3.x_range = p1.x_range


    p4 = plot_sleep_intervals(df=df)
    # todo toggle between 'absolute/relative' length
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


def _fix_NaT_datetime(df):
    # ugh. some of these contain NaT (not a time), and this causes bokeh to crash during rendering??
    # getting "Out of range float values are not JSON compliant: nan"
    # they aren't even used during rendering, but I think bokeh just serializes the whole df?
    # FIXME would be nice to fix this as this prevents displaying errors over in plots
    return df.dropna(subset=['sleep_start', 'sleep_end'])


def _plot_sleep_correlations(df):
    df = _fix_NaT_datetime(df)

    # todo add holiday/non-holiday? or days from holiday? could be interesting
    # todo reuse/determine width
    # hmm, didn't manage to quickly google how to do this
    from .core.bokeh import scatter_matrix
    sm = scatter_matrix(df, width=3000, height=3000)
    return sm
    # TODO autodetect and have a global render() function that can handle anything?

    # TODO add tools for vertical projections?
    # ugh. https://github.com/holoviz/hvplot/blob/ab43c4f68aa7e485326dea567a348b96d24ebf60/hvplot/plotting/scatter_matrix.py#L45 not sure if the needed parameters are passed?..
    # gridmatrix code? https://github.com/holoviz/holoviews/blob/5deb4a7b7f04f989fcc39bb06e657e8b6dfb4ea2/holoviews/operation/element.py#L997
    # TODO date slider? to hightligh changes over dates E.g. left-right


@tab
def plot_sleep_all():
    from .data import sleep_dataframe as DF
    return _plot_all_sleep(DF())


@tab
def plot_sleep_correlations():
    from .data import sleep_dataframe as DF
    return _plot_sleep_correlations(DF())


def plot_sleep_all_fake():
    from .data import fake_sleep
    with fake_sleep():
        return plot_sleep_all()


def plot_sleep_correlations_fake():
    from .data import fake_sleep
    with fake_sleep():
        return plot_sleep_correlations()


from .core.tests import make_test
test_sleep_all          = make_test(plot_sleep_all_fake)
test_sleep_correlations = make_test(plot_sleep_correlations_fake)

# TODO ideally I want to visualize the DF automatically? and maybe tweak specific details
