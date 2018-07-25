# Packages
from flask import render_template
from flask_classy import FlaskView, route

# Local
from sciencelabs.users.users_controller import UsersController
from sciencelabs.db_repository.user_functions import User
from sciencelabs.db_repository.course_functions import Course
from sciencelabs.db_repository.schedule_functions import Schedule


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
        user = self.user.get_user(user_id)
        roles = self.user.get_all_roles()
        user_roles = self.user.get_user_roles(user_id)
        active_semester = self.schedule.get_active_semester()
        course_list = self.course.get_semester_courses(active_semester.id)
        return render_template('users/edit_user.html', **locals())
