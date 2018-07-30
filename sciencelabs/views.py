# Global
import os

# Packages
from flask import render_template
from flask_classy import FlaskView

# Local
from sciencelabs import app

# this only works if it is a dict (not a normal boolean variable)
banner_connection_is_working = {
    'value': True
}


class View(FlaskView):

    def index(self):
        return render_template('index.html', **locals())
