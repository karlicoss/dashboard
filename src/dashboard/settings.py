from bokeh.themes import Theme

# https://docs.bokeh.org/en/latest/docs/reference/themes.html
# eh. kind of crappy (I'd much rather prefer python native way of overriding), but at least it works
# Legend.location.property._default = 'top_left' -- didn't work
theme = Theme(
    json={
        'attrs': {
            'Legend': {
                'location': 'top_left',
                'orientation': 'horizontal',
                'click_policy': 'hide',  # todo 'mute'?
            }
        }
    }
)
