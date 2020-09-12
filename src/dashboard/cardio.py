from bokeh.layouts import column

from .core.bokeh import rolling, date_figure


def plot_running(df):
    df = df.set_index('start_time')

    rdf = df[df['sport'].str.contains('Running')]

    # TODO could be useful in spinning/elliptical as well?
    # but need to add manual data first
    rdf['speed_to_hr'] = df['speed_avg'] / df['heart_rate_avg']

    # todo I suppose it's threadmill?
    zero_speed = rdf['speed_avg'] < 0.5
    # FIXME settingswithcopywarning
    rdf.loc[zero_speed, 'error'] = 'zero speed, suspicious'


    from datetime import timedelta
    # todo probably don't really need it?... I guess it also really belongs to HPI?
    too_short = rdf['duration'] < timedelta(minutes=5)
    rdf.loc[too_short, 'error'] = 'too short, suspicious'


    # TODO for rolling; if plot is missing, generate automatically for easier interactive experience?
    #
    # TODO compare it with old running stuff and make sure all the differences are accounted for
    # TODO FIXME rolling doesn't work without setting the index
    # todo filter away stuff without speed? and show as errors perhaps
    r1 = rolling(df=rdf, x='start_time', y='speed_avg'     , avgs=['14D'])
    r1.figure.title.text = 'Running speed'
    r2 = rolling(df=rdf, x='start_time', y='heart_rate_avg', avgs=['14D'])
    r2.figure.title.text = 'Running HR'
    r3 = rolling(df=rdf, x='start_time', y='speed_to_hr'   , avgs=['14D']) # todo change to 30D?
    r3.figure.title.text = 'Running speed/HR (the more the better)'

    return column([
        r1.layout,
        r2.layout,
        r3.layout,
    ])


def plot_spinning(df):
    # TODO do it on the DF level?
    df = df.set_index('start_time')

    sdf = df[df['sport'].str.contains('Spinning')]

    # TODO no need to pass x if the index is timestamp?
    r = rolling(df=sdf, x='start_time', y='heart_rate_avg', avgs=['14D'])
    r.figure.title.text = 'Spinning HR'

    return r.layout


# TODO pay attention at warnings from the old dashboard
# todo 2019-05-23 -- single endomondo item error
def plot_cross_trainer(df):
    df = df.set_index('start_time')

    edf = df[df['sport'].str.contains('Cross training')]

    r = rolling(df=edf, x='start_time', y='heart_rate_avg', avgs=['14D'])
    r.figure.title.text = 'Cross trainer HR'
    # TODO combine with manually logged data and get power etc
   
    return r.layout
