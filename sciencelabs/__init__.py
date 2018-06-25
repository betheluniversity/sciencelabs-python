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
from sciencelabs.lab_session import LabSessionView
View.register(app)
LabSessionView.register(app)

app.jinja_env.globals.update(app_settings=app_settings)

if __name__ == "__main__":
    app.run()
