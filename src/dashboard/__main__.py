from collections.abc import Iterable
from pathlib import Path

from .core.common import logger
from .settings import theme
from .tabs import Tab, tabs

# I guess it kinda makes sense to dump each tab separately


def render_tab(*, tab: Tab, filename: Path):
    res = tab.plotter()

    from bokeh.io import curdoc, output_file, save

    output_file(filename, title=tab.name, mode='inline', root_dir=None)
    curdoc().theme = theme
    # TODO a bit weird that it needs two function calls to save..
    save(res)


def run(to: Path, tab_name: str | None = None, *, debug: bool = False) -> Iterable[Exception]:
    for tab in tabs():
        if isinstance(tab, Exception):
            # todo collect errors in a separate tab? or just 'dashboard.html'?
            yield tab
            continue

        if tab_name is not None and tab.name != tab_name:
            logger.info('skipping %s', tab.name)
            # todo error if no matches??
            continue

        logger.info('rendering %s', tab.name)
        fname = to / (tab.name + '.html')

        try:
            if debug:
                # todo optional dependency?
                from ipdb import launch_ipdb_on_exception  # type: ignore[import-not-found]

                ctx = launch_ipdb_on_exception
            else:
                from contextlib import nullcontext

                ctx = nullcontext
            with ctx():
                _res = render_tab(tab=tab, filename=fname)
        except Exception as e:
            e.add_note(f'while processing {tab.name}')
            # TODO make it defensive? if there were any errors, backup old file, don't overwrite? dunno.
            logger.exception(e)

            import html
            import traceback

            tb = '</br>'.join(html.escape(l) for l in traceback.format_exception(Exception, e, e.__traceback__))
            fname.write_text(tb)

            yield e
            continue


def main() -> None:
    from argparse import ArgumentParser as P

    p = P()
    p.add_argument('--to', type=Path, required=True)
    p.add_argument('--tab', type=str, help='Plot specific tab (by default plots all)')
    p.add_argument('--debug', action='store_true', help='debug on exception')
    args = p.parse_args()

    # todo pass function names to render? seems easier than tab names? or either?
    errors = list(run(to=args.to, tab_name=args.tab, debug=args.debug))
    if len(errors) > 0:
        logger.error('Had %d errors while rendering', len(errors))
        for e in errors:
            logger.exception(e)
        import sys

        sys.exit(1)


if __name__ == '__main__':
    main()
