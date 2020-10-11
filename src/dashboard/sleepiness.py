'''
Subjectiveness sleepiness, felt during the day
'''
from .core.bokeh import scatter_matrix, rolling
from .core.pandas import unlocalize, lag_df


def plot_sleepiness_vs_exercise():
    # from .data
    from datetime import timedelta

    from .data import cardio_dataframe as CDF
    from .data import sleepiness_dataframe as SDF

    c = CDF()
    c = c[c['error'].isna()] # TODO careful

    s = SDF()
    s = s[s['error'].isna()]

    s['sleepy'] = 1

    s['dt'] = unlocalize(s['dt'])
    s = s.set_index('dt').sort_index()


    c['dt'] = unlocalize(c['start_time'])
    c = c.set_index('dt').sort_index()

    mindt = min(s.index)
    c = c[c.index >= mindt] # clip till the time we started collecting it

    deltas = [timedelta(hours=h) for h in range(-200, 200)]
    ldf = lag_df(x=c['kcal'], y=s['sleepy'], deltas=deltas)

    # FIXME: need to set timedeltas on x axis
    # todo maybe rolling is a somewhat misleading name?
    return rolling(x='lag', y='value', df=ldf, avgs=[]).figure
    # we want to find out what predicts sleepiness.. so it's y
    # and kcal is x
