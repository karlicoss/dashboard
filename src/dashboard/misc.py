from datetime import timedelta

from bokeh.models import ColumnDataSource as CDS
import numpy as np
import pandas as pd


# NOTE: vbar is _centered_ at the corresponding x
# TODO add reason? e.g. travel/public holiday/weekend?
def add_daysoff(plot, *, dates, bottom=0, top=80):
    # print(p.y_range.computed_range)
    # TODO not sure how to figure out min/max date automatically??
    # FIXME align to day boundary?
    mind = min(dates)
    maxd = max(dates)
    day = timedelta(1)

    # TODO need to keep boundary (-0.5, 0.5)?
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

