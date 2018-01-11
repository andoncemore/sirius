import io
import datetime
import flask
from flask.ext import login
from flask import request
import flask_wtf
import wtforms
import base64
import json
import cgi

from sirius.models.db import db
from sirius.models import hardware
from sirius.models.print_keys import PrintKey
from sirius.models import messages as model_messages
from sirius.protocol import protocol_loop
from sirius.protocol import messages
from sirius.coding import image_encoding
from sirius.coding import templating
from sirius import stats

blueprint = flask.Blueprint('print_key_api', __name__)


@blueprint.route('/printkey/<print_key_secret>', methods=['GET', 'POST'])
def print_with_print_key(print_key_secret):
    print_key = PrintKey.query.filter(PrintKey.secret == print_key_secret).first()
    if print_key is None:
        flask.abort(404)

    printer = print_key.printer
    if printer is None:
        flask.abort(404)

    if request.method == 'GET':
        printer_info = {
            "name": printer.name,
            "owner": printer.owner.username,
            "status": 'online' if printer.is_online else 'offline'
        }

        html_preference_score = request.accept_mimetypes.quality('text/html')
        json_preference_score = request.accept_mimetypes.quality('application/json')

        if html_preference_score > json_preference_score:
            return flask.render_template(
                'print_key.html',
                printer=printer,
                printer_info_json=json.dumps(printer_info, indent=2),
                print_key=print_key,
            )
        else:
            return json.dumps(printer_info), 200, {'content-type': 'application/json'}
    else:
        from_name = request.args.get('from') or 'Key ' + print_key_secret[0:4]

        

        if request.content_type == 'text/html':
            html = request.get_data(as_text=True)
        elif request.content_type.startswith('image/'):
            data_uri = 'data:{type};base64,{data}'.format(
                type=request.content_type,
                data=base64.b64encode(request.data)
            )
            html = '<img src="{uri}" style="width: 100%">'
        elif request.content_type.startswith('text/'):
            # fallback for sending any text format
            html = '<div style="white-space: pre-wrap">{text}</div>'.format(
                text=cgi.escape(request.get_data(as_text=True))
            )
        else:
            flask.abort(415)

        try:
            printer.print_html(html, from_name=from_name)
        except hardware.Printer.OfflineError:
            return json.dumps({'status': 'failed-offline'}), 503, {'content-type': 'application/json'}

        return json.dumps({'status': 'sent'}), 200, {'content-type': 'application/json'}
