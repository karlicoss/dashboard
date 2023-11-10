from datetime import date, timedelta, datetime
import html
from itertools import cycle, chain
import logging
from typing import Dict, Optional, Sequence, Union, Optional
import warnings

from bokeh.layouts import gridplot, column
from bokeh.models import ColumnDataSource as CDS

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype


# TODO FIXME also handle errors?
# global error list + plotly like number of errors per plot?
def scatter_matrix(
        df,
        *,
        xs: Optional[Sequence[str]]=None, ys: Optional[Sequence[str]]=None,
        width=None, height=None,
        regression=True,
        **kwargs,
):
    assert len(df) > 0, 'TODO handle this'

    # FIXME handle empty df
    source = CDS(df)
    # TODO what about non-numeric stuff?

    xs = df.columns if xs is None else xs
    ys = df.columns if ys is None else ys
    ys = list(reversed(ys)) # reorder to move meaningful stuff to the top left corner

    isnum = lambda c: is_numeric_dtype(df.dtypes[c])
    # reorder so non-numeric is in the back
    # todo mode to drop non-numeric? not sure.. definitely can drop 'error' and datetimish?
    xs = list(sorted(xs, key=isnum, reverse=True))
    ys = list(sorted(ys, key=isnum, reverse=True))

    # TODO not sure I wanna reuse axis?
    def make(xc: str, yc: str):
        p = figure(df=df)
        diag = xc == yc # todo handle properly
        # TODO not sure if I even want them... move to the very end?
        if isnum(xc) and isnum(yc):
            p.scatter(x=xc, y=yc, source=source, size=3)
        else:
            # TODO ugh, doesn't want to show the label without any points??
            # p.circle(x=0.0, y=0.0)
            # FIXME how to make sure text fits into the plot??
            add_text(
                p,
                x=0.0, y=0.0,
                text='Not numeric',
                text_color='red',
            )
        p.xaxis.axis_label = xc
        p.yaxis.axis_label = yc
        return p

    grid = [[make(xc=x, yc=y) for x in xs] for y in ys]
    from bokeh.layouts import gridplot
    w1 = None if width  is None else width  // min(len(xs), len(ys))
    h1 = None if height is None else height // min(len(xs), len(ys))
    grid_res = gridplot(grid, width=w1, height=h1)

    # TODO might be useful to include/exclude specific cols (e.g. datetime) while keeping them in annotations

    # TODO add the presence of the grid to the 'visual tests'
    # but if I swith it to raw bokeh -- it has Grid class.. might need to mess with
    # also maybe add extra axis under each plot in the grid? easier for a huge matrix of plots
    # some code in old dashboard
    if not regression:
        return grid_res

    # todo this would be need for plotly as well?
    import statsmodels.formula.api as smf  # type: ignore[import-untyped]

    for plot in chain.from_iterable(grid):
        gs = plot.renderers
        if len(gs) == 0:
            # must be non-numeric? meh though
            continue
        [g] = gs
        xx = g.glyph.x
        yy = g.glyph.y

        if xx == yy:
            # diagonal thing, e.g. histogram. compute some stats??
            continue

        # FIXME proper error handling, display number of dropped items?
        df = df.replace([np.inf, -np.inf], np.nan)  # FIXME meh. only happens during test?
        dd = df[[xx, yy]].dropna()  # otherwise from_scatter fails
        # todo would be nice to display stats on the number of points dropped


        udd = dd.drop_duplicates()
        if len(udd) <= 1:
            # can't perform a reasonable regression then
            add_text(
                plot,
                x=0.0,
                y=0.0,
                text='ERROR: no points to correlate',
                text_color='red',
            )
            continue


        res = smf.ols(f"{yy} ~ {xx}", data=dd).fit()
        intercept = res.params['Intercept']
        slope = res.params[xx]
        r2 = res.rsquared

        ## TODO crap. is it really the best way to figure out relative position??
        relx = 0.01
        rely = 0.1

        # todo highlight high enough R2?
        minx, maxx = min(dd[xx]), max(dd[xx])
        miny, maxy = min(dd[yy]), max(dd[yy])
        # todo font size dependent on width?? ugh.
        txt = f'R2 = {r2:.4f}\nY ~ {slope:.3f} X'

        # todo need to add various regression properties, like intercept, etc
        # TODO hopefuly this overlays correctly?? not sure about nans, again
        from bokeh.models import Slope  # type: ignore[attr-defined]  # works in runtime, seems like annotations issue?
        sl = Slope(gradient=slope, y_intercept=intercept, line_color='green', line_width=3)
        plot.add_layout(sl)
        add_text(
            plot,
            text=txt,
            x=minx + (maxx - minx) * relx,
            y=miny + (maxy - miny) * rely,
            text_color=g.glyph.line_color,
        )


    # TODO dynamic resizing would be nice
    return grid_res
# todo plotly/sns also plotted some sort of confidence intervals? not sure if they are useful

def add_text(plot, *, text: str, **kwargs):
    from bokeh.models import Text
    # ugh. for fuck's sake, Label doesn't support multiline... https://github.com/bokeh/bokeh/issues/7317
    # and glyphs always want a data source
    textsrc = CDS({'text': [text]})
    kwargs['text'] = 'text'
    glyph = Text(**kwargs)
    plot.add_glyph(textsrc, glyph)


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
from bokeh.plotting import figure as Figure  # FIXME
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


# ok, so multiple cases
#    x | y | err | res
# 1. N   *   *   | error table
# 2. Y   N   N   | set err  , goto YNY
# 3. Y   N   Y   | plot (fake y)  , error table
# 4. Y   Y   N   | plot                        ,          contribute to the avg
# 5. Y   Y   Y   | plot, highlight, error table, does NOT contribute to the avg
# test for it, also add to docs.
# this should def be common with plotly

# None is treated as 'omit' the scatter plot
# todo not sure about that though... maybe better to control on the call sites?
Avg = Optional[Union[str, int]]

# todo better name? also have similar function for plotly
def rolling(*, x: str, y: str, df, avgs: Sequence[Avg]=['7D', '30D'], legend_label=None, context: Optional[RollingResult]=None, **kwargs) -> RollingResult:
    # TODO maybe use a special logging handler, so everything logged with warning level gets displayed?
    errors = []

    # todo ugh. the same HPI check would be nice..
    tzs = set(df.index.map(lambda x: getattr(x, 'tzinfo', None))) # meh
    if len(tzs) > 1:
        errors.append(f'WARNING: a mixture of timezones: {tzs}. You might want to unlocalize() them first.')
    elif len(tzs) == 1:
        [_tz] = tzs
        if _tz is not None:
            # todo not really sure about that.. maybe it's okay, although UTC might be wrong as well
            errors.append(f'WARNING: detected timezone: {_tz}. You might want to unlocalize() first.')

    # todo should copy df first??
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

    has_x = df.index.notna()
    has_y = df[y].notna()
    err   = df['error'].notna() if 'error' in df.columns else df.index == 'how_to_make_empty_index?'
    # ^^^ todo a bit ugly... think about this better

    for_table = ~has_x # case 1 is handled

    # case 2: set proper error for ones that don't have y
    df.loc[has_x & ~has_y & ~err, 'error'] = f'{y} is nan/null'
    # now case 2 and 3 are the same

    # case 3
    case_3 = has_x & ~has_y
    for_table |= case_3
    for_marks  = case_3

    # case 4, 5
    ok = has_x & has_y
    case_4 = ok & err
    for_table |= case_4
    for_warn   = case_4

    dfm = df.loc[for_marks]
    dfe = df.loc[for_table]
    dfw = df.loc[for_warn]
    df  = df.loc[ok]
    if len(dfm) > 0:
        # todo meh.. how to make the position absolute??
        some_y = df[y].quantile(0.8) # to display kinda on top, but not too high
        if np.isnan(some_y):
            # otherwise fails during JSON serialization
            some_y = 0.0
        plot.scatter(
            source=CDS(dfm),
            x=x,
            y=some_y,
            legend_label='errors',
            line_color='red',
            fill_color='yellow', # ??
            marker='circle_cross',
            size=10,
        )

    if len(dfe) > 0:
        errors.append(f'Also encountered {len(dfe)} errors:')

    from bokeh.models.widgets.markups import Div
    # first a summary for the most important warnings/errors
    # todo append later stuff as well, there are some warnings during means
    for e in errors:
        layouts.append(Div(
            text=html.escape(e),
            styles={'color': 'red', 'font-weight': 'strong'},
        ))

    if len(dfe) > 0:
        # todo could even keep the 'value' erorrs and display below too.. but for now it's ok
        # ok, if it respected newlines, would be perfect
        # for now this is 'fine'...

        # todo maybe should display all points, highlight error ones as red (and it sorts anyway so easy to overview?)
        # todo would be nice to highlight the corresponding points in table/plot
        from bokeh.models.widgets import DataTable, DateFormatter, TableColumn
        from bokeh.models.widgets.tables import DateFormatter, NumberFormatter, HTMLTemplateFormatter
        # didn't work at all??
        # from bokeh.models.widgets.tables import ScientificFormatter

        # todo DataCube?? even more elaborate
        dfe = dfe.reset_index() # todo ugh. otherwise doesn't display the index at all?
        dfe = dfe.sort_values(by=x)

        # todo maybe display 'error' as the first col?
        datefmt = DateFormatter(format="%Y-%m-%d")
        # todo speed_avg could have less digits (guess by the dispersion or something??)

        # TODO horrible, but js bits of bokeh compute some complete bullhit for column widths
        # todo set monospace font??
        one_char = 10 # pixels
        def datatable_columns(df):
            for c, t in df.dtypes.items():
                formatter = None

                # TODO also use col name.. then won't have to handle nans!
                width = 15 # in characters
                # for fixed width types, we can have something kind of reasonable
                if str(t).startswith('float'):
                    l = df[c].dropna().astype(str).str.len().max()
                    width = 4 if np.isnan(l) else l

                if str(t).startswith('datetime'):
                    formatter = DateFormatter(format='%Y%m%d %H%M%S %Z', nan_format='Nan')
                    width = 15
                elif str(t).startswith('timedelta'):
                    # TODO warn if df contains stuff with duration >1D?
                    # without nan_format, it results in NaN:Nan:Nan
                    formatter = DateFormatter(format='%H:%M:%S', nan_format='Nan')
                    width = 8

                # if c == 'error':
                #     # meh, but the only easy way to limit and ellipsize it I found
                #     # aaand it still computes width in some weird way, ends up taking too much space
                #     formatter = HTMLTemplateFormatter(template='<div style="text-overflow: ellipsis; overflow: hidden; width: 60ch;"><%= value %></div>')

                tc = TableColumn(
                    field=c,
                    title=c,
                    **({} if formatter is None else dict(formatter=formatter)),
                    width=width * one_char,
                )
                yield tc

        # TODO hmm, if we reuse the data source, editing & selection might work?
        errors_table = DataTable(
            source=CDS(dfe),
            columns=list(datatable_columns(dfe)),
            # todo ugh. handle this properly, was too narrow on the sleep plots
            editable=True,

            width=2000,

            # default ends up in trimmed table content
            autosize_mode='none',

            # this might overstretch the parent...
            # autosize_mode='fit_viewport',

            # this just makes it respect the parent width
            # width_policy='fit',
        )
        layouts.append(errors_table)

        # todo
        # >>> plot.circle([1,2,3], [4,5,6], name="temp")
        # >>> plot.select(name="temp")
        # [GlyphRenderer(id='399d53f5-73e9-44d9-9527-544b761c7705', ...)]

    if len(dfw) > 0:
        plot.circle(source=CDS(dfw), x=x, y=y, legend_label='warnings', size=20, color='yellow')
   
    # todo warn if unsorted?
    df = df.sort_index()

    if len(df) == 0:
        # add a fake point, so at least plotting doesn't fail...
        df = pd.DataFrame([{
            x: datetime(year=2000, month=1, day=1),
            y: 0.0,
        }]).set_index(x)
        avgs = ['3D' for _ in avgs]
        # FIXME need to add this to errors as well, or at least title..
        # TODO need to add a better placholder, timestamp 0 really messes things up
        warnings.warn(f'No data points for {df}, empty plot!')

    if None not in avgs:
        plots.append(plot.scatter(x=x, y=y, source=CDS(df), legend_label=legend_label, **kwargs))  # type: ignore[arg-type]
   
    # only stuff without errors/warnings participates in the avg computation
    if 'error' in df.columns: # meh
        df = df[df['error'].isna()]
    for period in [a for a in avgs if a is not None]:
        dfy = df[[y]]
        if str(dfy.index.dtype) == 'object':
            logging.error(f"{dfy.dtypes}: index type is 'object'. You're likely doing something wrong")
        if 'datetime64' in str(dfy.index.dtype):
            # you're probably doing something wrong otherwise..
            # todo warn too?
            # check it's a valid period
            pd.to_timedelta(period)
        # TODO how to fill the missing values??
        # a sequence of consts would be a good test for it
        # todo why would index be na at this point? probably impossible?
        dfa = dfy[dfy.index.notna()].rolling(period).mean()
        # TODO assert x in df?? or rolling wrt to x??

        # somehow plot.line works if 'x' is index? but df[x] doesnt..

        # todo different style by default? thicker line? not sure..
        plots.append(plot.line(x=x, y=y, source=CDS(dfa), legend_label=f'{legend_label} ({period} avg)', **kwargs))

    plot.title.text = f'x: {x}, y: {y}'  # type: ignore[attr-defined]
    # TODO axis labels instead?
    return ctx
    # return RollingResult(
    #     # todo maybe return orig layouts and let the parent wrap into column?
    #     layout=column(layouts, sizing_mode='stretch_width'),
    #     plots=plots, # todo rename to 'graphs'?
    #     figures=[plot],
    # )

from bokeh.models import CustomJSHover
def figure(df=None, **kwargs) -> Figure:
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
        tfmt = '@' + c
        if df is None:
            dateish = 'datetime64' in str(t)
        else:
            # this is more reliable, works if there is a mix of timestamps..
            s = df.reset_index()[c].dropna()
            dateish = len(s) > 0 and s.apply(lambda x: isinstance(x, (pd.Timestamp, datetime))).all()
        # TODO add to tests?
        if dateish:
            fmt = 'datetime'
            # todo %T only if it's actually datetime, not date? not sure though...
            tfmt += '{%F %a %T}'
        elif 'timedelta64' in str(t):  # also meh
            fmt = CustomJSHover(code='const tick = value; ' + hhmm_formatter(unit=t))  # type: ignore[assignment]
            tfmt += '{custom}'
            # eh, I suppose ok for now. would be nice to reuse in the tables...
        elif c == 'error':
            # FIXME ugh. safe here is potentially dangerous... need to figure out how to do this
            tfmt = '<pre>@error{safe}</pre>'
        if fmt is not None:
            formatters['@' + c] = fmt

        tooltips.append((c, tfmt))
    # TODO very annoying, seems that if one of the tooltips is broken, nothing works at all?? need defensive tooltips..

    # see https://docs.bokeh.org/en/latest/docs/user_guide/tools.html#formatting-tooltip-fields
    # TODO: use html tooltip with templating
    # and https://docs.bokeh.org/en/latest/docs/reference/models/formatters.html#bokeh.models.formatters.DatetimeTickFormatter
    from bokeh.models import HoverTool
    hover = HoverTool(
        tooltips=tooltips,
        formatters=formatters,
        # display a tooltip whenever the cursor is vertically in line with a glyph
        # TODO not sure I like this, it's a bit spammy
        mode='vline'
    )
    from bokeh.plotting import figure as F
    # TODO this kinda expands it to fullscreen
    # ugh would be nice to automatically expand to fullscreen?
    kw = {'width': 2000}
    kw.update(**kwargs)
    f = F(**kw)
    # ugh. would be nice if add_tools returned self..
    f.add_tools(hover)
    return f


# not sure if it's that useful.. for a single parameter.
def date_figure(df=None, **kwargs) -> Figure:
    # ugh. without date_figure it's actually showing unix timestamps on the x axis
    # wonder if can make it less manual?
    kw = dict(x_axis_type='datetime')
    kw.update(**kwargs)
    return figure(df=df, **kw)


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

    from bokeh.models.widgets import DateRangeSlider
    ds = DateRangeSlider(
        title="Date Range: ",
        start=sdate,
        end=edate,
        value=(sdate, edate),
        step=1,
    )
    from bokeh.models import CustomJS

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
    from bokeh.palettes import Dark2_5 as palette

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
        # todo rely on kwargs for date x axis?
        p = date_figure(**({} if x_range is None else dict(x_range=x_range)), **kwargs)

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


        p.title.text = str(grp)  # type: ignore[attr-defined]  # this works, but mypy complains..
        if x_range is None:
            x_range = p.x_range

        plots.append(p)

    return gridplot([[x] for x in plots])

# TODO use axis name to name the plot (at least by default?)


def set_hhmm_axis(axis, *, mint: int, maxt: int, period: int=30) -> None:
    from bokeh.models import FixedTicker
    # FIXME infer mint/maxt
    ticks = list(range(mint, maxt, period))
    axis.ticker = FixedTicker(ticks=ticks)
    from bokeh.models import CustomJSTickFormatter
    axis.formatter = CustomJSTickFormatter(code=hhmm_formatter(unit=int))


# TODO use J for defensive js?
def hhmm_formatter(unit):
    if unit == int:
        xx = 'var mins = tick'
    elif str(unit) == 'timedelta64[ns]':
        xx = 'var mins = Math.floor(tick / 10 ** 3 / 60)' # eh why 10^3 works if it's nanos??
    else:
        raise RuntimeError(f'Unhandled: {unit}')

    return xx + """
        var sign = ''
        if (mins < 0) {
            sign = '-'
            mins = -mins
        }
        var days = ''
        var hh = Math.floor(mins / 60).toString()
        if (hh > 24) {
            days = Math.floor(hh / 24).toString() + 'd '
            hh = hh % 24
        }
        var mm = (mins % 60).toString()
        if (hh.length == 1) hh = "0" + hh
        if (mm.length == 1) mm = "0" + mm
        var parts = []
        parts.push(hh)
        parts.push(mm)
        return sign + days + parts.join(':')
    """


def guess_range(plot, *, axis: str):
    assert axis in {'x', 'y'}, axis
    mins = []
    maxs = []
    # todo extract helper to guess miny, maxy?
    graphs = plot.renderers
    for g in graphs:
        glyph = g.glyph
        name = getattr(glyph, axis, None)
        if name is None:
            if axis == 'y':
                # TODO assumes bar plot.. careful
                minname, maxname = glyph.bottom, glyph.top
            else:
                minname, maxname = glyph.left  , glyph.right
        else:
            minname, maxname = name, name
        # note: name was qual to 447.0 at some point (sleep plot). no idea what it means..
        # TODO nan might be the wrong type for datetime etc.
        minvals = g.data_source.data.get(minname, [np.nan])
        maxvals = g.data_source.data.get(maxname, [np.nan])
        mins.append(np.nanmin(minvals))
        maxs.append(np.nanmax(maxvals))
    if len(mins) == 0:
        mins = [np.nan]
    if len(maxs) == 0:
        maxs = [np.nan]
    mn = np.nanmin(mins)
    mx = np.nanmax(maxs)
    if np.isnan(mn):
        mn = 100.0 # TODO might not be numeric..
    if np.isnan(mx):
        mx = 0.0
    # todo not sure what's a good value to fallback?
    return (mn, mx)
