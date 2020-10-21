from datetime import timedelta

from bokeh.models import ColumnDataSource as CDS
from bokeh.layouts import column

from .core.bokeh import set_hhmm_axis, date_figure
from .core import tab
from .misc import add_daysoff


# todo add 'activity'? or break down and color by it??
def _plot_rescuetime(df):
    # TODO figure out timezone in DAL
    def mins(dt):
        return dt.hour * 60 + dt.minute

    # todo hmm, max might be greater than 3600? I wonder if this is because of hour boundaries

    def aux(df):
        df['date']   = df['dt'].dt.floor('D')
        df['left'  ] = df['date'] - timedelta(days=0.5) # make it centered at the day boundary
        df['right' ] = df['left'] + timedelta(days=1)
        df['bottom'] = df['dt'].apply(mins) # TODO use time type here instead??


    # right, so it seem it's aggregating at 5 minute boundaries? so if we don't do this, rects will overlap on the plot
    dfi = df.groupby('dt').sum().reset_index()
    aux(dfi)
    dfi['top'  ] = dfi['bottom'] + dfi['duration_s'] / 60
    dfi['alpha'] = 1.0


    dfh = df.set_index('dt').resample('1h').sum().reset_index()
    aux(dfh)
    dfh['top'  ] = dfh['bottom'] + 60
    dfh['alpha'] = dfh['duration_s'] / 3600.0

    # ok, seems that rectangles are the best choice judging by this https://docs.bokeh.org/en/latest/docs/user_guide/categorical.html#heatmaps

    def plot(p, df):
        # todo hmm, they overlap? maybe need to stack
        p.quad(source=CDS(df), top='top', bottom='bottom', left='left', right='right', color='darkgreen', alpha='alpha')
        top = 26 * 60
        set_hhmm_axis(p.yaxis, mint=0, maxt=top, period=60)
        add_daysoff(p)


    pi = date_figure()
    plot(pi, dfi)

    ph = date_figure(height=250)
    plot(ph, dfh)

    # todo hmm, I guess they have to be connected to the same datasource?
    from .core.bokeh import date_slider
    return column([
        date_slider(pi, date_column='date'),
        pi,
        date_slider(ph, date_column='date'),
        ph
    ])
# TODO omit errors from tooltips if they aren't presetn
# TODO days off-add some sort of overlay to only show weekdays or only show weekends that would cover the plot completely
# so it's possible to switch and compare visually


# right, so this can be used for smarter functions?? maybe even data filtering?
# from bokeh.transform import transform
# from bokeh.models import LinearColorMapper
# mapper = LinearColorMapper(palette=colors, low=0, high=3600)
# transform('duration_s', mapper))

@tab
def plot_rescuetime():
    from .data import rescuetime_dataframe as DF
    return _plot_rescuetime(DF())


def plot_rescuetime_fake():
    from .data import fake_rescuetime
    with fake_rescuetime(rows=100000):
        return plot_rescuetime()


from .core.tests import make_test
test_rescuetime = make_test(plot_rescuetime_fake)
