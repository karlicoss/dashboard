from datetime import datetime, date, timedelta
from itertools import islice
from typing import Tuple

import math
# https://wiki.openstreetmap.org/wiki/Mercator#Python_implementation
# ugh https://gis.stackexchange.com/a/156046 this one works fine??
def merc(lat: float, lon: float) -> Tuple[float, float]:
    eps = 0.000001
    if abs(lon) < eps:
        # TODO meh. at least take sign into the account...
        lon = eps

    r_major = 6378137.000
    x = r_major * math.radians(lon)
    scale = x/lon
    y = 180.0/math.pi * math.log(math.tan(math.pi/4.0 + lat * (math.pi/180.0)/2.0)) * scale
    return (x, y)

import pandas as pd # type: ignore

from my.location import iter_locations

from .data import all_locs

# todo might need to lru_cache so reloading works

from bokeh.models import ColumnDataSource as CDS # type: ignore
from bokeh.plotting import figure, show # type: ignore
# https://stackoverflow.com/questions/50680820/bokeh-openstreetmap-tile-not-visible-in-all-browsers
from bokeh.tile_providers import OSM, get_provider # type: ignore

# TODO wonder if it's possible to cache the tiles?
tile_provider = get_provider(OSM)


def plot(day: str, df):
#    from bokeh.io import output_notebook
#     output_notebook()
    # mx = []
    # my = []
    # for lat, lon in zip(df['lat'], df['lon']):
    #     (mmx, mmy) = merc(lat, lon)
    #     mx.append(mmx)
    #     my.append(mmy)

    df = pd.DataFrame(
        (merc(lat, lon) for _, (lat, lon) in df[['lat', 'lon']].iterrows()),
        columns=['mlon', 'mlat'],
        index=df.index,
    )
    # todo err... swap lat and lon?
    # df['mlon'] = mx
    # df['mlat'] = my

    # range bounds supplied in web mercator coordinates
    # p = figure(x_range=(-2000000, 6000000), y_range=(-1000000, 7000000),

    # todo set some reasonable minimum span? otherwise if there is no movement, almost nothing is displayed
    x_range = min(df['mlon']) - 100, max(df['mlon']) + 100
    y_range = min(df['mlat']) - 100, max(df['mlat']) + 100

    # print(x_range, y_range)
    # print(max(df['mlon']), min(df['mlon']))

    # TODO determine range from data?
    p = figure(
        title='map',
        x_axis_type='mercator',
        y_axis_type='mercator',
        # todo autodetect?
        # todo hmm, if I fix width, sometimes rendering fails? 20171118
        # plot_width =2500,
        # plot_height=1400,
        x_range=x_range,
        y_range=y_range,
    )
    p.add_tile(tile_provider)

    p.circle(x='mlon', y='mlat', size=10, fill_color='blue', fill_alpha=0.8, source=CDS(df))

    # I guess mimicking the same interface as google maps is ok? e.g. sidebar with points and time on the left and highlight them (maybe with different colors depending on whether they are in the future or in the past)

    #save to html file
    # output_file("file.html")
    # save(plot)

    return p




# set limit to finite value to speed up
def plot_all(limit=None):
    from bokeh.io import export_png, export_svgs, save
    # todo add min/max date?
    # todo multiple threads?

    # todo extract this mock data into HPI
    # use some python library to generate it
    real = True
    if real:
        locs = all_locs()
        idf = pd.DataFrame(islice((l._asdict() for l in locs), 0, limit))
    else:
        idf = pd.DataFrame([{
            'dt': datetime.strptime('20200101', '%Y%m%d') + timedelta(minutes=30 * x),
            'lat': max((0.01 * x) % 90, 0.1),
            'lon': max((0.01 * x) % 90, 0.1),
        } for x in range(1, 1000)])

    df = idf.set_index('dt')

    # todo make defensive, collect errors
    def process(day_and_grp):
        day, grp = day_and_grp
        # todo uhoh. chromedriver might die?
        days = day.strftime('%Y%m%d')
        p = plot(day=days, df=grp)

        fname = f'output/{days}.png'
        print(f'saving {fname}')
        if True:
            export_png (p, filename=fname)
        else:
            # hmm, this doesn't produce the background (map). but faster to dump?
            p.output_backend = 'svg'
            export_svgs(p, filename=fname)

    inputs = [(day, grp) for day, grp in df.groupby(lambda x: x.date())]

    # todo ugh. pretty sure it's resulting in race conditions... (probably because of shared chromedriver?) need to test it properly
    from concurrent.futures import ThreadPoolExecutor as Pool
    # todo and process pool executor just gets stuck?


    parallel = False

    if parallel:
        with Pool() as pool:
            for _ in pool.map(process, inputs):
                pass
    else:
        for _ in map(process, inputs):
            pass

    # [(key, grp) for key, grp in df[:10].set_index('dt')
    # for day in [
    #         '20171116',
    #         '20171117',
    #         '20171118',
    #         '20171119',
    # ]:
    #     plot(day)
    # date_ = datetime.strptime(day, '%Y%m%d').date()
    # points = [l for l in locs if l.dt.date() == date_]
