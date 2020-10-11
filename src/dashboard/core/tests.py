from pathlib import Path


def save_plot(plot, name: str):
    base = Path('test-outputs')
    path = base / Path(name)
    path.parent.mkdir(exist_ok=True, parents=True)
    suf = path.suffix
    if suf == '.html':
        from bokeh.io import output_file, save
        output_file(str(path), title='hello', mode='inline', root_dir=None)
        save(plot)
    elif suf == '.png':
        # todo sigh.. seems that png export is way too slow
        from bokeh.io import export_png
        export_png(plot, filename=str(path))
    else:
        raise RuntimeError(name, suf)


def make_test(plot_factory):
    name = plot_factory.__name__
    if name.endswith('_fake'):
        name = name[:-5]
    if name.startswith('plot_'):
        name = name[5:]

    def test() -> None:
        p = plot_factory()
        save_plot(p, name=f'{name}.html')
    return test
