import logging
from typing import Union, Sequence, List

import pandas as pd
from pandas.api.types import is_numeric_dtype

Column = str


Groups = Sequence[Union[Sequence[Column], Column]]

def set_group_hints(df, groups: Groups):
    # todo set default to empty/none?
    df.attrs['group_hints'] = groups
    return df


def read_group_hints(df):
    hints = df.attrs['group_hints']

    cols = list(df.columns)

    groups: List[List[Column]] = []

    # TODO warn if not presetn??

    for x in hints:
        gr: List[Column]
        if isinstance(x, Column):
            gr = [x]
        else:
            gr = list(x)
        gg: List[Column] = []
        for f in gr:
            if f not in cols:
                # TODO this should be displayed separately as 'errors'
                logging.warning('Unexpected column: %s', f)
            else:
                cols.remove(f)
                gg.append(f)
        groups.append(gg)

    if len(cols) == 0:
        logging.warning('Unexpected columns: %s', cols)
        groups.append(cols)

    return groups


#####
from typing import Tuple, Optional, Dict, NamedTuple
# highlight for 'normal' ranges
# todo would be also nice to have actual vertical ranges too?

class Range(NamedTuple):
    # todo later, allow Optional
    low: float
    high: float
    color: Optional[str] = None # up to the renderer??

RangeHints = Dict[Column, Sequence[Range]]


_RANGE_HINTS = 'range_hints'
# todo perhaps ranges could be more dynamic? e.g. with colours and annotations?
# like in Thriva's reports
def set_range_hints(df, ranges: RangeHints):
    df.attrs[_RANGE_HINTS] = ranges
    return df


def read_range_hints(df) -> RangeHints:
    hints = df.attrs.get(_RANGE_HINTS, {})
    # TODO warn about unknown columns?
    return hints

#####

# NOTE:
# When one or more x_t+h, with negative h, are predictors of y_t, it is sometimes said that x leads y.
# When one or more x_t+h, with positive h, are predictors of y_t, it is sometimes said that x lags  y.
# TODO can probably implement it natively in pandas??
def lag_df(*, x, y, deltas):
    # TODO careful with x/y interpretation?
    rows = []
    idx = x.index
    for lag in deltas:
        # min/max for negative values handling
        fun = lambda dt: y[min(dt, dt + lag): max(dt, dt + lag)].sum()
        within = pd.Series(idx.map(fun), index=idx)
        r = x.cov(within)
        # TODO might be useful to add regline/uncertaincy.. some correlations are complete crap
        rows.append(dict(lag=lag, value=r))
    return pd.DataFrame(rows).set_index('lag')


def unlocalize(s):
    # TODO maybe do some extra checks?
    return s.map(lambda d: None if d is None else d.replace(tzinfo=None))


def resample_sum(df: pd.DataFrame, *, period) -> pd.DataFrame:
    '''
    Helper to handle-nonnumeric columns during aggregation.
    By default they just get omitted, which is annoying for error handlign and debugging
    '''
    def agg(s):
        # sum numeric, concat the rest
        if is_numeric_dtype(s.dtype):
            return s.sum()
        else:
            ss = s.dropna()
            if len(ss) == 0:
                return None
            else:
                # if s.name == 'duration':
                #     breakpoint()
                #     pass
                return '; '.join(ss.astype(str)) # todo \n?

    ds = df.resample(period)
    return ds.aggregate(func=agg)


def test_resample_sum():
    df = pd.DataFrame([
        dict(y=1   , s='a' ),
        dict(y=4   , s='c' ),
        dict(y=2   , s=None),
        dict(y=None, s='d' ),
        dict(y=None, s=None),
    ], index=pd.date_range('2000/01/01', periods=5, freq='T'))
    df = resample_sum(df, period='2T')
    # TODO not sure if the last should be 0 or None..
    assert list(df['y']) == [5, 2, 0]
    assert list(df['s']) == ['a; c', 'd', None]
