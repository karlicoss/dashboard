import pandas as pd # type: ignore

from .core.bokeh import rolling, date_figure
from .core.bokeh import date_slider as DS

# TODO dataframe stubs would be useful

# TODO errors are usually of two types
# with dt
# without dt
# we're using exception for both, but setting an extra attribute (TODO think about the name?) + body
# good dynamic/safety balance. we benefit from the same Exception type without introducing extra restrictions
# on the other hand, if the attribute is unhandled, there is always a visual hint in the exception string


def plot_weight(df=None):
    # todo need dataframe type
    if df is None:
        from .data import weight_dataframe as DF
        df = DF()

    # TODO would be cool to make automatic?
    p = date_figure()

    # TODO decide on 'plot' vs 'figure'
    # TODO autodetecting would be nice, similar to old plotly dashboard
    [g, g7, g30] = rolling(plot=p, x='dt', y='weight', df=df, color='blue', legend_label='Weight')
    g7 .glyph.line_width = 2
    g30.glyph.line_color = 'lightblue'
    g30.glyph.line_width = 2

    # todo make it default, I always want this
    p.legend.click_policy = 'hide'

    from bokeh.layouts import gridplot
    # TODO how to make slider automatic?
    return gridplot([
        [DS(p)],
        [p],
    ])


# todo move these to hpi? not sure.
# todo inject random errors? have some sort of helper for that
def fake_weight_data():
    # TODO hmm, wonder what's the difference between hypothesis and faker wrt. data generation?
    from faker import Faker
    fake = Faker()
    fake.seed_instance(123)

    from datetime import datetime, timedelta
    # ok, later think of something proper
    start = datetime.strptime('20150101', '%Y%m%d')
    end   = datetime.strptime('20200101', '%Y%m%d')

    count = 200

    dates = [fake.date_time_between(start, end) for _ in range(count)]

    import math

    period = timedelta(days=100)
    weights = [
        # TODO brownian motion??
        # avg
        70.0 + \
        # oscillation
        5 * math.sin((dt - start) / period) + \
        # noise
        fake.pyint(min_value=-1, max_value=1)

        for dt in dates
    ]


    import pandas as pd
    df = pd.DataFrame([{
        'dt'    : dt,
        'weight': weight,
    } for dt, weight in zip(dates, weights)])

    df = df.set_index('dt')
    return df


# todo not sure if should/can keep tests close?
def test_plot_weight():
    return plot_weight(fake_weight_data())
