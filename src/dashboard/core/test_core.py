from datetime import datetime
from typing import Any

import hypothesis.strategies as st
import numpy as np
import pandas as pd
from hypothesis import example, given, settings
from hypothesis.extra.pandas import column, columns, data_frames, range_indexes

from .bokeh import rolling, scatter_matrix

# def hash_df(df) -> str:
#     # https://stackoverflow.com/questions/31567401/get-the-same-hash-value-for-a-pandas-dataframe-each-time#comment89018817_47800021
#     import hashlib
#     from pandas.util import hash_pandas_object
#     return hashlib.sha256(pd.util.hash_pandas_object(df, index=True).values).hexdigest()
# from hypothesis.strategies import text
# @given(text())
# def test_decode_inverts_encode(s):
#     assert s.encode('utf8').decode('utf8') == s
from .tests import save_plot

SETTINGS: dict[str, Any] = {
    'derandomize': True,  # I want deterministic..
    'deadline': None,  # saving timings might end up very different
}


@settings(**SETTINGS)
@given(
    data_frames(
        columns=columns(['value'], dtype=float),
        rows=st.tuples(
            st.floats(min_value=3.0, max_value=100.0, allow_nan=False),
        ),
    ).filter(lambda df: len(df) > 4)
)
# @example(pd.DataFrame([], columns=['value']))
@example(
    pd.DataFrame(
        [
            {
                'value': None,
            }
            for _ in range(10)
        ]
    )
)
def test_rolling(df):
    df.index = df.index.rename('x')  # meh. by default index doesn't have name..
    r = rolling(x='x', y='value', df=df, avgs=[2, 5], legend_label='test')
    [g, g2, g5] = r
    # todo need different numbers for each test
    save_plot(r.layout, 'test_rolling.html')


# todo meh, there must be a better way?
_count = 0


@settings(**SETTINGS, max_examples=10)
@given(
    data_frames(
        index=range_indexes(min_size=10),
        columns=[
            column('dt', dtype='datetime64[ns]'),
            column('value', dtype=float),
        ],
        rows=st.tuples(
            st.datetimes(
                min_value=datetime.strptime('20190101', '%Y%m%d'),
                max_value=datetime.strptime('20200101', '%Y%m%d'),
            ),
            st.floats(min_value=20.0, max_value=100.0),
        ),
        # for some reason hypothesis spams me with duplicate results...
    ).filter(lambda df: len(df) > 10)
)
@example(
    pd.DataFrame(
        [
            {
                'dt': None,
                'value': None,
            }
            for i in range(5)
        ]
    ).astype({'value': float})
)
def test_rolling_errors(df):
    global _count
    _count += 1

    # todo not sure if should inject these via hypothesis?
    # todo is this deterministic??
    df['error'] = None
    # fmt: off
    nan_dt    = df.sample(frac=0.1).index
    nan_value = df.sample(frac=0.1).index
    df.loc[nan_dt   , 'dt'   ] = np.nan
    df.loc[nan_dt   , 'error'] = 'no datetime ' * 20 # todo add some id??
    df.loc[nan_value, 'value'] = np.nan
    df.loc[nan_value, 'error'] = 'some error' # TODO add dt?
    # fmt: on

    df = df.drop(nan_dt & nan_value)

    # todo not sure if should be autodetected?
    df = df.set_index('dt')

    r = rolling(x='dt', y='value', df=df)
    [g, g7, g30] = r
    # todo saving takes a while.. maybe make it configurable?
    save_plot(r.layout, name=f'rolling_errors_{_count}.html')


# TODO somehow reuse these for 'demo' tabs?
# TODO test when too many errors? title overfills and the plot collapses to zero


# hmm max_examples isn't respected??
# right, it's because of the 'shrinking mode' when it's searching for minimal example
# https://hypothesis.works/articles/how-many-tests/#failing-tests


# TODO WTF?? it generates really dumb examples...
_count2 = 0
import string


@settings(**SETTINGS, max_examples=20)
@given(
    data_frames(
        columns=[
            column('dt', dtype='datetime64[ns]'),
            column('value1', dtype=float),
            column('value2', dtype=float),
            column('value3', dtype=float),
            column('error', dtype=str),
        ],
        rows=st.tuples(
            st.datetimes(
                min_value=datetime.strptime('20190101', '%Y%m%d'),
                max_value=datetime.strptime('20200101', '%Y%m%d'),
            ),
            st.floats(min_value=0.0, max_value=10.0),
            st.floats(allow_nan=True),
            st.floats(min_value=10.0, max_value=100.0),
            st.text(alphabet=string.ascii_letters),
        ),
    ).filter(lambda df: len(df) > 5)
)
# @example(pd.DataFrame([
#     dict(dt=None, value1=0.0, value2=0.0   , error=''),
#     dict(dt=None, value1=0.0, value2=np.inf, error=''),
# ]))
def test_scatter_matrix(df):
    # every other is an error
    df[::2]['error'] = ''

    r = scatter_matrix(df, ys=['value1', 'value2', 'value3'])
    global _count2
    _count2 += 1
    # TODO ugh. possibly need to disable Hypothesis check for deterministic time to run the function
    # this makes it retest too many times because the rendering takes unpredictable time..
    save_plot(r, name=f'test_scatter_matrix_{_count2}.html')
