# Packages
from flask import render_template
from flask_classy import FlaskView

# Local
from sciencelabs.users.users_controller import UsersController
from sciencelabs.db_repository.user_functions import User


class UsersView(FlaskView):
    def __init__(self):
        self.base = UsersController()
        self.user = User()

    def index(self):
        users_info = self.user.get_user_info()
        return render_template('users/users.html', **locals())

    def add_user(self):
        return render_template('users/add_user.html')

    def edit_user(self, user_id):
        user, role = self.user.get_user(user_id)
        return render_template('users/edit_user.html', **locals())
