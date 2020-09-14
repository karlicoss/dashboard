from datetime import datetime

import pandas as pd
import numpy as np

from bokeh.plotting import figure

from .bokeh import rolling, date_figure

from hypothesis import given, settings, assume
from hypothesis.extra.pandas import columns, column, data_frames, range_indexes
import hypothesis.strategies as st


def hash_df(df) -> str:
    # https://stackoverflow.com/questions/31567401/get-the-same-hash-value-for-a-pandas-dataframe-each-time#comment89018817_47800021
    import hashlib
    from pandas.util import hash_pandas_object
    return hashlib.sha256(pd.util.hash_pandas_object(df, index=True).values).hexdigest()


# from hypothesis.strategies import text
# @given(text())
# def test_decode_inverts_encode(s):
#     assert s.encode('utf8').decode('utf8') == s


def save_plot(plot, name: str):
    from pathlib import Path
    suf = Path(name).suffix
    if suf == '.html':
        from bokeh.io import output_file, save
        output_file(name, title='hello', mode='inline', root_dir=None)
        save(plot)
    elif suf == '.png':
        # TODO sigh.. seems that png export is way too wlow
        from bokeh.io import export_png
        export_png(plot, filename=name)
    else:
        raise RuntimeError(name, suf)


# todo limit the number of examples?? or min_size?
@settings(derandomize=True)
@given(data_frames(
    columns=columns(['value'], dtype=float),
    rows=st.tuples(
        st.floats(min_value=3.0, max_value=100.0, allow_nan=False),
    ),
))
def test_rolling(df):
    assume(len(df) > 4) # TODO set min size
    # TODO needs to hande empty as well

    df.index.rename('x', inplace=True) # meh. by default index doesn't have name..
    r= rolling(x='x', y='value', df=df, avgs=[2, 5], legend_label='test')
    [g, g2, g5] = r
    save_plot(r.layout, 'res.html')
# TODO test all nans in y


# TODO meh
_count = 0

@settings(derandomize=True, max_examples=100)
@given(data_frames(
    index=range_indexes(min_size=10),
    columns=[
        column('dt'   , dtype=datetime),
        column('value', dtype=float   ),
    ],
    rows=st.tuples(
        st.datetimes(
            min_value=datetime.strptime('20190101', '%Y%m%d'),
            max_value=datetime.strptime('20200101', '%Y%m%d'),
        ),
        st.floats(min_value=20.0, max_value=100.0),
    ),
))
def test_rolling_errors(df):
    # TODO no idea why hypothesis spams me with duplicate results..
    df = df.drop_duplicates()
    assume(len(df) > 10)


    global _count
    print(_count)
    if _count > 3:
        return
    _count += 1

    # todo not sure if should inject these via hypothesis?
    # todo is this deterministic??
    df['error'] = None
    nan_dt    = df.sample(frac=0.1).index
    nan_value = df.sample(frac=0.1).index
    df.loc[nan_dt   , 'dt'   ] = np.nan
    df.loc[nan_dt   , 'error'] = 'no datetime ' * 20 # todo add some id??
    df.loc[nan_value, 'value'] = np.nan
    df.loc[nan_value, 'error'] = 'some error' # TODO add dt?

    df = df.drop(nan_dt & nan_value)

    # todo not sure if should be autodetected?
    df = df.set_index('dt')

    r = rolling(x='dt', y='value', df=df)
    [g, g7, g30] = r

    r.figure.legend.click_policy = 'hide'

    # todo saving takes a while.. maybe make it configurable?
    save_plot(r.layout, name=f'out/{_count}.html')
# TODO somehow reuse these for 'demo' tabs?
# TODO test when too many errors? title overfills and the plot collapses to zero
