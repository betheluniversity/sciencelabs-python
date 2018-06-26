# Packages
from flask import render_template
from flask_classy import FlaskView

# Local
from sciencelabs.email.email_controller import EmailController


class EmailView(FlaskView):
    route_base = 'email/create'

    def __init__(self):
        self.base = EmailController()

    def index(self):
        return render_template('email/home.html')

