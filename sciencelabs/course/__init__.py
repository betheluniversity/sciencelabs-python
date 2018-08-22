# Packages
from flask import render_template, request, redirect, url_for
from flask_classy import FlaskView, route

# Local
from sciencelabs.course.course_controller import CourseController
from sciencelabs.db_repository.course_functions import Course
from sciencelabs.db_repository.schedule_functions import Schedule
from sciencelabs.oracle_procs.db_functions import get_course_is_valid, get_info_for_course

alert = None  # Default alert to nothing


# This method get's the current alert (if there is one) and then resets alert to nothing
def get_alert():
    global alert
    alert_return = alert
    alert = None
    return alert_return


# This method sets the alert for when one is needed next
def set_alert(message_type, message):
    global alert
    alert = {
        'type': message_type,
        'message': message
    }


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
            cc_str += coursecodes.dept + str(coursecodes.courseNum) + ' (' + coursecodes.courseName + ')' + '; '
        semester = self.schedule.get_active_semester()

        return render_template('course/course_table.html', **locals())

    @route("/admin/", methods=['POST'])
    def submit(self):
        form = request.form
        course_string = form.get('potential_courses')
        course_list = course_string.split(";")
        for course in course_list:
            cc_info = get_course_is_valid(course[:3], course[3:])
            course_info = get_info_for_course(course[:3], course[3:])
            if cc_info:
                self.handle_coursecode(cc_info[0])
                if course_info:
                    for info in course_info:
                        self.handle_course(course_info[info])

        return redirect(url_for('CourseView:index'))

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


    # TODO FIGURE OUT HOW TO DELETE COURSES
    @route("/admin/", methods=['POST'])
    def delete(self):
        form = request.form
        course_id = form.get('course-id')
        course_info = self.course.get_course(course_id)
        if course_info:
            self.course.delete_course(course_info)
        return redirect(url_for('CourseView:index'))
