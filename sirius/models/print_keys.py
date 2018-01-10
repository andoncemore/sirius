import datetime, random, string
from sirius.models.db import db


def generate_secret():
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(20))


class PrintKey(db.Model):
    """
    Keys uniquely identify a printer and include a secret so you can print to a
    little printer by just embedding a secret in an URL.
    """
    id = db.Column(db.Integer, primary_key=True)
    secret = db.Column(db.String, default=generate_secret, unique=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    printer_id = db.Column(db.Integer, db.ForeignKey('printer.id'))
    printer = db.relationship('Printer', backref=db.backref('print_keys', lazy='dynamic'))
