import numpy as np
import pandas as pd


def fourier(s: pd.Series) -> pd.Series:
    # TODO need to resample.. (fill with avgs?) warn about large gaps?
    ts = list(range(len(s)))
    # FIXME assert index is continuous? otherwise it's not properly sampled
    f = ts[1] - ts[0]

    vals = list(s)
    ft = np.abs(np.fft.rfft(vals))
    freqs = np.fft.rfftfreq(len(vals), f)
    mags = abs(ft)

    _periods = 1 / freqs
    # todo hmm. plotting with periods results in basically 'exponential' axis... not sure what to do
    return pd.Series(mags, index=freqs)
    # TODO strip away .iloc[1:]? it's always big


def periods(s: pd.Series, *, n: int = 3):
    from scipy.signal import find_peaks  # type: ignore[import-untyped]

    f = fourier(s)
    f.index = 1 / f.index
    pidx, _ = find_peaks(list(f))
    # todo yield instead?
    for _, p in sorted(((f.iloc[p], p) for p in pidx), reverse=True)[:n]:
        print(f'{p:5d} {f.index[p]:6.2f} {f.iloc[p]:7.2f}')


def deseasonalize(df):
    from statsmodels.tsa.seasonal import seasonal_decompose  # type: ignore[import-untyped]

    # TODO meh, not sure if should be here..
    df = df.resample('D').interpolate('linear')
    dec = seasonal_decompose(df)  # (can pass period=)
    # todo wonder which periods is it guessing..
    # TODO wonder how it calculates seasonal? also it's not catching yearly trends?
    # ddd = dec.seasonal + dec.trend + dec.resid
    return df - dec.seasonal


def test_periods():
    ts = np.arange(0, 1500, 1)
    vals = [
        60 + \
        10  * np.sin(6.29 / 365 * i) + \
        20  * np.sin(6.29 / 7   * i) + \
        5   * np.sin(6.29 / 28  * i)

        for i in ts
    ]  # fmt: skip
    s = pd.Series(vals, index=ts)
    periods(s)
    # TODO assert
