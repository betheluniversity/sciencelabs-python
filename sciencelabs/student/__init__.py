import json

# Packages
from flask import render_template, request, redirect, url_for
from flask import session as flask_session
from flask_classy import FlaskView, route
from datetime import datetime

# Local
from sciencelabs.db_repository.course_functions import Course
from sciencelabs.db_repository.schedule_functions import Schedule
from sciencelabs.db_repository.session_functions import Session
from sciencelabs.db_repository.user_functions import User
from sciencelabs.sciencelabs_controller import ScienceLabsController


class StudentView(FlaskView):

    def __init__(self):
        self.course = Course()
        self.schedule = Schedule()
        self.session = Session()
        self.user = User()
        self.slc = ScienceLabsController()

    @route('/zoom-sign-on')
    def virtual_sign_on(self):
        open_sessions = self.session.get_open_sessions()
        # Check if student exists in the system
        semester = self.schedule.get_active_semester()
        username = flask_session['USERNAME']
        student = self.user.get_user_by_username(username)
        if not student:
            student = self.user.create_user_at_sign_in(username, semester)

        # Check if student has been deactivated at some point
        if student.deletedAt != None:
            self.user.activate_existing_user(student.username)
            self.user.create_user_courses(student.username, student.id, semester.id)

        # Check to make sure the user has the Student role, add it if they don't
        self.user.check_or_create_student_role(student.id)

        signed_in_sessions = []
        signed_in_courses = {}
        session_courses = {}
        for session in open_sessions:
            try:
                session_courses[session.id].append((self.session.get_sess_courses(session.id, semester.id)))
            except:
                session_courses[session.id] = self.session.get_sess_courses(session.id, semester.id)
            signed_in = self.session.student_currently_signed_in(session.id, student.id)
            if signed_in:
                signed_in_sessions.append(session)
                signed_in_courses[session.id] = self.session.get_student_session_courses(session.id, student.id)

        return render_template('student/virtual_sign_on.html', **locals())

    @route('/load_modal', methods=['POST'])
    def load_virtual_sign_on_modal(self):
        session_id = str(json.loads(request.data).get('session_id'))
        semester = self.schedule.get_active_semester()

        student = self.user.get_user_by_username(flask_session['USERNAME'])
        # Check if student is already signed in
        if self.session.student_currently_signed_in(session_id, student.id):
            self.slc.set_alert('danger', 'You are already signed in.')
            return redirect(url_for('StudentView:virtual_sign_on'))
        student_courses = self.user.get_student_courses(student.id, semester.id)
        time_in = datetime.now().strftime("%I:%M%p")

        return render_template('student/virtual_sign_on_modal.html', **locals())

    @route('/sign-out', methods=['POST'])
    def virtual_sign_out(self):
        session_id = str(json.loads(request.data).get('session_id'))
        student = self.user.get_user_by_username(flask_session['USERNAME'])
        self.session.student_sign_out(session_id, student.id)

        return 'success'
