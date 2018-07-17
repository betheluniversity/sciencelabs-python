# Packages
from flask import render_template
from flask_classy import FlaskView, route

# Local
from sciencelabs.session.session_controller import SessionController
from sciencelabs.db_repository.session_functions import Session
from sciencelabs.db_repository.user_functions import User


class SessionView(FlaskView):
    def __init__(self):
        self.base = SessionController()
        self.user = User()
        self.session = Session()

    def index(self):
        return render_template('session/base.html')

    def closed(self):
        sessions = self.session.get_closed_sessions()
        session_tutors = self.session
        return render_template('session/closed_sessions.html', **locals())

    def create(self):
        return render_template('session/create_session.html')

    @route('/deleted')
    def restore(self):
        return render_template('session/restore_session.html')

    @route('/edit/<int:session_id>')
    def edit_session(self, session_id):
        session = self.session.get_session(session_id)
        leads, tutors = self.session.get_session_tutors(session_id)
        session_students = self.user.get_session_students(session_id)
        return render_template('session/edit_closed_session.html', **locals())

    def edit_student(self, session_id):
        return render_template('session/edit_student.html')

    def add_student(self):
        return render_template('session/add_student.html')

    def add_anonymous(self):
        return render_template('session/add_anonymous.html')

    def edit_tutor(self, tutor_id, session_id):
        tutor = self.session.get_tutor_session_info(tutor_id, session_id)
        return render_template('session/edit_tutor.html', **locals())

    def add_tutor(self):
        return render_template('session/add_tutor.html')

    def delete_session(self):
        return render_template('session/delete_session.html')
