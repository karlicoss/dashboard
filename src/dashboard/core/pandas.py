import logging
from typing import Union, Sequence, List

import pandas as pd

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
    return s.apply(lambda d: d.replace(tzinfo=None))
