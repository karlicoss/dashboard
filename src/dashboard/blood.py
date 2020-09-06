from .core.bokeh import plot_multiple, set_group_hints


# todo wonder if it's possible to add multiple ranges? e.g. I could have LDL/HDL/trigs on the same plot
def plot_blood(df):
    # p = date_figure()
    # TODO fuck. seems that bokeh fails to plot if some data is interleaved with Nans
    # right, see https://github.com/bokeh/bokeh/issues/737
    # I guess, need a helper after all to handle it better

    # todo add 'normal' ranges somehow..
    # perhaps via dataframe attributes as well? or datatypes (not sure how?)

    # todo display source on a tooltop
    cols = set(df.columns)
    cols = cols.difference({'dt', 'extra', 'source'})


    # todo add cholesterol (and ratios) as well?

    # would be nice to make it more dynamic... also
    df['trig_over_hdl'] = df['triglycerides'] / df['hdl']

    # TODO document this. it's a pretty nice way to decouple data and plotting
    # if anything is renamed, you still get a plot
    df = set_group_hints(
        df,
        [
            'vitamin_d',
            ['glucose', 'ketones'],
            ['ldl', 'hdl', 'triglycerides', 'trig_over_hdl'],
            # todo allow ignoring? maybe with a special marker?
        ]
    )



    # todo meh. wonder how to make it properly adjustable?
    # just move to config?
    return plot_multiple(df=df, columns=cols, frame_height=200)
