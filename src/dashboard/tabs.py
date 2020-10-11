# abstract 'tabs', used by the interactive server and static HTML renderer
from typing import NamedTuple, Iterable, Protocol, Any

from .core import Res, nicename
from .core.tabs import is_tab

Plotter = Any

class Tab(NamedTuple):
    name: str
    plotter: Plotter



def tab(p: Plotter) -> Tab:
    return Tab(
        name=p.__name__,
        plotter=p,
    )

def handle(module) -> Iterable[Res[Tab]]:
    total = 0
    for x in dir(module):
        if x.startswith('__'):
            continue
        v = getattr(module, x)
        # todo check if callable first?
        if is_tab(v):
            total += 1
            yield Tab(
                # todo make sure it isn't clashing?
                name=nicename(x),
                plotter=v,
            )
    if total == 0:
        yield RuntimeError(f'No @tab discovered in {module}')

# todo render a separate tab with errors??
# ideally this file wraps everythign into lazy wrappers, so if half of the tabs are broken, the other still renders
# todo also need magic top level function similar to old dashboard??

def tabs() -> Iterable[Res[Tab]]:
    # todo just import all submodules? not sure..
    # NOTE would be neater to use __import__ (because it's an expreesion, but it's not mypy friendly :()
    # although at this point static imports don't give as much benefit... maybe a test for successful imports is enough?
    try:
        from . import     cardio
        yield from handle(cardio)
    except Exception as e:
        yield e

    try:
        from . import     weight
        yield from handle(weight)
    except Exception as e:
        yield e

    try:
        from . import     combined
        yield from handle(combined)
    except Exception as e:
        yield e

    try:
        from . import     rescuetime
        yield from handle(rescuetime)
    except Exception as e:
        yield e

    try:
        from . import     environment
        yield from handle(environment)
    except Exception as e:
        yield e

    try:
        from . import     sleepiness
        yield from handle(sleepiness)
    except Exception as e:
        yield e

    try:
        from . import     sleep
        yield from handle(sleep)
    except Exception as e:
        yield e

    # just keeping this one here as a demonstration how explicit Tab works
    def blood():
        from .data import blood_dataframe
        df = blood_dataframe()
        from .blood import plot_blood as plot
        return plot(df)
    yield tab(blood)

    error_test_tab = Tab(
        name='error_handling_test',
        plotter=lambda: "garbage",
    )

    # uncomment to test out error handling
    # yield error_test
