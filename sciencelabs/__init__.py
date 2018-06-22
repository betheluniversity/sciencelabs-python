# Global
import logging

# Packages
from flask import Flask
from raven.contrib.flask import Sentry

# Local
from sciencelabs.sciencelabs_controller import get_app_settings


app = Flask(__name__)

app.config.from_object('config.config')

sentry = Sentry(app, dsn=app.config['SENTRY_URL'], logging=True, level=logging.INFO)

from sciencelabs.views import View
from sciencelabs.lab_session import LabSessionView
from sciencelabs.reports import ReportView
View.register(app)
LabSessionView.register(app)
ReportView.register(app)

app_settings = get_app_settings()
app.jinja_env.globals.update(app_settings=app_settings)

if __name__ == "__main__":
    app.run()
