def scatter_matrix(df, *args, width=None, height=None, regression=True, **kwargs):
    import hvplot # type: ignore
    import holoviews as hv # type: ignore

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
        # GridMatrix is just a dict. nice!
        for k, plot in sm.items():
            xx, yy = k
            if xx == yy:
                # diagonal thing, e.g. histogram
                continue
            # TODO definitely test nan behaviour for scatter_matrix...

            dd = plot.data[[xx, yy]].dropna() # otherwise from_scatter fails
            # todo need to add various regression properties, like intercept, etc
            # TODO hopefuly this overlays correctly?? not sure about nans, again
            sm[k] = plot * hv.Slope.from_scatter(hv.Scatter((dd[xx], dd[yy]))).opts(color='red')
            # wow! * (same plot) vs + (different plots) is pretty clever!
            # also I like how multiplication doesn't commute so the 'first' plot wins the layout parameters

    # TODO dynamic resizing would be nice
    return sm


def _scatter_matrix_demo(**kwargs):
    # todo hmm, why it generates such crappy columns? e.g. just zeros and infs??
    # from hypothesis.extra.pandas import column, data_frames
    # dfs = data_frames([column('A', dtype=int), column('B', dtype=float)])
    # for _ in range(10):
    #     print(dfs.example())

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
