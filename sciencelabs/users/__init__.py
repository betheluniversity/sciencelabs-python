import json

# Packages
from flask import render_template, request, redirect, url_for
from flask_classy import FlaskView, route

# Local
from sciencelabs.users.users_controller import UsersController
from sciencelabs.db_repository.user_functions import User
from sciencelabs.db_repository.course_functions import Course
from sciencelabs.db_repository.schedule_functions import Schedule
from sciencelabs.wsapi.wsapi_controller import WSAPIController
from sciencelabs.alerts.alerts import *
from sciencelabs.sciencelabs_controller import requires_auth
from sciencelabs.sciencelabs_controller import ScienceLabsController


class UsersView(FlaskView):
    route_base = 'user'

    def __init__(self):
        self.base = UsersController()
        self.user = User()
        self.course = Course()
        self.schedule = Schedule()
        self.wsapi = WSAPIController()
        self.slc = ScienceLabsController()

    def index(self):
        self.slc.check_roles_and_route(['Administrator'])

        current_alert = get_alert()
        users_info = self.user.get_user_info()
        return render_template('users/users.html', **locals())

    @route('/search')
    def add_user(self):
        self.slc.check_roles_and_route(['Administrator'])

        return render_template('users/add_user.html')

    @route("/admin/<int:user_id>")
    def edit_user(self, user_id):
        self.slc.check_roles_and_route(['Administrator'])

        current_alert = get_alert()
        professor = False
        user = self.user.get_user(user_id)
        roles = self.user.get_all_roles()
        user_role_ids = self.user.get_user_role_ids(user_id)
        active_semester = self.schedule.get_active_semester()
        course_list = self.course.get_semester_courses_with_section(active_semester.id)
        professor_role = self.user.get_professor_role()
        if professor_role.id in user_role_ids:
            professor = True
            professor_courses = self.course.get_professor_courses(user_id)
        return render_template('users/edit_user.html', **locals())

    @route('/create/<username>/<first_name>/<last_name>')
    def select_user_roles(self, username, first_name, last_name):
        self.slc.check_roles_and_route(['Administrator'])

        current_alert = get_alert()
        roles = self.user.get_all_roles()
        existing_user = self.user.check_for_existing_user(username)
        if existing_user:
            self.user.activate_existing_user(username)
        return render_template('users/select_user_roles.html', **locals())

    @route("/search-users", methods=['post'])
    def search_users(self):
        self.slc.check_roles_and_route(['Administrator'])

        form = request.form
        first_name = form.get('firstName')
        last_name = form.get('lastName')
        results = self.wsapi.get_username_from_name(first_name, last_name)
        return render_template('users/user_search_results.html', **locals())

    @route("/deactivate_single_user/<int:user_id>")
    def deactivate_single_user(self, user_id):
        self.slc.check_roles_and_route(['Administrator'])

        try:
            self.user.delete_user(user_id)
            set_alert('success', 'User deactivated successfully!')
            return redirect(url_for('UsersView:index'))
        except Exception as error:
            set_alert('danger', 'Failed to deactivate user: ' + str(error))
            return redirect(url_for('UsersView:edit_user', user_id=user_id))

    @route("/deactivate_users", methods=['post'])
    def deactivate_users(self):
        self.slc.check_roles_and_route(['Administrator'])

        try:
            form = request.form
            json_user_ids = form.get('jsonUserIds')
            user_ids = json.loads(json_user_ids)
            for user in user_ids:
                self.user.delete_user(user)
            set_alert('success', 'User(s) deactivated successfully!')
        except Exception as error:
            set_alert('danger', 'Failed to deactivate user(s): ' + str(error))
        return 'done'  # Return doesn't matter: success or failure take you to the same page. Only the alert changes.

    @route("/save_user_edits", methods=['post'])
    def save_user_edits(self):
        self.slc.check_roles_and_route(['Administrator'])

        try:
            form = request.form
            user_id = form.get('user-id')
            first_name = form.get('first-name')
            last_name = form.get('last-name')
            email = form.get('email')
            username = form.get('username')
            roles = form.getlist('roles')
            self.user.update_user_info(user_id, first_name, last_name, email)
            self.user.clear_current_roles(user_id)
            self.user.set_user_roles(username, roles)
            set_alert('success', 'Edited user successfully!')
            return redirect(url_for('UsersView:index'))
        except Exception as error:
            set_alert('danger', 'Failed to edit user: ' + str(error))
            return redirect(url_for('UsersView:edit_user', user_id=user_id))

    @route('/create_user', methods=['post'])
    def create_user(self):
        self.slc.check_roles_and_route(['Administrator'])

        try:
            form = request.form
            first_name = form.get('first-name')
            last_name = form.get('last-name')
            username = form.get('username')
            roles = form.getlist('roles')
            email_pref = 0  # Default sending emails to No
            if 'Administrator' in roles or 'Professor' in roles:  # If the user is a administrator or a professor, they get emails.
                email_pref = 1
            self.user.create_user(first_name, last_name, username, email_pref)
            self.user.set_user_roles(username, roles)
            set_alert('success', 'User added successfully!')
            return redirect(url_for('UsersView:index'))
        except Exception as error:
            set_alert('danger', 'Failed to add user: ' + str(error))
            return redirect(url_for('UsersView:select_user_roles', username=username, first_name=first_name, last_name=last_name))

    def act_as_user(self, user_id):
        if not session['ADMIN-VIEWER']:
            self.slc.check_roles_and_route(['Administrator'])
            user_info = self.user.get_user(user_id)
            session['ADMIN-VIEWER'] = True
            session['ADMIN-USERNAME'] = session['USERNAME']
            session['ADMIN-ROLES'] = session['USER-ROLES']
            session['USERNAME'] = user_info.username
            session['NAME'] = user_info.firstName + ' ' + user_info.lastName
            session['USER-ROLES'] = []
            user_roles = User().get_user_roles(user_id)
            for role in user_roles:
                session['USER-ROLES'].append(role.name)
        return redirect("/")

    @requires_auth
    @route('/cron_populate_user_courses', methods=['get'])
    def cron_populate_user_courses(self):
        try:
            return self.user.populate_user_courses_cron()
        except Exception as error:
            return 'failed: ' + str(error)

    @requires_auth
    @route('/cron_populate_courses', methods=['get'])
    def cron_populate_courses(self):
        try:
            return self.user.populate_courses_cron()
        except Exception as error:
            return 'failed: ' + str(error)
