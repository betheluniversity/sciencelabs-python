# Packages
from flask import render_template, request, redirect, url_for
from flask_classy import FlaskView, route

# Local
from sciencelabs.course.course_controller import CourseController
from sciencelabs.db_repository.course_functions import Course
from sciencelabs.db_repository.schedule_functions import Schedule
from sciencelabs.wsapi.wsapi_controller import WSAPIController
from sciencelabs.sciencelabs_controller import ScienceLabsController


class CourseView(FlaskView):
    route_base = 'course'

    def __init__(self):
        self.base = CourseController()
        self.course = Course()
        self.schedule = Schedule()
        self.wsapi = WSAPIController()
        self.slc = ScienceLabsController()


    @route('/admin/')
    def index(self):
        self.slc.check_roles_and_route(['Administrator'])

        return render_template('course/base.html', **locals())

    @route('<int:course_id>')
    def view_course(self, course_id):
        self.slc.check_roles_and_route(['Administrator', 'Academic Counselor'])

        course, user, semester = self.course.get_course(course_id)
        return render_template('course/view_course.html', **locals())

    def load_course_table(self):
        course_info = self.course.get_course_info()
        active_coursecodes = self.course.get_active_coursecode()
        cc_str = ''
        for coursecodes in active_coursecodes:
            cc_str += '%s%s (%s); ' % (coursecodes.dept, coursecodes.courseNum, coursecodes.courseName)
        semester = self.schedule.get_active_semester()

        return render_template('course/course_table.html', **locals())

    @route("/submit/", methods=['POST'])
    def submit(self):
        self.slc.check_roles_and_route(['Administrator'])

        form = request.form
        course_string = form.get('potential_courses')
        course_list = course_string.split(";")
        for course in course_list:
            course_code = course.split(" ")[0]
            number = self.dept_length(course_code)
            cc_info = self.wsapi.validate_course(course_code[:number], course_code[number:])
            course_info = self.wsapi.get_course_info(course[:number], course[number:])
            if cc_info and course_info:
                self.handle_coursecode(cc_info[0])
                for info in course_info:
                    self.handle_course(course_info[info])

        return redirect(url_for('CourseView:index'))

    def dept_length(self, course_string):
        count = 0
        for character in course_string:
            if character.isalpha():
                count += 1
            else:
                break
        return count

    def handle_coursecode(self, info):
        does_exist = self.course.check_for_existing_coursecode(info)
        if does_exist:
            self.course.check_if_existing_coursecode_is_active(info)
            self.slc.set_alert('success', 'Existing Course Code activated!')
        else:
            self.course.create_coursecode(info)
            self.slc.set_alert('success', 'Course Code created successfully!')

    def handle_course(self, info):
        does_exist = self.course.check_for_existing_course(info)
        if not does_exist:
            self.course.create_course(info)
            self.slc.set_alert('success', 'Course created successfully!')
        else:
            self.slc.set_alert('danger', 'Course already exists so doing nothing.')

    @route("/delete/<int:course_id>")
    def delete_course(self, course_id):
        self.slc.check_roles_and_route(['Administrator'])

        course_table, user_table, semester_table = self.course.get_course(course_id)
        if course_table:
            course_info = self.course.get_course_info()
            count = 0
            for courses, user in course_info:
                if courses.dept == course_table.dept and courses.course_num == course_table.course_num:
                    count += 1
                self.course.deactivate_coursecode(course_table.dept, course_table.course_num)
            self.course.delete_course(course_table, user_table)
        self.slc.set_alert('success', 'Course deleted successfully!')

        return redirect(url_for('CourseView:index'))
