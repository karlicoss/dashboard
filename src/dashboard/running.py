from dashboard.core.bokeh import rolling, date_figure

def plot_running(df):
    rdf = df[df['sport'].str.contains('Running')]

    # todo I suppose it's threadmill?
    zero_speed = rdf['speed_avg'] < 0.5
    # FIXME settingswithcopywarning
    rdf.loc[zero_speed, 'error'] = 'zero speed, suspicious'

    # TODO for rolling; if plot is missing, generate automatically for easier interactive experience?
    # p = date_figure()

    # TODO compare it with old running stuff and make sure all the differences are accounted for
    # TODO FIXME rolling doesn't work without setting the index
    rdf = rdf.set_index('start_time')
    # todo filter away stuff without speed? and show as errors perhaps
    r = rolling(x='start_time', y='speed_avg', df=rdf, avgs=[14])
    r.figure.legend.click_policy = 'hide'
    return r.layout
