from datetime import timedelta

from bokeh.models import ColumnDataSource as CDS
import numpy as np
import pandas as pd

from .core.bokeh import guess_range


# NOTE: vbar is _centered_ at the corresponding x
# TODO add reason? e.g. travel/public holiday/weekend?
def add_daysoff(plot, *, dates=None, bottom=None, top=None):
    if bottom is None or top is None:
        b, t = guess_range(plot, axis='y')
        # todo how to extend the range a bit so there is some leeway?
        bottom = bottom or b
        top    = top    or t

    if dates is None:
        mind, maxd = guess_range(plot, axis='x')
    else:
        mind = min(dates)
        maxd = max(dates)
    day = timedelta(1)

    # todo need to keep boundary (-0.5, 0.5)? .. or it's automatic??
    days = list(np.arange(mind, maxd, day))
    # TODO make a dataframe with it??

    days_2 = pd.date_range(start=mind, end=maxd, freq='D')
    days_2.name = 'date'

    # FIXME make non-defensive, this is only temporary for tests
    try:
        import my.calendar.holidays as holidays
    except Exception as e:
        import logging
        logging.exception(e)
        return

    col_df = pd.DataFrame(index=days_2, columns=['color'])
    def calc_color(row):
        # todo separate column, abstract away
        dt = row.name
        is_workday = holidays.is_working_day(dt)
        return 'blue' if is_workday else 'red'

    col_df['color'] = col_df.apply(calc_color, axis=1)

    # right... nice thing about this is that it's infinite to the top and bottom...
    # but I have no clue how to make them togglable...
    # from bokeh.models import BoxAnnotation
    # for d, row in col_df.iterrows():
    #     ann = BoxAnnotation(left=d, right=d + day, fill_alpha=0.1, fill_color=row['color'])
    #     plot.add_layout(ann)

    # https://stackoverflow.com/a/56258632/706389
    # todo box annotation vs vbar??
    return plot.vbar(
        source=CDS(col_df),
        x='date',
        color='color',
        width=day,
        bottom=bottom,
        top=top,
        alpha=0.05,
        legend_label='Days off',
    )


