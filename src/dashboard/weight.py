import pandas as pd # type: ignore

from .core.bokeh import rolling, date_figure

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

    # todo I guess dates off are not useful here?
    p = date_figure()

    # TODO decide on 'plot' vs 'figure'
    # TODO autodetecting would be nice, similar to old plotly dashboard
    [g, g7, g30] = rolling(plot=p, x='dt', y='weight', df=df, color='blue', legend_label='Weight')
    g7 .glyph.line_width = 2
    g30.glyph.line_color = 'lightblue'
    g30.glyph.line_width = 2

    # todo make it default, I always want this
    p.legend.click_policy = 'hide'
    return p
