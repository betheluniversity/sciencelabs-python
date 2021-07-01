import json

# Packages
from flask import render_template, request, redirect, url_for
from flask import session as flask_session
from flask_classy import FlaskView, route
from datetime import datetime, timedelta

# Local
from sciencelabs.db_repository.course_functions import Course
from sciencelabs.db_repository.schedule_functions import Schedule
from sciencelabs.db_repository.session_functions import Session
from sciencelabs.db_repository.user_functions import User
from sciencelabs.sciencelabs_controller import ScienceLabsController
from sciencelabs.email_tab import EmailController


class StudentView(FlaskView):

    def __init__(self):
        self.course = Course()
        self.schedule = Schedule()
        self.session = Session()
        self.user = User()
        self.slc = ScienceLabsController()
        self.email = EmailController()

    @route('/reservations')
    def reservations(self):
        # Check if student exists in the system
        student = self.verify_student()

        result_sessions, student_session_courses = self.check_session_courses(self.session.get_reservation_sessions())

        sessions = []
        for session in result_sessions:
            if session.room.lower() != 'virtual':
                sessions.append(session)

        open_sessions, valid_session_courses = self.check_session_courses(self.session.get_open_sessions())
        signed_in_sessions = []
        signed_in_courses = {}
        for session in open_sessions:
            signed_in = self.session.student_currently_signed_in(session.id, student.id)
            if signed_in and self.session.is_reserved(session.id, student.id):
                for s in sessions:
                    if s.id == session.id:
                        sessions.remove(s)
                signed_in_sessions.append(session)
                signed_in_courses[session.id] = self.session.get_student_session_courses(session.id, student.id)

        return render_template('student/reservations.html', **locals(), is_reserved=self.session.is_reserved,
                               get_seats_available=self.session.get_num_seats_available,
                               get_room_group_seats_available=self.session.get_room_group_num_seats_available)

    @route('/virtual-sign-on')
    def virtual_sign_on(self):
        # Check if student exists in the system
        student = self.verify_student()

        semester = self.schedule.get_active_semester()

        sessions, student_session_courses = self.check_session_courses(self.session.get_upcoming_sessions())

        open_sessions, open_student_session_courses = self.check_session_courses(self.session.get_open_sessions())

        signed_in_sessions = []
        signed_in_courses = {}
        for session in open_sessions:
            signed_in = self.session.student_currently_signed_in(session.id, student.id)
            if signed_in:
                signed_in_sessions.append(session)
                signed_in_courses[session.id] = self.session.get_signed_in_courses(session.id, student.id)

        return render_template('student/virtual_sign_on.html', **locals())

    @route('/load-modal', methods=['POST'])
    def load_course_selector_modal(self):
        session_id = str(json.loads(request.data).get('session_id'))
        semester = self.schedule.get_active_semester()
        student = self.user.get_user_by_username(flask_session['USERNAME'])

        # Check if student is already signed in
        if self.session.student_currently_signed_in(session_id, student.id):
            self.slc.set_alert('danger', 'You are already signed in.')
            return redirect(url_for('StudentView:virtual_sign_on'))
        student_courses = self.user.get_student_courses(student.id, semester.id)
        course_codes = self.session.get_session_course_codes(session_id)

        matched_courses = []
        for course in student_courses:
            for course_code in course_codes:
                if course.course_code_id == course_code.id:
                    matched_courses.append(course)

        time_in = datetime.now().strftime("%I:%M%p")

        return render_template('student/course_selector_modal.html', **locals())

    @route('/reservation-confirm', methods=['POST'])
    def reservation_confirm(self):
        form = request.form
        session_id = form.get('sessionID')
        username = form.get('username')
        student_id = int(form.get('studentID'))

        json_courses = form.get('jsonCourseIDs')
        student_courses = json.loads(json_courses)
        other_course_check = 1 if form.get('otherCourseCheck') == 'true' else 0
        other_course_name = form.get('otherCourseName')
        time_in = form.get('timeIn')
        session = self.session.get_session(session_id)

        if not student_courses:
            self.slc.set_alert('danger', 'You must pick the courses you are here for.')
            flask_session['USERNAME'] = username
            return 'failed'

        end_time = datetime.combine(session.date, datetime.strptime(str(session.schedEndTime), '%H:%M:%S').time())
        if datetime.now() > end_time:
            self.slc.set_alert('danger', 'You can not reserve a session that has started more than 10 minutes ago.')
            flask_session['USERNAME'] = username
            return 'failed'

        if not student_courses and other_course_name == '':
            self.slc.set_alert('danger', 'You must pick the courses you are here for or select \'Other\' and fill in the field.')
            # Need to set the username here because it gets cleared, but we need it to reload the page
            flask_session['USERNAME'] = username
            return 'failed'

        session_reservations = self.session.get_session_reservations(session_id)
        for reservation in session_reservations:
            if reservation.user_id == student_id:
                self.slc.set_alert('danger', 'You have already reserved this session. You can\'t reserve it again.')
                return 'failed'

        self.session.reserve_session(session_id, student_id, student_courses)
        self.slc.set_alert('success', 'Your reservation has been confirmed.')

        # send email
        recipient = self.user.get_user_by_username(flask_session.get('USERNAME'))
        self.email.reservation_confirm_or_cancel(session_id, recipient, student_courses)

        return 'success'

    @route('/cancel-reservation', methods=['POST'])
    def cancel_reservation(self):
        session_id = str(json.loads(request.data).get('session_id'))
        student_id = str(json.loads(request.data).get('student_id'))

        self.slc.set_alert('success', 'Your reservation has been cancelled successfully.')

        # send email
        recipient = self.user.get_user_by_username(flask_session.get('USERNAME'))
        self.email.reservation_confirm_or_cancel(session_id, recipient, None, True)

        self.session.cancel_reservation(session_id, student_id)

        return 'success'

    @route('/sign-out', methods=['POST'])
    def virtual_sign_out(self):
        session_id = str(json.loads(request.data).get('session_id'))
        student = self.user.get_user_by_username(flask_session['USERNAME'])

        self.session.student_sign_out(session_id, student.id)

        return 'success'

    def check_session_courses(self, sessions):
        semester = self.schedule.get_active_semester()
        student = self.user.get_user_by_username(flask_session['USERNAME'])

        student_session_courses = {}
        sessions_to_remove = []
        for session in sessions:
            courses = []
            courses_match = False
            
            all_session_course_codes = self.session.get_session_course_codes(session.id)
            for course in self.user.get_student_courses(student.id, semester.id):
                for course_code in all_session_course_codes:
                    if course.course_code_id == course_code.id:
                        courses.append(course)
                        courses_match = True
            if courses_match:
                student_session_courses[session.id] = courses
            else:
                sessions_to_remove.append(session)

        for session in sessions_to_remove:
            sessions.remove(session)

        return sessions, student_session_courses

    def verify_student(self):
        semester = self.schedule.get_active_semester()
        student = self.user.get_user_by_username(flask_session['USERNAME'])

        if not student:
            student = self.user.create_user_at_sign_in(flask_session['USERNAME'], semester)

        # Check if student has been deactivated at some point
        if student.deletedAt != None:
            self.user.activate_existing_user(student.username)

        self.user.create_user_courses(student.username, student.id, semester.id)

        # Check to make sure the user has the Student role, add it if they don't
        self.user.check_or_create_student_role(student.id)

        return student
