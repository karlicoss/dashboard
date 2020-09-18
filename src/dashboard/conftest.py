from pathlib import Path

import pytest

@pytest.fixture(scope='session', autouse=True)
def generate_html_index():
    yield

    outs = Path('test-outputs')
    # todo descriptions would be nice? maybe dump some json along the plot
    htmls = list(sorted(outs.rglob('*.html')))
    htmls = [h.relative_to(outs) for h in htmls]

    divs = [f'<div><a href="{p}">{p}</a></div>' for p in htmls]
    jdivs = "\n".join(divs)
    INDEX = f'''
<html>
<head><title>Plots index</title></head>
<body>
{jdivs}
</body>
</html
'''
    (outs / 'index.html').write_text(INDEX)
