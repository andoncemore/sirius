import io
import datetime
import flask
from flask.ext import login
from flask import request, jsonify
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
def print_key(print_key_secret):
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
            html = html_for_image_data(request.data)
        elif request.content_type.startswith('text/'):
            # fallback for sending any text format
            html = html_for_plain_text(request.get_data(as_text=True))
        elif request.content_type == 'application/json':
            json_object = request.get_json()
            if 'html' in json_object:
                html = json_object['html']
            elif 'text' in json_object:
                html = html_for_plain_text(json_object['text'])
            else:
                flask.abort(jsonify(message='json requests must have "html" or "text"'))
        else:
            flask.abort(415)

        try:
            printer.print_html(html, from_name=from_name)
        except hardware.Printer.OfflineError:
            return json.dumps({'status': 'failed-offline'}), 503, {'content-type': 'application/json'}

        return json.dumps({'status': 'sent'}), 200, {'content-type': 'application/json'}

def html_for_plain_text(text):
    return '<div style="white-space: pre-wrap">{text}</div>'.format(
        text=cgi.escape(text)
    )

def html_for_image_data(image_data):
    data_uri = 'data:{type};base64,{data}'.format(
        type=request.content_type,
        data=base64.b64encode(image_data)
    )
    return '<img src="{uri}" style="width: 100%">'