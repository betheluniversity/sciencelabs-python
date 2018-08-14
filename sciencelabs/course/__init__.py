# Packages
from flask import render_template, request
from flask_classy import FlaskView, route

# Local
from sciencelabs.course.course_controller import CourseController
from sciencelabs.db_repository.course_functions import Course
from sciencelabs.db_repository.schedule_functions import Schedule
from sciencelabs.oracle_procs.db_functions import get_course_is_valid


class CourseView(FlaskView):
    route_base = 'course'

    def __init__(self):
        self.base = CourseController()
        self.course = Course()
        self.schedule = Schedule()
        self.potential_courses = []

    @route('/admin/')
    def index(self):
        course_info = self.course.get_course_info()
        semester = self.schedule.get_active_semester()
        return render_template('course/base.html', **locals())

    @route('<int:course_id>')
    def view_course(self, course_id):
        course, user, semester = self.course.get_course(course_id)
        return render_template('course/view_course.html', **locals())

    @route("/add-potential-courses", methods=['POST'])
    def add_potential_course(self):
        form = request.form
        sbj_num = form.get('sbj_num')
        self.potential_courses.append(sbj_num)
        return ''

    @route("/submit", methods=['POST'])
    def submit(self):
        results = []
        for course in self.potential_courses:
            result = get_course_is_valid(course[:3], course[3:])
            if result:
                results.append(result)
        self.potential_courses = []
        return results
