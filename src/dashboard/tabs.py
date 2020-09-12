# abstract 'tabs', used by the interactive server and static HTML renderer
from typing import NamedTuple, Iterable, Protocol, Any

from .core import Res

Plotter = Any

class Tab(NamedTuple):
    name: str
    plotter: Plotter



def tab(p: Plotter) -> Tab:
    return Tab(
        name=p.__name__,
        plotter=p,
    )


# ideally this file wraps everythign into lazy wrappers, so if half of the tabs are broken, the other still renders
# todo also need magic top level function similar to old dashboard??

# todo not sure if should be Res type?? hopefully tabs themselves can't fail
def tabs() -> Iterable[Tab]:
    def plot_blood():
        # todo not sure if belongs here.. maybe autodiscover by the return type?
        from .data import blood_dataframe
        df = blood_dataframe()
        from .blood import plot_blood as plot
        return plot(df)

    yield Tab(
        name='blood',
        plotter=plot_blood,
    )

    def plot_sleep():
        from .data import sleep_dataframe
        from .sleep import plot_all_sleep
        return plot_all_sleep(sleep_dataframe())

    yield Tab(
        name='sleep',
        plotter=plot_sleep
    )

    def sleep_correlations():
        from .data import sleep_dataframe
        from .sleep import plot_sleep_correlations
        return plot_sleep_correlations(sleep_dataframe())

    yield tab(sleep_correlations)

    def plot_weight():
        # todo wish I could do it in a lambda...
        from .weight import plot_weight as P
        return P()

    yield Tab(
        name='weight',
        plotter=plot_weight,
    )
    # todo just allow yeld weight function?? autoname it

    def plot_weight_test():
        from .weight import test_plot_weight as P
        return P()

    yield Tab(
        name='weight_test',
        plotter=plot_weight_test,
    )

    def running():
        from .data import endomondo_dataframe as DF
        from .running import plot_running as P
        return P(DF())
    yield tab(running)

    error_test_tab = Tab(
        name='error_handling_test',
        plotter=lambda: "garbage",
    )

    # uncomment to test out error handling
    # yield error_test
