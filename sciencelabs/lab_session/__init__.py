# Packages
from flask import render_template
from flask_classy import FlaskView

# Local
from sciencelabs.lab_session.lab_session_controller import LabSessionController


class LabSessionView(FlaskView):
    def __init__(self):
        self.base = LabSessionController()

    def index(self):
        return render_template('lab_session/home.html')
