# Packages
from flask import render_template
from flask_classy import FlaskView

# Local
from sciencelabs.course.course_controller import CourseController


class CourseView(FlaskView):
    route_base = 'course/admin'

    def __init__(self):
        self.base = CourseController()

    def index(self):
        course_info = self.base.get_course_info()
        return render_template('course/base.html', **locals())
