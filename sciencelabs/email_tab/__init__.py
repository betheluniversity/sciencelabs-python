# Packages
from flask import render_template
from flask_classy import FlaskView

# Local
from sciencelabs.email_tab.email_controller import EmailController
from sciencelabs.db_repository.user_functions import User


class EmailView(FlaskView):
    route_base = 'email_tab/create'

    def __init__(self):
        self.base = EmailController()
        self.user = User()

    def index(self):
        role_list = self.user.get_all_roles()
        user_list = self.user.get_all_current_users()
        return render_template('email_tab/base.html', **locals())

