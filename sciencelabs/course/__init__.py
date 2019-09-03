# Packages
from flask import render_template, request, redirect, url_for
from flask_classy import FlaskView, route

# Local
from sciencelabs.db_repository.course_functions import Course
from sciencelabs.db_repository.schedule_functions import Schedule
from sciencelabs.wsapi.wsapi_controller import WSAPIController
from sciencelabs.sciencelabs_controller import ScienceLabsController


class CourseView(FlaskView):
    route_base = 'course'

    def __init__(self):
        self.course = Course()
        self.schedule = Schedule()
        self.wsapi = WSAPIController()
        self.slc = ScienceLabsController()

    @route('/admin/')
    def index(self):
        self.slc.check_roles_and_route(['Administrator'])

        courses = self.course.get_current_courses()
        courses_and_profs = {}
        for course in courses:
            courses_and_profs[course] = self.course.get_course_profs(course.id)
        active_coursecodes = self.course.get_active_coursecode()
        cc_str = ''
        for coursecodes in active_coursecodes:
            cc_str += '{0}{1} ({2}); '.format(coursecodes.dept, coursecodes.courseNum, coursecodes.courseName)
        semester = self.schedule.get_active_semester()

        return render_template('course/base.html', **locals())

    # This route exists in case a user deletes the "admin" part of the course url - redirects back to base page
    @route('/')
    def course_redirect(self):
        return redirect(url_for('CourseView:index'))

    @route('<int:course_id>')
    def view_course(self, course_id):
        self.slc.check_roles_and_route(['Administrator', 'Academic Counselor'])

        course, user, semester = self.course.get_course(course_id)
        return render_template('course/view_course.html', **locals())

    @route("/submit/", methods=['POST', 'GET'])
    def submit(self):
        self.slc.check_roles_and_route(['Administrator'])

        form = request.form
        all_courses_string = form.get('potential_courses')
        all_courses_list = all_courses_string.split(';')
        message = "These course codes were submitted successfully: "
        for course in all_courses_list:
            course_code = course.split(" ")[0]
            split_number = self._dept_length(course_code)
            course_dept = course_code[:split_number]
            course_num = course_code[split_number:]

            try:

                if self.wsapi.validate_course(course_dept, course_num):
                    course_info = self.wsapi.get_course_info(course_dept, course_num)

                    if course_info:
                        course_code_entry = self.course.new_term_course_code(course_info)
                        self.course.new_term_course(course_info, course_code_entry)
                        message += '{0} '.format(course_code)

                #     else:
                #         self.slc.set_alert('danger', '{0} is not offered this semester.'.format(course_code))
                #
                # else:
                #     self.slc.set_alert('danger', '{0} is an invalid course code.'.format(course_code))

            except Exception as error:
                self.slc.set_alert('danger', '{0} Failed: {1}'.format(course_code, error))

        self.slc.set_alert('success', message)

        return redirect(url_for('CourseView:index'))

    def _dept_length(self, course_string):
        count = 0
        for character in course_string:
            if character.isalpha():
                count += 1
            else:
                break
        return count

    @route("/delete/<int:course_id>")
    def delete_course(self, course_id):
        self.slc.check_roles_and_route(['Administrator'])

        try:
            self.course.delete_course(course_id)
            self.slc.set_alert('success', 'Course deleted successfully!')

        except Exception as error:
            self.slc.set_alert('danger', 'Failed to delete course: {0}'.format(error))

        return redirect(url_for('CourseView:index'))
