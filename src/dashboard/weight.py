import pandas as pd

from .core.bokeh import rolling, date_figure
from .core.bokeh import date_slider as DS
from .core import tab

# TODO dataframe stubs would be useful

# TODO errors are usually of two types
# with dt
# without dt
# we're using exception for both, but setting an extra attribute (TODO think about the name?) + body
# good dynamic/safety balance. we benefit from the same Exception type without introducing extra restrictions
# on the other hand, if the attribute is unhandled, there is always a visual hint in the exception string

@tab
def plot_weight(df=None):
    # todo need dataframe type
    if df is None:
        from .data import weight_dataframe as DF
        df = DF()

    # todo decide on 'plot' vs 'figure'
    # TODO autodetecting would be nice, similar to old plotly dashboard
    res = rolling(x='dt', y='weight', df=df, color='blue', legend_label='Weight')
    [g, g7, g30] = res.plots
    g7 .glyph.line_width = 2
    g7 .visible = False  # type: ignore[assignment]  # ugh, bokeh type is Bool because it's a model or something??
    g30.glyph.line_color = 'lightblue'
    g30.glyph.line_width = 2

    # todo meh, a bit manual.. but works
    layout = res.layout
    # TODO how to make slider automatic?
    layout.children.insert(0, DS(res.figure))
    return layout


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


def plot_weight_fake():
    return plot_weight(fake_weight_data())


from .core.tests import make_test
test_plot_weight = make_test(plot_weight_fake)
