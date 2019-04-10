import datetime, random, string, os
from flask import request
from sirius.models.db import db
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm.attributes import flag_modified

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

    number_of_uses = db.Column(db.Integer, default=0, nullable=False)
    senders = db.Column(postgresql.ARRAY(db.String), default=list, nullable=False)

    def record_usage(self, by_name):
        self.number_of_uses += 1
        if by_name not in self.senders:
            self.senders.append(by_name)
            flag_modified(self, 'senders')

    parent_id = db.Column(db.Integer, db.ForeignKey('print_key.id'))
    parent = db.relationship(
        'PrintKey', 
        backref=db.backref('children', lazy='dynamic'), 
        remote_side=[id])

    def senders_formatted(self):
        return ', '.join((s or 'Anonymous') for s in self.senders)
    
    @property
    def url(self):
        if 'DEVICE_KEY_DOMAIN' in os.environ:
            return 'https://%s/%s' % (os.environ['DEVICE_KEY_DOMAIN'], self.secret)
        else:
            # if a DEVICE_KEY_DOMAIN is not defined, we need a request object
            # to get the full URL.
            return '%sprintkey/%s' % (request.url_root, self.secret)
        