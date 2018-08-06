import json

# Packages
from flask import render_template, request
from flask_classy import FlaskView, route

# Local
from sciencelabs.users.users_controller import UsersController
from sciencelabs.db_repository.user_functions import User
from sciencelabs.db_repository.course_functions import Course
from sciencelabs.db_repository.schedule_functions import Schedule
from sciencelabs.oracle_procs.db_functions import get_username_from_name


class UsersView(FlaskView):
    def __init__(self):
        self.base = UsersController()
        self.user = User()
        self.course = Course()
        self.schedule = Schedule()

    def index(self):
        users_info = self.user.get_user_info()
        return render_template('users/users.html', **locals())

    @route('/search')
    def add_user(self):
        return render_template('users/add_user.html')

    def edit_user(self, user_id):
        professor = False;
        user = self.user.get_user(user_id)
        roles = self.user.get_all_roles()
        user_roles = self.user.get_user_roles(user_id)
        active_semester = self.schedule.get_active_semester()
        course_list = self.course.get_semester_courses_with_section(active_semester.id)
        professor_role = self.user.get_professor_role()
        if professor_role in user_roles:
            professor = True;
            professor_courses = self.course.get_professor_courses(user_id)
        return render_template('users/edit_user.html', **locals())

    @route('/create/<username>/<first_name>/<last_name>')
    def select_user_roles(self, username, first_name, last_name):
        roles = self.user.get_all_roles()
        existing_user = self.user.check_for_existing_user(username)
        if existing_user:
            self.user.activate_existing_user(username)
        return render_template('users/select_user_roles.html', **locals())

    @route("/search-users", methods=['post'])
    def search_users(self):
        form = request.form
        first_name = form.get('firstName')
        last_name = form.get('lastName')
        results = get_username_from_name(first_name, last_name)
        return render_template('users/user_search_results.html', **locals())

    @route("/deactivate_single_user", methods=['post'])
    def deactivate_single_user(self):
        form = request.form
        user_id = form.get('userID')
        self.user.delete_user(user_id)
        return 'success'

    @route("/deactivate_users", methods=['post'])
    def deactivate_users(self):
        form = request.form
        json_user_ids = form.get('jsonUserIds')
        user_ids = json.loads(json_user_ids)
        for user in user_ids:
            self.user.delete_user(user)
        return 'success'

    @route("/save_user_edits", methods=['post'])
    def save_user_edits(self):
        form = request.form
        user_id = form.get('userId')
        first_name = form.get('firstName')
        last_name = form.get('lastName')
        email = form.get('email')
        username = form.get('username')
        json_roles = form.get('roles')
        roles = json.loads(json_roles)
        self.user.update_user_info(user_id, first_name, last_name, email)
        self.user.clear_current_roles(user_id)
        self.user.set_user_roles(username, roles)
        return 'success'

    @route('/create_user', methods=['post'])
    def create_user(self):
        form = request.form
        first_name = form.get('firstName')
        last_name = form.get('lastName')
        username = form.get('username')
        json_roles = form.get('roles')
        roles = json.loads(json_roles)
        self.user.create_user(first_name, last_name, username)
        self.user.set_user_roles(username, roles)
        return 'success'
