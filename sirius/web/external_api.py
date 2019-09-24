import io
import datetime
import flask
import flask_login as login
from flask import request
import flask_wtf
import wtforms
import base64
import json

from sirius.models.db import db
from sirius.models import hardware
from sirius.models import messages as model_messages
from sirius.protocol import protocol_loop
from sirius.protocol import messages
from sirius.coding import image_encoding
from sirius.coding import templating
from sirius import stats

blueprint = flask.Blueprint('external_api', __name__)

# TODO : need a refactor as this is code duplication from printer_print
@blueprint.route('/ext_api/v1/printer/<int:printer_id>/print_html', methods=['POST'])
@login.login_required
def print_html(printer_id):
    printer = hardware.Printer.query.get(printer_id)
    if printer is None:
        flask.abort(404)

    # PERMISSIONS
    # the printer must either belong to this user, or be
    # owned by a friend
    if printer.owner.id == login.current_user.id:
        # fine
        pass
    elif printer.id in [p.id for p in login.current_user.friends_printers()]:
        # fine
        pass
    else:
        flask.abort(404)

    request.get_data()
    task = json.loads(request.data)
    if not task['message'] or not task['face']:
        flask.abort(500)

    pixels = image_encoding.default_pipeline(
        templating.default_template(
            task['message'],
            from_name=login.current_user.username
        )
    )

    hardware_message = None
    if task['face'] == "noface":
        hardware_message = messages.SetDeliveryAndPrintNoFace(
            device_address=printer.device_address,
            pixels=pixels,
        )
    else:
        hardware_message = messages.SetDeliveryAndPrint(
            device_address=printer.device_address,
            pixels=pixels,
        )


    # If a printer is "offline" then we won't find the printer
    # connected and success will be false.
    success, next_print_id = protocol_loop.send_message(
        printer.device_address, hardware_message)

    # Store the same message in the database.
    png = io.BytesIO()
    pixels.save(png, "PNG")
    model_message = model_messages.Message(
        print_id=next_print_id,
        pixels=bytearray(png.getvalue()),
        sender_id=login.current_user.id,
        target_printer=printer,
    )

    # We know immediately if the printer wasn't online.
    if not success:
        model_message.failure_message = 'Printer offline'
        model_message.response_timestamp = datetime.datetime.utcnow()
    db.session.add(model_message)

    response = {}
    if success:
        response['status'] = 'Sent your message to the printer!'
    else:
        response['status'] = ("Could not send message because the "
                     "printer {} is offline.").format(printer.name)

    return json.dumps(response)
