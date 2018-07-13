# Packages
from flask import render_template
from flask_classy import FlaskView
from datetime import datetime

# Local
from sciencelabs.session.session_controller import SessionController
from sciencelabs.db_repository.SessionRepo import Session
from sciencelabs.db_repository.TutorSessionRepo import TutorSession
from sciencelabs.db_repository.UserRepo import User


class SessionView(FlaskView):
    def __init__(self):
        self.base = SessionController()

    def index(self):
        return render_template('session/base.html')

    def closed(self):
        timedelta_to_time = datetime.min
        sessions = Session().get_closed_sessions()
        session_tutors = TutorSession()
        return render_template('session/closed_sessions.html', **locals())

    def create(self):
        return render_template('session/create_session.html')

    def restore(self):
        return render_template('session/restore_session.html')

    def edit_session(self, session_id):
        timedelta_to_time = datetime.min
        session = Session.get_session(self, session_id)
        leads, tutors = TutorSession.get_session_tutors(self, session_id)
        session_students = User.get_session_students(self, session_id)
        return render_template('session/edit_closed_session.html', **locals())

    def edit_student(self):
        return render_template('session/edit_student.html')

    def add_student(self):
        return render_template('session/add_student.html')

    def add_anonymous(self):
        return render_template('session/add_anonymous.html')

    def edit_tutor(self, tutor_id, session_id):
        timedelta_to_time = datetime.min
        tutor = TutorSession.get_tutor_session_info(self, tutor_id, session_id)
        return render_template('session/edit_tutor.html', **locals())

    def add_tutor(self):
        return render_template('session/add_tutor.html')

    def delete_session(self):
        return render_template('session/delete_session.html')
