# Global
import os

# Packages
from flask import render_template
from flask_classy import FlaskView

# Local
from sciencelabs import app


class IndexView(FlaskView):

    def index(self):
        return render_template('index.html', **locals())
