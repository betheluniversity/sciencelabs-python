# Packages
from flask import render_template
from flask_classy import FlaskView, route

# Local
from sciencelabs.course.course_controller import CourseController
from sciencelabs.db_repository.course_functions import Course


class CourseView(FlaskView):
    route_base = 'course'

    def __init__(self):
        self.base = CourseController()
        self.course = Course()

    @route('/admin')
    def index(self):
        course_info = self.course.get_course_info()
        return render_template('course/base.html', **locals())

    @route('<int:course_id>')
    def view_course(self, course_id):
        course = self.course.get_course(course_id)
        return render_template('course/view_course.html', **locals())