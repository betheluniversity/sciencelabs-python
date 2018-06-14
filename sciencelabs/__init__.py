# Global
import logging

# Packages
import flask_profiler
from flask import Flask
from raven.contrib.flask import Sentry


app = Flask(__name__)
app.config.from_object('config.config')

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


@app.route('/')
def hello():
    return "Hello World"


@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)


sentry = Sentry(app, dsn=app.config['SENTRY_URL'], logging=True, level=logging.INFO)
flask_profiler.init_app(app)

if __name__ == "__main__":
    app.run()
