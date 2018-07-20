# Packages
from flask import render_template
from flask_classy import FlaskView
from datetime import datetime

# Local
from sciencelabs.session.session_controller import SessionController
from sciencelabs.db_repository.session_functions import Session
from sciencelabs.db_repository.user_functions import User
from sciencelabs.db_repository.schedule_functions import Schedule
from sciencelabs.db_repository.course_functions import Course


class SessionView(FlaskView):
    def __init__(self):
        self.base = SessionController()
        self.user = User()
        self.session = Session()
        self.schedule = Schedule()
        self.course = Course()

    def index(self):
        semester = self.schedule.get_active_semester()
        return render_template('session/base.html', **locals())

    def closed(self):
        timedelta_to_time = datetime.min
        sessions = self.session.get_closed_sessions()
        session_tutors = self.session
        semester = self.schedule.get_active_semester()
        semester_list = self.schedule.get_semesters()
        return render_template('session/closed_sessions.html', **locals())

    def create(self):
        semester_list = self.schedule.get_semesters()
        return render_template('session/create_session.html', **locals())

    def restore(self):
        semester = self.schedule.get_active_semester()
        semester_list = self.schedule.get_semesters()
        return render_template('session/restore_session.html', **locals())

    def edit_session(self, session_id):
        timedelta_to_time = datetime.min
        session = self.session.get_session(session_id)
        tutors = self.session.get_session_tutors(session_id)
        session_students = self.session.get_session_students(session_id)
        student_courses = self.session
        semester_list = self.schedule.get_semesters()
        course_list = self.course.get_semester_courses(40013)
        session_courses = self.session.get_session_courses(session_id)
        return render_template('session/edit_closed_session.html', **locals())

    def edit_student(self, student_id, session_id):
        timedelta_to_time = datetime.min
        student = self.session.get_student_session_info(student_id, session_id)
        return render_template('session/edit_student.html', **locals())

    def add_student(self):
        return render_template('session/add_student.html')

    def add_anonymous(self):
        return render_template('session/add_anonymous.html')

    def edit_tutor(self, tutor_id, session_id):
        timedelta_to_time = datetime.min
        tutor = self.session.get_tutor_session_info(tutor_id, session_id)
        return render_template('session/edit_tutor.html', **locals())

    def add_tutor(self):
        return render_template('session/add_tutor.html')

    def delete_session(self):
        return render_template('session/delete_session.html')
