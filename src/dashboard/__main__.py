import logging
from pathlib import Path
from typing import Iterable, Optional

from .tabs import tabs, Tab

# I guess it kinda makes sense to dump each tab separately

def render_tab(*, tab: Tab, filename: Path):
    res = tab.plotter()

    from bokeh.io import save, output_file
    output_file(filename, title=tab.name, mode='inline', root_dir=None)
    # TODO a bit weird that it needs two function calls to save..
    save(res)


def run(to: Path, tab_name: Optional[str]=None, debug: bool=False) -> Iterable[Exception]:
    for tab in tabs():
        if isinstance(tab, Exception):
            # todo collect errors in a separate tab? or just 'dashboard.html'?
            yield tab
            continue

        if tab_name is not None and tab.name != tab_name:
            logging.info('skipping %s', tab.name)
            # todo error if no matches??
            continue

        logging.info('rendering %s', tab.name)
        fname = to / (tab.name + '.html')

        try:
            if debug:
                # todo optional dependency?
                from ipdb import launch_ipdb_on_exception # type: ignore
                ctx = launch_ipdb_on_exception
            else:
                from contextlib import nullcontext
                ctx = nullcontext
            with ctx():
                res = render_tab(tab=tab, filename=fname)
        except Exception as e:
            # TODO make it defensive? if there were any errors, backup old file, don't overwrite? dunno.
            logging.exception(e)

            import html
            import traceback
            tb = '</br>'.join(html.escape(l) for l in traceback.format_exception(Exception, e, e.__traceback__))
            fname.write_text(tb)

            yield e
            continue



def main():
    logging.basicConfig(level=logging.INFO)

    from argparse import ArgumentParser as P
    p = P()
    p.add_argument('--to', type=Path, required=True)
    p.add_argument('--tab', type=str, help='Plot specific tab (by default plots all)')
    p.add_argument('--debug', action='store_true', help='debug on exception')
    args = p.parse_args()

    # todo pass function names to render? seems easier than tab names? or either?
    errors = list(run(to=args.to, tab_name=args.tab, debug=args.debug))
    if len(errors) > 0:
        logging.error('Had %d errors while rendering', len(errors))
        for e in errors:
            logging.exception(e)
        import sys
        sys.exit(1)


if __name__ == '__main__':
    main()
