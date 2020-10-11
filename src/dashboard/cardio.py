from bokeh.layouts import column

from .core.bokeh import rolling, date_figure


def _plot_running(df):
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
# TODO would be cool to display all HR plots on the same page? not sure how to align them properly though


def plot_spinning(df):
    # TODO do it on the DF level?
    df = df.set_index('start_time')

    sdf = df[df['sport'].str.contains('Spinning')]

    # TODO no need to pass x if the index is timestamp?
    r = rolling(df=sdf, x='start_time', y='heart_rate_avg', avgs=['14D'])
    r.figure.title.text = 'Spinning HR'

    return r.layout
# TODO merge in manual descriptions, attach interval information


# TODO pay attention at warnings from the old dashboard
# todo 2019-05-23 -- single endomondo item error
def plot_cross_trainer(df):
    df = df.set_index('start_time')

    # HPI: generally, make sure all types are explicitly numeric/dateish apart from the exceptions?
    # check with a decorator or something??
    df['power_to_hr'] = df['power_avg'] / df['heart_rate_avg']

    # TODO 14D?
    r1 = rolling(df=df, x='start_time', y='heart_rate_avg', avgs=['7D'])
    r1.figure.title.text = 'Cross trainer HR'
    r2 = rolling(df=df, x='start_time', y='power_avg'     , avgs=['7D'])
    r2.figure.title.text = 'Cross trainer power'
    r3 = rolling(df=df, x='start_time', y='power_to_hr'   , avgs=['7D'])
    r3.figure.title.text = 'Cross trainder power to HR (the more the better)'

    return column([
        r1.layout,
        r2.layout,
        r3.layout,
    ])

# TODO fill distance for treadmill from manual pictures?

# TODO for data filtering -- would be nice to have some heavy, reasonable preparation in python
# but then have a jsy interface to manipulate and do this vvv kind of filtering
# and if it was preserved across the sessions..
# TODO plot with all cardio exercise? not sure if would make much sense. but a table probable would..
# TODO rolling: check that columns types are numeric? otherwise get weird errors


# todo display breakdown by sport as well?
def plot_cardio_volume(df):
    # todo not sure ... should it always copy??
    df = df.copy()
    df = df.set_index('start_time')

    # todo not sure if this belongs to HPI or here??

    # TODO: actually use heartbeats as proxy? and remove kcals??
    # see https://beepb00p.xyz/heartbeats_vs_kcals.html
    df['volume'] = df['kcal']

    # assume it's zero on non-cardio days
    # TODO need to take walking etc into the account... infer from location data?
    # FIXME need to handle non-numeric fields carefully? at least warn they they would be dropped..
    # def test this too
    df = df.resample('D').sum()

    r = rolling(df=df, x='start_time', y='volume', avgs=['7D', '30D'])
    [g, g7, g30] = r
    g7 .glyph.line_dash = 'dashed'
    g30.glyph.line_width = 2

    f = r.figure
    f.title.text = 'Cardio exercise volume'
    f.legend.orientation = 'horizontal'
    f.legend.location = 'top_left'

    return r.layout
# note: old dashboard -- ok, plotting just endomondo stuff with old dashboard using kcal as volume proxy, matches very closely
# TODO would be interesting to add BMR as a third plot? or just add to total somhow..


def plot_running():
    from .data import endomondo_dataframe as DF
    return _plot_running(DF())


def plot_running_fake():
    from .data import fake_endomondo
    with fake_endomondo(count=100):
        return plot_running()


from .core.tests import make_test
test_running = make_test(plot_running_fake)
