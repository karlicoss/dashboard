from datetime import date, timedelta
from itertools import cycle
import logging
from typing import Dict, Optional

from bokeh.layouts import gridplot, column
from bokeh.models import ColumnDataSource as CDS, Text, Title, Label
from bokeh.plotting import figure

import numpy as np
import pandas as pd


# TODO FIXME also handle errors?
# global error list + plotly like number of errors per plot?
def scatter_matrix(df, *args, width=None, height=None, regression=True, **kwargs):
    import hvplot
    import holoviews as hv
    hv.extension('bokeh')

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

    # TODO hmm. seems that it magically removing all non-numeric data?
    # unfortunately, this might mess with labels... wonder if I need my custom impl after all...
    # I guess need to look in hvplot.gridmatrix code... definitely add a visual test for that...
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


def test_scatter_matrix_demo() -> None:
    import numpy as np
    import pandas as pd
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

    # todo save perhaps??
    return scatter_matrix(df, width=500, height=500)


from bokeh.layouts import LayoutDOM
from bokeh.models import Plot
from bokeh.plotting import Figure
from typing import Sequence, List
from dataclasses import dataclass

from more_itertools import one

# NamedTuple is friendly towards overriding __iter__
@dataclass
class RollingResult:
    layout: LayoutDOM
    # todo switch to Sequence..
    plots: List[Plot]
    figures: List[Figure]

    def __iter__(self):
        return iter(self.plots)


    @property
    def figure(self):
        return one(self.figures)


# todo better name? also have similar function for plotly
def rolling(*, x: str, y: str, df, avgs=['7D', '30D'], legend_label=None, context: Optional[RollingResult]=None, **kwargs) -> RollingResult:
    if legend_label is None:
        legend_label = y

    # meh... don't think I like it
    # TODO def test this
    if context is None:
        ls = []
        plot = date_figure(df=df)
        ls.append(plot)

        ctx = RollingResult(
            layout=column(ls, sizing_mode='stretch_width'),
            plots=[],
            figures=[plot],
        )
    else:
        ctx = context

    plot = ctx.figure
    plots = ctx.plots
    layouts = ctx.layout.children

    # todo assert datetime index? test it too
    # todo although in theory it doens't have to be datetimes with the approprivate avgs??

    nan_x = df.index.isna()
    # FIXME display separately... but not sure where...
    dfxe = df.loc[ nan_x]
    df   = df.loc[~nan_x]
    if len(dfxe) > 0:
        # TODO think about a better location
        # todo hmm, not sure if Title is the best thing to use? but Label/Text didn't work from the first attempt

        # todo could even keep the 'value' erorrs and display below too.. but for now it's ok
        # ok, if it respected newlines, would be perfect
        # for now this is 'fine'...
        # TODO monospace font?
        # TODO just reuse the datatable??
        for line in dfxe.to_string().splitlines():
            title = Title(text=line, align='left', text_color='red')
            plot.add_layout(title, 'below')
        # TODO use html maybe?
        # https://stackoverflow.com/a/54132533/706389

    # todo warn if unsorted?
    df = df.sort_index()

    # TODO also error might be present where index is not nan
    nan_y = df[y].isnull() # todo vs isna??
    # TODO a bit ugly... think about this better
    if 'error' in df.columns:
        nan_y = nan_y | ~df['error'].isnull()

    dfye = df.loc[ nan_y]
    df   = df.loc[~nan_y]
    # filtering nans is necessary for rolling mean calculations
    # I guess errors aren't useful on avg plots anyway

    # TODO FIXME size needs to conform the plot (e.g. look at weight plot)
    if len(dfye) > 0:
        # ugh. couldn't easily figure out how to toggle this??
        # from bokeh.models import LabelSet
        # labels = LabelSet(
        #     source=CDS(dfye),
        #     x=x,
        #     y=max(df[y]) / 2, # TODO meh
        #     text='error',
        #     angle=3.14 / 2,
        #     text_color='red',
        # )
        # plot.add_layout(labels)

        plot.scatter(
            source=CDS(dfye),
            x=x,
            # TODO meh.. how to make the position absolute??
            y=df[y].quantile(0.8), # to display kinda on top, but not too high
            legend_label='errors',
            line_color='red',
            fill_color='yellow', # ??
            marker='circle_cross',
            size=10,
        )

        # TODO would be nice to highlight in table/plot
        # TODO maybe should display all points, highlight error ones as red (and it sorts anyway so easy to overview?)
        from bokeh.models.widgets import DataTable, DateFormatter, TableColumn
        # todo DataCube?? even more elaborate
        dfye = dfye.reset_index() # todo ugh. otherwise doesn't display the index at all?
        # TODO display datetime and timedeltas columns properly?
        # todo maybe display 'error' as the first col?
        errors_table = DataTable(
            source=CDS(dfye),
            columns=[TableColumn(field=c, title=c) for c in dfye.columns],
            # todo ugh. handle this properly, was too narrow on the sleep plots
            width=2000,
        )
        layouts.append(errors_table)

        # todo
        # >>> plot.circle([1,2,3], [4,5,6], name="temp")
        # >>> plot.select(name="temp")
        # [GlyphRenderer(id='399d53f5-73e9-44d9-9527-544b761c7705', ...)]
       
    plots.append(plot.scatter(x=x, y=y, source=CDS(df), legend_label=legend_label, **kwargs))
    for period in avgs:
        dfy = df[[y]]
        if 'datetime64' in str(dfy.index.dtype):
            # you're probably doing something wrong otherwise..
            assert str(period).endswith('D'), period
        dfa = dfy[dfy.index.notna()].rolling(period).mean()
        # TODO assert x in df?? or rolling wrt to x??

        # somehow plot.line works if 'x' is index? but df[x] doesnt..

        # todo different style by default? thicker line? not sure..
        plots.append(plot.line(x=x, y=y, source=CDS(dfa), legend_label=f'{legend_label} ({period} avg)', **kwargs))


    # ugh. hacky but does the trick. if too early, it complains that
    # 'Before legend properties can be set, you must add a Legend explicitly, or call a glyph method with a legend parameter set.'
    plot.legend.click_policy = 'hide'

    return ctx
    # return RollingResult(
    #     # todo maybe return orig layouts and let the parent wrap into column?
    #     layout=column(layouts, sizing_mode='stretch_width'),
    #     plots=plots, # todo rename to 'graphs'?
    #     figures=[plot],
    # )


# ugh. without date_figure it's actually showing unix timestamps on the x axis
# wonder if can make it less manual?
def date_figure(df=None, **kwargs):
    from bokeh.models import HoverTool

    if df is None:
        # just have at least some defaults..
        dtypes = {
            'date' : 'datetime64',
            'error': str,
        }
    else:
        dtypes = df.reset_index().dtypes.to_dict()

    tooltips   = []
    formatters = {}
    for c, t in dtypes.items():
        fmt = None
        tfmt = ''
        if 'datetime64' in str(t): # meh
            fmt = 'datetime'
            # todo %T only if it's actually datetime, not date? not sure though...
            tfmt = '{%F %a %T}'
        elif 'timedelta64' in str(t): # also meh
            fmt = 'datetime'
            # eh, I suppose ok for now. would be nice to reuse in the tables...
            tfmt = '{%H:%M}'
        if fmt is not None:
            formatters['@' + c] = fmt

        tooltips.append((c, f'@{c}' + tfmt))

    # see https://docs.bokeh.org/en/latest/docs/user_guide/tools.html#formatting-tooltip-fields
    # TODO: use html tooltip with templating
    # and https://docs.bokeh.org/en/latest/docs/reference/models/formatters.html#bokeh.models.formatters.DatetimeTickFormatter
    hover = HoverTool(
        tooltips=tooltips,
        formatters=formatters,
        # display a tooltip whenever the cursor is vertically in line with a glyph
        # TODO not sure I like this, it's a bit spammy
        mode='vline'
    )
    f = figure(x_axis_type='datetime', plot_width=2000, **kwargs)
    f.add_tools(hover)
    return f


# NOTE: this
# show(p1)
# show(p2)
# vs
# show(gridplot([[p1], [p2]]))
# the latter works better because it aligns stuff properly
#  otherwise impossible to notice js errors

def J(code):
    return f'''
try {{
    {code}
}} catch (e) {{
    alert("ERROR! " + String(e));
}}
'''


# note.. hmm, sems that they have to share a layout in order for JS callbacks to work??
def date_slider(p, *, dates=None, date_column='dt'):
    # todo a bit crap, but kinda works.. not sure what's the proper way?
    # maybe they aren't computed before show()??
    # p.x_range.on_change('start', lambda attr, old, new: print("Start", new))
    # p.x_range.on_change('end', lambda attr, old, new: print("End", new))

    if dates is None:
        graphs = p.renderers
        # todo autodetect by type instead of name?
        dts = np.concatenate([g.data_source.data[date_column] for g in graphs])
        # FFS... apparently no easier way
        sdate = pd.Timestamp(np.min(dts)).to_pydatetime()
        edate = pd.Timestamp(np.max(dts)).to_pydatetime()
    else:
        sdate = min(dates)
        edate = max(dates)
    # todo not sure if should use today?
    edate += timedelta(days=5)

    from bokeh.models.widgets import DateRangeSlider # type: ignore
    ds = DateRangeSlider(
        title="Date Range: ",
        start=sdate,
        end=edate,
        value=(sdate, edate),
        step=1,
    )
    from bokeh.models import CustomJS # type: ignore

    # TODO hmm. so, js won't be able to call into python in Jupyter...
    # see https://docs.bokeh.org/en/latest/docs/gallery/slider.html
    update_js = CustomJS(
        args=dict(ds=ds, xrange=p.x_range),
        code=J('''
    const [ll, rr] = ds.value;
    // didn't work??
    // xrange.set({"start": ll, "end": rr})
    xrange.start = ll;
    xrange.end   = rr;

    // todo hmm, turned out it wasn't necessary??
    // source.trigger('change');
    '''
    ))

    # todo add some quick selectors, e.g. last month, last year, etc like plotly
    ds.js_on_change('value', update_js)
    return ds


def plot_multiple(df, *, columns, **kwargs):
    # todo autodiscover columns somehow?
    # basically all except dates?

    # todo use multiindex for groups? not sure if possible
    # https://stackoverflow.com/questions/30791839/is-there-an-easy-way-to-group-columns-in-a-pandas-dataframe
    
    # todo make configurable
    from bokeh.palettes import Dark2_5 as palette # type: ignore

    from .pandas import read_group_hints, read_range_hints
    groups = read_group_hints(df)

    range_hints = read_range_hints(df)

    # todo think of a better name?..
    x_range = None

    # todo height??
    # todo for grouping, could simply take soft hints?
    # and if something is unknown, just warn and display on the plot
    plots = []
    for grp in groups:
        # todo add source to annotation?
        p = date_figure(x_range=x_range, **kwargs)

        # todo color rainbow??
        for f, color in zip(grp, cycle(palette)):
            # todo make this behaviour adjustable?
            fdf = df[df[f].notna()]

            # TODO rely on dt index? it can be non-unique so it should be fine...
            p.scatter(x='dt', y=f, source=CDS(data=fdf), color=color, legend_label=f)
            p.line   (x='dt', y=f, source=CDS(data=fdf), color=color, legend_label=f)

            # TODO axis labels
            
            # hmm it actually uses glucose level as an example
            # https://docs.bokeh.org/en/latest/docs/user_guide/annotations.html#box-annotations

            # TODO from bokeh.sampledata.glucose import data -- could use for demo/testing
            rhs = range_hints.get(f, [])
            # TODO if no color, just vary color + ???
            for rh in rhs:
                # right. annotation works, but wasn't sure how to make it toggable
                # from bokeh.models import BoxAnnotation # type: ignore
                # normal = BoxAnnotation(bottom=rh.low, top=rh.high, fill_alpha=0.1, fill_color=rh.color)
                # p.add_layout(normal)


                extras: Dict[str, Optional[str]] = dict(color=None)
                col = rh.color
                if col is None:
                    col = color
                    if len(rhs) > 1:
                        logging.warning("Multiple ranges for %s don't have colour, this will result in ranges overlapping: %s", f, rhs)
                        # at least make the separators visible
                        extras = dict(color='black', line_dash='dotted')

                # todo hide by default?
                # hmm, without left=, it plots at timestamp 0 =/
                p.hbar(
                    left =min(fdf['dt']),
                    right=max(fdf['dt']),
                    y=(rh.low + rh.high) / 2, height=rh.high - rh.low, # eh, this is awkward..
                    fill_color=col,
                    fill_alpha=0.1,
                    legend_label=f'{f} ranges',
                    **extras,
                )


        p.title.text = str(grp)
        if x_range is None:
            x_range = p.x_range

        p.legend.click_policy = 'hide'

        plots.append(p)

    return gridplot([[x] for x in plots])

# TODO use axis name to name the plot (at least by default?)
