import flask
from flask.ext import login
import flask_wtf
import wtforms

from sirius.models import hardware
from sirius.protocol import protocol_loop
from sirius.protocol import messages
from sirius.coding import image_encoding

blueprint = flask.Blueprint('printer_print', __name__)


class PrintForm(flask_wtf.Form):
    target_printer = wtforms.SelectField(
        'target_printer',
        coerce=int,
        validators=[wtforms.validators.DataRequired()],
    )
    message = wtforms.StringField(
        'message',
        validators=[wtforms.validators.DataRequired()],
    )


@login.login_required
@blueprint.route('/<int:user_id>/<username>/printer/<int:printer_id>/print', methods=['GET', 'POST'])
def printer_print(user_id, username, printer_id):
    assert user_id == login.current_user.id
    assert username == login.current_user.username

    printer = hardware.Printer.query.get(printer_id)
    if printer is None:
        flask.abort(404)

    form = PrintForm()
    # Note that the form enforces access permissions: People can't
    # submit a valid printer-id that's not owned by the user:
    form.target_printer.choices = [
        (x.id, x.name) for x in login.current_user.printers.all()]

    if form.validate_on_submit():
        flask.flash('Sent your message to the printer!')

        # TODO: move image encoding into a pthread.
        # TODO: use templating to avoid injection attacks
        pixels = image_encoding.html_to_png(
            '<html><body>{}</body></html>'.format(form.message.data))
        hardware_message = messages.SetDeliveryAndPrint(
            device_address=printer.device_address,
            pixels=pixels,
        )
        protocol_loop.send_message(printer.device_address, hardware_message)

        return flask.redirect(flask.url_for(
            'printer_overview.printer_overview',
            user_id=login.current_user.id,
            username=login.current_user.username,
            printer_id=printer.id))

    return flask.render_template(
        'printer_print.html',
        printer=printer,
        form=form,
    )