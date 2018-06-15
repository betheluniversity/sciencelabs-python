# Global
import logging

# Packages
import flask_profiler
from flask import Flask
from raven.contrib.flask import Sentry


app = Flask(__name__)

app.config.from_object('config.config')

# create logging
if not app.debug:
    from logging import FileHandler
    file_handler = FileHandler(app.config['INSTALL_LOCATION'] + '/error.log')
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.DEBUG)

app.config["flask_profiler"] = {
    "enabled": True,
    "storage": {
        "engine": "sqlite",  # TODO Not sqlite? Talk to Eric
        "FILE": app.config['INSTALL_LOCATION'] + '/flask_profiler.sql'
    },
    "ignore": [
        "/static/*"
    ]
}

sentry = Sentry(app, dsn=app.config['SENTRY_URL'], logging=True, level=logging.INFO)

from sciencelabs.views import View

View.register(app)


@app.route("/homepage", methods=["POST"])
def homepage():
    return 0

flask_profiler.init_app(app)

if __name__ == "__main__":
    app.run()
