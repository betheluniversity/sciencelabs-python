# Packages
from flask import render_template
from flask_classy import FlaskView

# Local
from sciencelabs.profile.profile_controller import ProfileController


class ProfileView(FlaskView):
    route_base = 'user/edit'

    def __init__(self):
        self.base = ProfileController()

    def index(self):
        return render_template('profile/home.html')

