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

    @route("/search-users", methods=['post'])
    def search_users(self):
        form = request.form
        first_name = form.get('firstName')
        last_name = form.get('lastName')
        results = get_username_from_name(first_name, last_name)
        return render_template('users/user_search_results.html', **locals())

    @route("/deactivate_user", methods=['post'])
    def deactivate_user(self):
        form = request.form
        user = form.get('user')
        # TODO: deactivate users
        return 'success'

    @route("/save_user_edits", methods=['post'])
    def save_user_edits(self):
        form = request.form
        user = form.get('user')
        # TODO: edit users
        return 'success'

    @route("/add_user_submit", methods=['post'])
    def add_user_submit(self):
        form = request.form
        user = form.get('user')
        # TODO: add users
        return 'success'
