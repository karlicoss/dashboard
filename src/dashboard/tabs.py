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

    def weight():
        # todo wish I could do it in a lambda...
        from .weight import plot_weight as P
        return P()
    yield tab(weight)

    def weight_test():
        from .weight import test_plot_weight as P
        return P()

    yield tab(weight_test)

    def running():
        from .data import endomondo_dataframe as DF
        from .cardio import plot_running as P
        return P(DF())
    yield tab(running)

    def spinning():
        from .data import endomondo_dataframe as DF
        from .cardio import plot_spinning as P
        return P(DF())
    yield tab(spinning)

    # TODO have an autodiscovery mechanism?
    # and allow for explicit invocations too
    def cross_trainer():
        from .data import cross_trainer_dataframe as DF
        from .cardio import plot_cross_trainer as P
        return P(DF())
    yield tab(cross_trainer)


    def exercise_volume():
        from .data import endomondo_dataframe as DF
        from .cardio import plot_cardio_volume as P
        return P(DF())
    yield tab(exercise_volume)


    def rescuetime():
        from .data import rescuetime_dataframe as DF
        from .rescuetime import plot_rescuetime as P
        return P(DF())
    yield tab(rescuetime)

    # I guess it's pretty convenient to keep tabs close
    # maybe just mark some tabs as test tabs?
    def fake_rescuetime():
        import my.rescuetime as R
        with R.fake_data(rows=100000):
            return rescuetime()
    yield tab(fake_rescuetime)

    error_test_tab = Tab(
        name='error_handling_test',
        plotter=lambda: "garbage",
    )

    # uncomment to test out error handling
    # yield error_test
