from hypothesis import settings

# todo crap. this doesn't work.
# pretty annoying that it's so hard to make it deterministic...

settings.register_profile('default', derandomize=True)
