#!/usr/bin/env python3
# TODO later, move inside dashboard package?
from pathlib import Path


from bokeh.layouts import column
from bokeh.models import Button
from bokeh.palettes import RdYlBu3
from bokeh.plotting import figure, curdoc

# TODO would be nice to autoreload?


def bokeh_main():
    from random import random
    # create a plot and style its properties
    p = figure(x_range=(0, 100), y_range=(0, 100), toolbar_location=None)
    p.border_fill_color = 'black'
    p.background_fill_color = 'black'
    p.outline_line_color = None
    p.grid.grid_line_color = None

    # add a text renderer to our plot (no data yet)
    r = p.text(x=[], y=[], text=[], text_color=[], text_font_size="26px",
            text_baseline="middle", text_align="center")

    i = 0

    ds = r.data_source

    # create a callback that will add a number in a random location
    def callback():
        nonlocal i

        # BEST PRACTICE --- update .data in one step with a new dict
        new_data = dict()
        new_data['x'] = ds.data['x'] + [random()*70 + 15]
        new_data['y'] = ds.data['y'] + [random()*70 + 15]
        new_data['text_color'] = ds.data['text_color'] + [RdYlBu3[i%3]]
        new_data['text'] = ds.data['text'] + [str(i)]
        ds.data = new_data

        i = i + 1

    # add a button widget and configure with the call back
    button = Button(label="Press Me")
    button.on_click(callback)

    # put the button and plot in a layout and add to the document
    curdoc().add_root(column(button, p))


# todo autogenerate all plot tabs? maybe based on annotations?
def bokeh_main_2():
    import sys
    src = Path(__file__).absolute().parent / 'src'
    sys.path.insert(0, str(src))

    from bokeh.layouts import layout # type: ignore
    from bokeh.models.widgets import Tabs, Panel # type: ignore
    from bokeh.plotting import figure # type: ignore

    from dashboard.core.bokeh import test_scatter_matrix
    import holoviews as hv
    f1 = hv.render(test_scatter_matrix())

    f2 = figure()
    f2.circle([0,0,2],[4,-1,1])

    # todo need something more lazy?
    from dashboard.data import emfit_dataframe
    from dashboard.sleep import plot_sleep
    # TODO would be cool to display logs in the frontend and also currently evaluated function?
    # although pehaps it's easier to just always keep logs open?
    # sp = plot_sleep(df=emfit_dataframe())


    from bokeh.models.widgets import DateRangeSlider # type: ignore
    from datetime import date
    drs = DateRangeSlider(
        title="Date Range: ",
        start=date(2017, 1, 1),
        end=date.today(),
        value=(date(2017, 9, 7), date(2017, 10, 15)),
        step=1,
    )

    def update(attr, old, new):
        print(attr, old, new)

    from bokeh.models import CustomJS # type: ignore
    # todo see https://docs.bokeh.org/en/latest/docs/gallery/slider.html
    update_js = CustomJS(
        args=dict(drs=drs),
        code='''
console.log("HIIII");
'''
    )

    drs.on_change('value', update)
    drs.js_on_change('value', update_js)

    l1 = layout([[f1, drs]], sizing_mode='fixed')
    l2 = layout([[f2]], sizing_mode='fixed')
    tabs = Tabs(tabs=[
        Panel(child=l1            , title='This is Tab 1'  ),
        Panel(child=l2            , title='This is Tab 2'  ),
        # Panel(child=layout([[sp]]), title='Sleep dataframe'),
    ])

    curdoc().add_root(tabs)


def main():
    import argparse
    p = argparse.ArgumentParser()
    args = p.parse_args()

    # todo pass all python code to --dev? not sure

    import os
    # todo cwd?
    os.execlp(
        'bokeh',
        'bokeh', 'serve', str(Path(__file__).absolute()),
        '--dev',
        # todo pass rest?
    )


if __name__ == '__main__':
    main()
elif __name__.startswith('bokeh'):
    bokeh_main_2()
else:
    raise RuntimeError(__name__)

# TODO visualize raw plots on a separate tab/tabs? basically discover all dataframes and infer what to render?
# TODO https://github.com/bokeh/bokeh/blob/master/examples/app/sliders.py
