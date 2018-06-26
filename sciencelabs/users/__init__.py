# Packages
from flask import render_template
from flask_classy import FlaskView

# Local
from sciencelabs.users.users_controller import UsersController

class UsersView(FlaskView):
    def __init__(self):
        self.base = UsersController()

    def index(self):
        return render_template('users/base.html')

    def add_user(self):
        return render_template('users/add_user.html')
