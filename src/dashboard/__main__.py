import logging
from pathlib import Path
from typing import Iterable

from .tabs import tabs, Tab

# I guess it kinda makes sense to dump each tab separately

def render_tab(*, tab: Tab, filename: Path):
    res = tab.plotter()

    from bokeh.io import save, output_file
    output_file(filename, title=tab.name, mode='inline', root_dir=None)
    # TODO a bit weird that it needs two function calls to save..
    save(res)


def run(to: Path) -> Iterable[Exception]:
    for tab in tabs():
        logging.info('rendering %s', tab.name)
        fname = to / (tab.name + '.html')

        try:
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
    args = p.parse_args()

    # todo pass function names to render? seems easier than tab names? or either?
    errors = list(run(to=args.to))
    if len(errors) > 0:
        logging.error('Had %d errors while rendering', len(errors))
        for e in errors:
            logging.exception(e)
        import sys
        sys.exit(1)


if __name__ == '__main__':
    main()
