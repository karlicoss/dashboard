# TODO would be nice to keep tests right within files?
# just add to readme how to run the tests

def test_mercator():
    from .location import merc as mercator
    # for now just check it doesn't fail
    mercator(0.0, 0.0)
