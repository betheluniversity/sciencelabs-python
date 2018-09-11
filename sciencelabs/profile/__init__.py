# Packages
from flask import render_template, redirect, url_for, request
from flask_classy import FlaskView, route

# Local
from sciencelabs.profile.profile_controller import ProfileController
from sciencelabs.db_repository.user_functions import User
from sciencelabs.alerts.alerts import *
from app_settings import app_settings


class ProfileView(FlaskView):
    route_base = 'user/edit'

    def __init__(self):
        self.base = ProfileController()
        self.user = User()

    def index(self):
        current_alert = get_alert()
        user = self.user.get_user_by_username(app_settings['TEST_USERNAME'])  # TODO: Update with roles and permissions
        return render_template('profile/home.html', **locals())

    @route('/save_edits', methods=['post'])
    def save_edits(self):
        try:
            form = request.form
            first_name = form.get('first-name')
            last_name = form.get('last-name')
            username = form.get('username')
            email_pref = form.get('receive-email')
            self.user.edit_user(first_name,last_name, username, email_pref)
            set_alert('success', 'User edited successfully!')
        except Exception as error:
            set_alert('danger', 'Failed to edit user: ' + str(error))
        return redirect(url_for('ProfileView:index'))

