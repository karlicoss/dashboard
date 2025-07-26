_TAB = '_tab'


def is_tab(f) -> bool:
    return getattr(f, _TAB, False)


def tab[F](f: F) -> F:
    setattr(f, _TAB, True)
    return f
