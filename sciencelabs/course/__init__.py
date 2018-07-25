# Packages
from flask import render_template
from flask_classy import FlaskView, route

# Local
from sciencelabs.course.course_controller import CourseController
from sciencelabs.db_repository.course_functions import Course
from sciencelabs.db_repository.schedule_functions import Schedule


class CourseView(FlaskView):
    route_base = 'course'

    def __init__(self):
        self.base = CourseController()
        self.course = Course()
        self.schedule = Schedule()

    @route('/admin')
    def index(self):
        course_info = self.course.get_course_info()
        semester = self.schedule.get_active_semester()
        return render_template('course/base.html', **locals())

    @route('<int:course_id>')
    def view_course(self, course_id):
        course = self.course.get_course(course_id)
        return render_template('course/view_course.html', **locals())