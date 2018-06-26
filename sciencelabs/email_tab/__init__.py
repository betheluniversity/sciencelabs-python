# Packages
from flask import render_template
from flask_classy import FlaskView

# Local
from sciencelabs.email_tab.email_controller import EmailController


class EmailView(FlaskView):
    route_base = 'email_tab/create'

    def __init__(self):
        self.base = EmailController()

    def index(self):
        return render_template('email_tab/home.html')

