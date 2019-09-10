#!/usr/bin/env python3

import os, sys
import re

if os.path.exists('.env'):
    print('Importing environment from .env...')
    regex = re.compile(r"#.*$") # strip comments
    for line in open('.env'):
        kv = regex.sub("", line).strip()
        if '=' not in kv:
            continue
        name, value = kv.split('=', 1)
        os.environ[name] = value

from sirius.web import webapp
from sirius.fake import commands as fake_commands
from sirius.emulate import commands as emulate_commands
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = webapp.create_app(os.getenv('FLASK_CONFIG', 'default'))
manager = Manager(app)
migrate = Migrate(app, webapp.db)

def make_shell_context():
    return dict(app=app, db=webapp.db)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)
manager.add_command('fake', fake_commands.fake_manager)
manager.add_command('emulate', emulate_commands.manager)


@manager.command
def deploy():
	"""Run deployment tasks."""
	from flask_migrate import upgrade

	# migrate database to latest revision
	upgrade()


if __name__ == '__main__':
    manager.run()

# run with
#gunicorn -b 0.0.0.0:5000 -k flask_sockets.worker manage:app
