# Packages
from flask import render_template
from flask_classy import FlaskView

# Local
from sciencelabs.course.course_controller import CourseController
from sciencelabs.db_repository.course_functions import Course


class CourseView(FlaskView):
    route_base = 'course/admin'

    def __init__(self):
        self.base = CourseController()
        self.course = Course()

    def index(self):
        course_info = self.course.get_course_info()
        return render_template('course/base.html', **locals())
