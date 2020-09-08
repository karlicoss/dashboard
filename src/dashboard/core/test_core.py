def test_bokeh_scatter_matrix():
    from .bokeh import _scatter_matrix_demo as demo

    # todo save or something?
    p = demo()


from hypothesis import given, settings, assume

# from hypothesis.strategies import text
# @given(text())
# def test_decode_inverts_encode(s):
#     assert s.encode('utf8').decode('utf8') == s


from hypothesis.extra.pandas import columns, data_frames
import hypothesis.strategies as st


# todo limit the number of examples?? or min_size?
@settings(derandomize=True)
@given(data_frames(
    columns=columns(['value'], dtype=float),
    rows=st.tuples(
        st.floats(min_value=3.0, max_value=100.0, allow_nan=False),
    ),
))
def test_rolling(df):
    assume(len(df) > 4) # TODO set min size
    # TODO needs to hande empty as well

    from bokeh.plotting import figure
    from .bokeh import rolling

    plot = figure(plot_width=800, plot_height=200)

    df.index.rename('x', inplace=True) # meh. by default index doesn't have name..
    [g, g2, g5] = rolling(plot=plot, x='x', y='value', df=df, avgs=[2, 5], legend_label='test')


    from bokeh.plotting import output_file, save
    output_file('res.html', mode='inline', root_dir=None)
    save(plot)
