import flask, io
import flask_login as login
from sqlalchemy import desc
from PIL import Image

from sirius.models import hardware
from sirius.models import messages
from sirius.models.print_keys import PrintKey
from sirius.models.db import db

blueprint = flask.Blueprint('printer_overview', __name__)


@login.login_required
@blueprint.route('/printer/<int:printer_id>')
def printer_overview(printer_id):
	printer = hardware.Printer.query.get(printer_id)
	if printer is None:
		flask.abort(404)
	
	# only show messages history to printer owner
	if printer.owner.id == login.current_user.id:
		messages.Message.timeout_updates()
		message_list = printer.messages.order_by(desc('created'))
	else:
		message_list = []

	# TODO - pagination?
	return flask.render_template(
		'printer_overview.html',
		printer=printer,
		messages=message_list[:10],
	)

@login.login_required
@blueprint.route('/printer/<int:printer_id>/message/<int:message_id>/reprint', methods=['POST'])
def reprint(printer_id, message_id):
	printer = hardware.Printer.query.get(printer_id)
	if printer is None:
		flask.abort(404)
	
	if printer.owner.id != login.current_user.id:
		flask.abort(403)

	message = printer.messages.filter(messages.Message.id==message_id).first()

	if message is None:
		flask.abort(404)

	pixels = Image.open(io.BytesIO(message.pixels))

	printer.print_pixels(pixels, from_name=message.sender_name)

	return flask.redirect(flask.url_for('.printer_overview', printer_id=printer.id))

@login.login_required
@blueprint.route('/printer/<int:printer_id>/printkey/<int:print_key_id>/delete', methods=['POST'])
def print_key_delete(printer_id, print_key_id):
	printer = hardware.Printer.query.get(printer_id)
	if printer is None:
		flask.abort(404)
	
	if printer.owner.id != login.current_user.id:
		flask.abort(403)

	print_key = printer.print_keys.filter(PrintKey.id==print_key_id).first()

	if print_key is None:
		flask.abort(404)

	db.session.delete(print_key)
	db.session.commit()

	return flask.redirect(flask.url_for('.printer_overview', printer_id=printer.id))

@login.login_required
@blueprint.route('/printer/<int:printer_id>/printkey/add', methods=['POST'])
def print_key_add(printer_id):
	printer = hardware.Printer.query.get(printer_id)
	if printer is None:
		flask.abort(404)
	
	if printer.owner.id != login.current_user.id:
		flask.abort(403)

	print_key = PrintKey(printer_id=printer.id)

	db.session.add(print_key)
	db.session.commit()

	return flask.redirect(flask.url_for('.printer_overview', printer_id=printer.id))
