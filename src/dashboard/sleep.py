from datetime import timedelta

from bokeh.models import ColumnDataSource as CDS # type: ignore

import numpy as np # type: ignore
import pandas as pd # type: ignore


def add_daysoff(plot, *, dates, bottom=0, top=80):
    # print(p.y_range.computed_range)
    # TODO not sure how to figure out min/max date automatically??
    mind = min(dates)
    maxd = max(dates)
    day = timedelta(1)

    # TODO need to keep boundary (-0.5, 0.5)?
    days = list(np.arange(mind, maxd, day))
    # TODO make a dataframe with it??

    days_2 = pd.date_range(start=mind, end=maxd, freq='D')
    days_2.name = 'date'

    import my.calendar.holidays as holidays

    col_df = pd.DataFrame(index=days_2, columns=['color'])
    def calc_color(row):
        # todo separate column, abstract away
        dt = row.name
        is_workday = holidays.is_working_day(dt)
        return 'blue' if is_workday else 'red'

    col_df['color'] = col_df.apply(calc_color, axis=1)

    # https://stackoverflow.com/a/56258632/706389
    # todo box annotation vs vbar??
    return plot.vbar(
        source=CDS(col_df),
        x='date',
        color='color',
        width=timedelta(1),
        bottom=bottom,
        top=top,
        alpha=0.05,
        legend_label='Days off',
    )


# todo not sure if it's really necessary
def date_figure(**kwargs):
    from bokeh.models import HoverTool # type: ignore
    from bokeh.plotting import figure # type: ignore

    # todo need other columns
    hover = HoverTool(
        tooltips=[
            ( 'date',   '@date{%F}'            ),
        ],
        formatters={
            '@date'        : 'datetime', # use 'datetime' formatter for '@date' field
        },
        # display a tooltip whenever the cursor is vertically in line with a glyph
        mode='vline'
    )
    f = figure(x_axis_type='datetime', plot_width=2000, **kwargs)
    f.add_tools(hover)
    return f
