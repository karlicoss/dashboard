# abstract 'tabs', used by the interactive server and static HTML renderer


from typing import NamedTuple, Iterable, Protocol, Any

from .core import Res

Plotter = Any

class Tab(NamedTuple):
    name: str
    plotter: Plotter


# ideally this file wraps everythign into lazy wrappers, so if half of the tabs are broken, the other still renders
def plot_blood():
    # todo not sure if belongs here.. maybe autodiscover by the return type?
    from .data import blood_dataframe
    df = blood_dataframe()
    from .blood import plot_blood as plot
    return plot(df)


# todo also need magic top level function similar to old dashboard??

# todo not sure if should be Res type?? hopefully tabs themselves can't fail
def tabs() -> Iterable[Tab]:
    yield Tab(
        name='blood',
        plotter=plot_blood,
    )

    error_test_tab = Tab(
        name='error_handling_test',
        plotter=lambda: "garbage",
    )
    # uncomment to test out error handling
    # yield error_test
