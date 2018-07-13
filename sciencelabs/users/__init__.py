# Packages
from flask import render_template
from flask_classy import FlaskView

# Local
from sciencelabs.users.users_controller import UsersController
from sciencelabs.db_repository.user_functions import UserFunctions


class UsersView(FlaskView):
    def __init__(self):
        self.base = UsersController()

    def index(self):
        users_info = UserFunctions().get_user_info()
        return render_template('users/base.html', **locals())

    def add_user(self):
        return render_template('users/add_user.html')
