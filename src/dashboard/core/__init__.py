from typing import TypeVar, Union

T = TypeVar('T')
Res = Union[T, Exception]

from .tabs import tab


def nicename(x: str) -> str:
    if x.endswith('_fake'):
        x = x[:-5]
    if x.startswith('plot_'):
        x = x[5:]
    return x
