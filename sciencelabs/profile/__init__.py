# Packages
from flask import render_template, redirect, url_for, request
from flask import session as flask_session
from flask_classy import FlaskView, route
import json

# Local
from sciencelabs.profile.profile_controller import ProfileController
from sciencelabs.db_repository.user_functions import User
from sciencelabs.sciencelabs_controller import ScienceLabsController


class ProfileView(FlaskView):
    route_base = 'user'

    def __init__(self):
        self.base = ProfileController()
        self.user = User()
        self.slc = ScienceLabsController()

    @route('/edit')
    def index(self):
        user = self.user.get_user_by_username(flask_session['USERNAME'])
        return render_template('profile/profile.html', **locals())

    @route('/save_edits', methods=['post'])
    def save_edits(self):
        try:
            form = request.form
            first_name = form.get('first-name')
            last_name = form.get('last-name')
            username = form.get('username')
            email_pref = form.get('receive-email') or 0  # if User is not allowed to change email pref, set to 0
            self.user.edit_user(first_name,last_name, username, email_pref)
            self.slc.set_alert('success', 'User edited successfully!')
        except Exception as error:
            self.slc.set_alert('danger', 'Failed to edit user: ' + str(error))
        return redirect(url_for('ProfileView:index'))

    @route('/view-role')
    def role_viewer(self):
        role_list = self.user.get_all_roles()
        return render_template('profile/role_viewer.html', **locals())

    @route('/change-role', methods=['POST'])
    def change_role(self):
        self.slc.check_roles_and_route(['Administrator'])
        if not flask_session['ADMIN-VIEWER']:
            role = str(json.loads(request.data).get('chosen-role'))
            flask_session['ADMIN-VIEWER'] = True
            # Saving old info to return too
            flask_session['ADMIN-USERNAME'] = flask_session['USERNAME']
            flask_session['ADMIN-ROLES'] = flask_session['USER-ROLES']
            flask_session['ADMIN-NAME'] = flask_session['NAME']
            # Setting up viewing role
            flask_session['USERNAME'] = role
            flask_session['NAME'] = ""
            flask_session['USER-ROLES'] = role
        return redirect(url_for('ProfileView:role_viewer'))
