from typing import TypeVar


_TAB = '_tab'

def is_tab(f) -> bool:
    return getattr(f, _TAB, False)


F = TypeVar('F')
def tab(f: F) -> F:
    setattr(f, _TAB, True)
    return f
