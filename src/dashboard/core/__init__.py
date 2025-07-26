type Res[T] = T | Exception

from .tabs import tab  # noqa: F401


def nicename(x: str) -> str:
    x = x.removesuffix('_fake')
    x = x.removeprefix('plot_')
    return x
