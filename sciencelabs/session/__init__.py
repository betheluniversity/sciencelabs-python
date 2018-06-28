# Packages
from flask import render_template
from flask_classy import FlaskView

# Local
from sciencelabs.session.session_controller import SessionController
from sciencelabs.db_repository import *


class SessionView(FlaskView):
    def __init__(self):
        self.base = SessionController()

    def index(self):
        print(repr(course))
        print('\n\n')
        print(repr(course_code))
        print('\n\n')
        print(repr(course_profs))
        print('\n\n')
        print(repr(course_viewer))
        print('\n\n')
        print(repr(role))
        print('\n\n')
        print(repr(schedule))
        print('\n\n')
        print(repr(schedule_course_codes))
        print('\n\n')
        print(repr(semester))
        print('\n\n')
        print(repr(session))
        print('\n\n')
        print(repr(session_course_codes))
        print('\n\n')
        print(repr(session_courses))
        print('\n\n')
        print(repr(student_session))
        print('\n\n')
        print(repr(tutor_schedule))
        print('\n\n')
        print(repr(tutor_session))
        print('\n\n')
        print(repr(user))
        print('\n\n')
        print(repr(user_course))
        print('\n\n')
        print(repr(user_role))
        return render_template('session/base.html')

    def closed(self):
        return render_template('session/closed_sessions.html')

    def create(self):
        return render_template('session/create_session.html')

    def restore(self):
        return render_template('session/restore_session.html')