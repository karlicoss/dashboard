# todo move these to bokeh helpers specifically?

def scatter_matrix(df, *args, width=None, height=None, regression=True, **kwargs):
    import hvplot # type: ignore
    import holoviews as hv # type: ignore
    from bokeh.models import Label # type: ignore

    columns = df.columns
    # TODO might be useful to include/exclude specific cols (e.g. datetime) while keeping them in annotations
    # todo reuse plotly code from old dashboard?

    if 'c' not in kwargs:
        # NOTE: if we don't specify some color, hvplot.scatter_matrix ignores kwargs completely (see the code). TODO perhaps report a bug?
        df = df.copy()
        df['fake_color'] = 'fake_color'
        kwargs['c'] = 'fake_color'

    ## hvplot.scatter_matrix seems to ignore width/height params, so we make up for it
    extra_opts = []
    w1 = None if width  is None else width  // len(columns)
    h1 = None if height is None else height // len(columns)
    if h1 is not None or w1 is not None:
        extra_opts.append(hv.opts.Scatter  (frame_width=w1, frame_height=h1))
        extra_opts.append(hv.opts.Histogram(frame_width=w1, frame_height=h1))
    ##

    sm = hvplot.scatter_matrix(
        df,
        *args,
        **kwargs,
    ).opts(*extra_opts)


    if regression:
        # todo this would be need for plotly as well?
        import statsmodels.formula.api as smf # type: ignore

        # GridMatrix is just a dict. nice!
        for k, plot in sm.items():
            xx, yy = k
            if xx == yy:
                # diagonal thing, e.g. histogram
                continue
            # TODO definitely test nan behaviour for scatter_matrix...

            dd = plot.data[[xx, yy]].dropna() # otherwise from_scatter fails

            res = smf.ols(f"{yy} ~ {xx}", data=dd).fit()
            intercept = res.params['Intercept']
            slope = res.params[xx]
            r2 = res.rsquared

            # todo ugh. why is it so hard... I wonder if holoviews only makes it harder..
            # lbl = Label(x=70, y=70, x_units='screen', text='Some Stuff', render_mode='css',
            #     border_line_color='black', border_line_alpha=1.0,
            #     background_fill_color='white', background_fill_alpha=1.0)

            ## TODO crap. is it really the best way to figure out relative position??
            relx = 0.01
            rely = 0.1

            # todo highlight high enough R2?
            minx, maxx = min(dd[xx]), max(dd[xx])
            miny, maxy = min(dd[yy]), max(dd[yy])
            # todo font size dependent on width?? ugh.
            text = hv.Text(
                minx + (maxx - minx) * relx,
                miny + (maxy - miny) * rely,
                f"R2 = {r2:.4f}\n{yy} ~ {slope:.3f} {xx}",
                halign='left',
            )
            ##

            # todo need to add various regression properties, like intercept, etc
            # TODO hopefuly this overlays correctly?? not sure about nans, again
            sl = hv.Slope.from_scatter(hv.Scatter((dd[xx], dd[yy]))).opts(color='red')
            # just a sanity check.. not sure which one I should use?
            # sl2 = hv.Slope(slope, intercept).opts(color='green')
            # TODO ugh. title doesn't work??
            sm[k] = plot * sl * text

            # wow! * (same plot) vs + (different plots) is pretty clever!
            # also I like how multiplication doesn't commute so the 'first' plot wins the layout parameters

    # TODO dynamic resizing would be nice
    return sm
# todo plotly/sns also plotted some sort of confidence intervals? not sure if they are useful


def _scatter_matrix_demo(**kwargs):
    # todo hmm, why it generates such crappy columns? e.g. just zeros and infs??
    # from hypothesis.extra.pandas import column, data_frames
    # dfs = data_frames([column('A', dtype=int), column('B', dtype=float)])
    # for _ in range(10):
    #     print(dfs.example())
    #

    import numpy as np # type: ignore
    import pandas as pd # type: ignore
    df = pd.DataFrame([
        (4     , 25    ),
        (6     , 40    ),
        # nans just to mess with it
        (np.nan, 60    ),
        (   10 , 99.9  ),

        # reorder just to mess with it
        (1     , 2     ),
        (2     , 4     ),
        (3     , 9.5   ),
        (4     , np.nan),
        (4.5   , 20.0  ),
    ], columns=['a', 'b'])

    # TODO annotate with what's expected?

    return scatter_matrix(df, **kwargs)
