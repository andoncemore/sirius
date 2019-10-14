import os, datetime
import jinja2

DEFAULT_TEMPLATE_FILE = os.path.join(os.path.dirname(__file__), 'default_template.html')

ENV = jinja2.Environment()

# TODO apply scrubber library if wanted.
# https://pypi.python.org/pypi/scrubber

def default_template(raw_html, from_name, date=datetime.datetime.now()):
    with open(DEFAULT_TEMPLATE_FILE) as f:
        template = f.read()

    t = ENV.from_string(template)
    return t.render(
        raw_html=raw_html,
        date=date,
        from_name=from_name
    )
