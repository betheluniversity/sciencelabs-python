import json

# Packages
from flask import render_template, request, redirect, url_for
from flask import session as flask_session
from flask_classy import FlaskView, route

# Local
from sciencelabs.db_repository.user_functions import User
from sciencelabs.db_repository.course_functions import Course
from sciencelabs.db_repository.schedule_functions import Schedule
from sciencelabs.wsapi.wsapi_controller import WSAPIController
from sciencelabs.sciencelabs_controller import ScienceLabsController


class UsersView(FlaskView):
    route_base = 'user'

    def __init__(self):
        self.user = User()
        self.course = Course()
        self.schedule = Schedule()
        self.wsapi = WSAPIController()
        self.slc = ScienceLabsController()

    def index(self):
        self.slc.check_roles_and_route(['Administrator'])

        active_users = self.user.get_all_current_users()
        users_info = {}
        for user in active_users:
            user_roles = self.user.get_user_roles(user.id)
            role_names = [role.name for role in user_roles]
            roles = ", ".join(role_names) if role_names else ''
            users_info[user] = roles
        return render_template('users/users.html', **locals())

    @route('/search')
    def add_user(self):
        self.slc.check_roles_and_route(['Administrator'])

        return render_template('users/add_user.html')

    @route("/admin/<int:user_id>")
    def edit_user(self, user_id):
        self.slc.check_roles_and_route(['Administrator'])

        professor = False
        user = self.user.get_user(user_id)
        roles = self.user.get_all_roles()
        user_role_ids = self.user.get_user_role_ids(user_id)
        active_semester = self.schedule.get_active_semester()
        course_list = self.course.get_semester_courses_with_section(active_semester.id)
        viewable_courses = self.course.get_course_viewer_courses(user_id)
        viewable_course_ids = []
        for course in viewable_courses:
            viewable_course_ids.append(course.id)

        professor_role = self.user.get_professor_role()
        if professor_role.id in user_role_ids:
            professor = True
            professor_courses = self.course.get_professor_teaching_courses(user_id, active_semester.id)

        return render_template('users/edit_user.html', **locals())

    @route('/create/<username>/<first_name>/<last_name>')
    def select_user_roles(self, username, first_name, last_name):
        self.slc.check_roles_and_route(['Administrator'])

        roles = self.user.get_all_roles()
        existing_user = self.user.get_user_by_username(username)
        if existing_user:  # User exists in system
            if existing_user.deletedAt:  # Has been deactivated in the past
                self.user.activate_existing_user(username)
                message = "This user has been deactivated in the past, but now they are reactivated with their same roles."
            else:  # Currently active
                message = "This user already exists in the system and is activated."
        return render_template('users/select_user_roles.html', **locals())

    @route("/search-users", methods=['post'])
    def search_users(self):
        self.slc.check_roles_and_route(['Administrator'])

        form = request.form
        first_name = form.get('firstName')
        last_name = form.get('lastName')
        results = self.wsapi.get_username_from_name(first_name, last_name)
        return render_template('users/user_search_results.html', **locals())

    @route("/deactivate-single-user/<int:user_id>")
    def deactivate_single_user(self, user_id):
        self.slc.check_roles_and_route(['Administrator'])

        try:
            self.user.delete_user(user_id)
            self.slc.set_alert('success', 'User deactivated successfully!')
            return redirect(url_for('UsersView:index'))
        except Exception as error:
            self.slc.set_alert('danger', 'Failed to deactivate user: {0}'.format(str(error)))
            return redirect(url_for('UsersView:edit_user', user_id=user_id))

    @route("/deactivate-users", methods=['post'])
    def deactivate_users(self):
        self.slc.check_roles_and_route(['Administrator'])

        try:
            form = request.form
            json_user_ids = form.get('jsonUserIds')
            user_ids = json.loads(json_user_ids)
            for user in user_ids:
                self.user.delete_user(user)
            self.slc.set_alert('success', 'User(s) deactivated successfully!')
        except Exception as error:
            self.slc.set_alert('danger', 'Failed to deactivate user(s): {0}'.format(str(error)))
        return 'done'  # Return doesn't matter: success or failure take you to the same page. Only the alert changes.

    @route("/save-user-edits", methods=['post'])
    def save_user_edits(self):
        self.slc.check_roles_and_route(['Administrator'])

        form = request.form
        user_id = form.get('user-id')
        username = form.get('username')
        first_name = form.get('first-name')
        last_name = form.get('last-name')
        email = form.get('email')
        roles = form.getlist('roles')
        viewable_courses = form.getlist('courses')
        try:
            self.user.update_user_info(user_id, first_name, last_name, email)
            self.user.clear_current_roles(user_id)
            self.user.set_user_roles(username, roles)
            self.user.set_course_viewer(user_id, viewable_courses)
            self.slc.set_alert('success', 'Edited {0} {1} ({2}) successfully!'.format(first_name, last_name, username))
            return redirect(url_for('UsersView:index'))
        except Exception as error:
            self.slc.set_alert('danger', 'Failed to edit user: {0}'.format(str(error)))
            return redirect(url_for('UsersView:edit_user', user_id=user_id))

    @route('/create-user', methods=['post'])
    def create_user(self):
        self.slc.check_roles_and_route(['Administrator'])

        form = request.form
        first_name = form.get('first-name')
        last_name = form.get('last-name')
        username = form.get('username')
        roles = form.getlist('roles')
        email_pref = 0  # Default sending emails to No
        # If the user is a administrator or a professor, they get emails.
        if 'Administrator' in roles or 'Professor' in roles:
            email_pref = 1
        try:
            self.user.create_user(first_name, last_name, username, email_pref)
            self.user.set_user_roles(username, roles)
            self.slc.set_alert('success', '{0} {1} ({2}) added successfully!'.format(first_name, last_name, username))
            return redirect(url_for('UsersView:index'))
        except Exception as error:
            self.slc.set_alert('danger', 'Failed to add user: {0}'.format(str(error)))
            return redirect(url_for('UsersView:select_user_roles', username=username, first_name=first_name,
                                    last_name=last_name))

    def act_as_user(self, user_id):
        if not flask_session['ADMIN-VIEWER']:
            self.slc.check_roles_and_route(['Administrator'])
            user_info = self.user.get_user(user_id)
            flask_session['ADMIN-VIEWER'] = True
            # Saving old info to return to
            flask_session['ADMIN-USERNAME'] = flask_session['USERNAME']
            flask_session['ADMIN-ROLES'] = flask_session['USER-ROLES']
            flask_session['ADMIN-NAME'] = flask_session['NAME']
            # Setting up viewing role
            flask_session['USERNAME'] = user_info.username
            flask_session['NAME'] = '{0} {1}'.format(user_info.firstName, user_info.lastName)
            flask_session['USER-ROLES'] = []
            user_roles = User().get_user_roles(user_id)
            for role in user_roles:
                flask_session['USER-ROLES'].append(role.name)
        return redirect(url_for('View:index'))

    @route("/reset-act-as", methods=["POST"])
    def reset_act_as(self):
        if flask_session['ADMIN-VIEWER']:
            try:
                # Resetting info
                flask_session['USERNAME'] = flask_session['ADMIN-USERNAME']
                flask_session['ADMIN-VIEWER'] = False
                flask_session['NAME'] = flask_session['ADMIN-NAME']
                flask_session['USER-ROLES'] = flask_session['ADMIN-ROLES']
                # Clearing out unneeded variables
                flask_session.pop('ADMIN-USERNAME')
                flask_session.pop('ADMIN-ROLES')
                flask_session.pop('ADMIN-NAME')
                return redirect(url_for('View:index'))
            except Exception as error:
                self.slc.set_alert('danger', 'An error occurred: {0}'.format(str(error)))
                return redirect(url_for('View:index'))
        else:
            self.slc.set_alert('danger', 'You do not have permission to access this function')
            return redirect(url_for('View:index'))
