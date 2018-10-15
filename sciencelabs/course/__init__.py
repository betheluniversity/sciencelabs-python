# Packages
from flask import render_template, request, redirect, url_for
from flask_classy import FlaskView, route

# Local
from sciencelabs.course.course_controller import CourseController
from sciencelabs.db_repository.course_functions import Course
from sciencelabs.db_repository.schedule_functions import Schedule
from sciencelabs.oracle_procs.db_functions import get_course_is_valid, get_info_for_course
from sciencelabs.sciencelabs_controller import requires_auth


class CourseView(FlaskView):
    route_base = 'course'

    def __init__(self):
        self.base = CourseController()
        self.course = Course()
        self.schedule = Schedule()

    @route('/admin/')
    def index(self):
        return render_template('course/base.html', **locals())

    @route('<int:course_id>')
    def view_course(self, course_id):
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
        form = request.form
        course_string = form.get('potential_courses')
        course_list = course_string.split(";")
        for course in course_list:
            number = self.dept_length(course)
            cc_info = get_course_is_valid(course[:number], course[number:])
            course_info = get_info_for_course(course[:number], course[number:])
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
        else:
            self.course.create_coursecode(info)

    def handle_course(self, info):
        does_exist = self.course.check_for_existing_course(info)
        if not does_exist:
            self.course.create_course(info)

    @route("/delete/<int:course_id>")
    def delete_course(self, course_id):
        course_table, user_table, semester_table = self.course.get_course(course_id)
        if course_table:
            course_info = self.course.get_course_info()
            count = 0
            for courses, user in course_info:
                if courses.dept == course_table.dept and courses.course_num == course_table.course_num:
                    count += 1
                self.course.deactivate_coursecode(course_table.dept, course_table.course_num)
            self.course.delete_course(course_table, user_table)

        return redirect(url_for('CourseView:index'))
