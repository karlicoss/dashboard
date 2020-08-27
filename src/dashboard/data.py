import functools

@functools.lru_cache()
def all_locs():
    from my.location import iter_locations
    # todo islice something earlier?
    return list(iter_locations())
