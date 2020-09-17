from datetime import timedelta

from bokeh.models import ColumnDataSource as CDS

from .core.bokeh import set_hhmm_axis, date_figure
from .misc import add_daysoff


def plot_rescuetime(df):
    # TODO figure out timezone in DAL
    def mins(dt):
        return dt.hour * 60 + dt.minute

    df = df.copy()

    df['date'] = df['dt'].dt.floor('D')
    df['left'  ] = df['date'] - timedelta(days=0.5) # make it centered at the day boundary
    df['right' ] = df['left'] + timedelta(days=1)
    df['bottom'] = df['dt'].apply(mins)
    df['top'   ] = df['bottom'] + df['duration_s'] / 60
    # todo add 'activity'? or break down and color by it??
    p = date_figure()
    # ok, seems that rectangles are the best choice judging by this https://docs.bokeh.org/en/latest/docs/user_guide/categorical.html#heatmaps
    p.quad(source=CDS(df), top='top', bottom='bottom', left='left',right='right', color="#B3DE69")
    top = 26 * 60
    set_hhmm_axis(p.yaxis, mint=0, maxt=top)

    add_daysoff(p, dates=df['dt'].dt.date, bottom=0, top=top)

    p.legend.click_policy = 'hide'
    return p
# TODO omit errors from tooltips if they aren't presetn
# TODO days off-add some sort of overlay to only show weekdays or only show weekends that would cover the plot completely
# so it's possible to switch and compare visually
