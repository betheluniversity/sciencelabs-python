# Global
import logging

# Packages
from flask import Flask
from raven.contrib.flask import Sentry

# Local
from app_settings import app_settings


app = Flask(__name__)

app.config.from_object('config.config')

sentry = Sentry(app, dsn=app.config['SENTRY_URL'], logging=True, level=logging.INFO)

from sciencelabs.views import View
from sciencelabs.session import SessionView
from sciencelabs.reports import ReportView
from sciencelabs.term_startup import TermStartupView
from sciencelabs.users import UsersView
from sciencelabs.email import EmailView
from sciencelabs.course import CourseView
View.register(app)
SessionView.register(app)
ReportView.register(app)
TermStartupView.register(app)
UsersView.register(app)
EmailView.register(app)
CourseView.register(app)

app.jinja_env.globals.update(app_settings=app_settings)

if __name__ == "__main__":
    app.run()
