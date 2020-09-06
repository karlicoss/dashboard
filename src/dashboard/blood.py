from .core.pandas import set_group_hints, set_range_hints, Range
from .core.bokeh import plot_multiple


# todo wonder if it's possible to add multiple ranges? e.g. I could have LDL/HDL/trigs on the same plot
def plot_blood(df):
    # p = date_figure()
    # TODO fuck. seems that bokeh fails to plot if some data is interleaved with Nans
    # right, see https://github.com/bokeh/bokeh/issues/737
    # I guess, need a helper after all to handle it better

    # todo add 'normal' ranges somehow..
    # I guess they would/could also depend on the data providers?
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

    # todo perhaps I just shouldn't plot ranges on the 'combined' plots? only plot them on separate per-column ones
    df = set_range_hints(
        df,
        {
            # accordign to Thriva
            # 120-175: normal
            # 175-375: high
            # TODO unclear how to combine range hints and multiple plots??
            'vitamin_d': [
                Range(low=0 , high=25 , color='red'        ), # low
                Range(low=25, high=50 , color='yellow'     ), # 'insufficient
                Range(low=50, high=75 , color='greenyellow'), # 'sufficient'
                Range(low=75, high=120, color='green'      ), # 'optimal'
            ],

            'hdl': [
                Range(low=1, high=2.5), # 'optimal',
            ],
            'ldl': [
                Range(low=0, high=3.4), # 'normal'
            ],
            'triglycerides': [
                Range(low=0, high=1), # 'optimal'
                Range(low=1, high=2), # 'normal'
            ],
        }
    )


    # todo meh. wonder how to make it properly adjustable?
    # just move to config?
    return plot_multiple(df=df, columns=cols, frame_height=200)
