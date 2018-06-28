# Global
import logging

# Packages
from flask import Flask
from raven.contrib.flask import Sentry
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table
from sqlalchemy import *

# Local
from app_settings import app_settings


app = Flask(__name__)

app.config.from_object('config.config')

sentry = Sentry(app, dsn=app.config['SENTRY_URL'], logging=True, level=logging.INFO)

db = create_engine('mysql://root:jj914.base@localhost/mathlab_real_db')
conn = db.connect()

metadata = MetaData()
user = Table('user', metadata, autoload=True, autoload_with=db)
print(repr(user))

print('<--------------------------------------------------------------------------------->')

role = Table('Role', metadata, autoload=True, autoload_with=db)
print(repr(role))

print('<--------------------------------------------------------------------------------->')

s = select([user])
result = conn.execute(s)
for row in result:
    print(row)

print('<--------------------------------------------------------------------------------->')

s = select([user.c.username])
result = conn.execute(s)
for row in result:
    print(row)

print('<--------------------------------------------------------------------------------->')

s = select([role])
result = conn.execute(s)
for row in result:
    print(row)

print('<--------------------------------------------------------------------------------->')

result = conn.execute(select([user, user.c.password]))
for row in result:
    print(row)

print('<--------------------------------------------------------------------------------->')

result = conn.execute(select([user, user.c.username]).where(user.c.username == 'bam95899'))  # or user.c.usernmae
for row in result:
    print(row)

result.close()

from sciencelabs.views import View
from sciencelabs.session import SessionView
from sciencelabs.reports import ReportView
from sciencelabs.term_startup import TermStartupView
from sciencelabs.users import UsersView
from sciencelabs.email_tab import EmailView
from sciencelabs.course import CourseView
from sciencelabs.schedule import ScheduleView
from sciencelabs.profile import ProfileView
View.register(app)
SessionView.register(app)
ReportView.register(app)
TermStartupView.register(app)
UsersView.register(app)
EmailView.register(app)
CourseView.register(app)
ScheduleView.register(app)
ProfileView.register(app)

app.jinja_env.globals.update(app_settings=app_settings)

if __name__ == "__main__":
    app.run()
