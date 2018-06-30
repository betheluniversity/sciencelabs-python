# Packages
from flask import render_template
from flask_classy import FlaskView

# Local
from sciencelabs.session.session_controller import SessionController


class SessionView(FlaskView):
    def __init__(self):
        self.base = SessionController()

    def index(self):
        return render_template('session/base.html')

    def closed(self):
        sessions = self.base.get_closed_sessions()
        return render_template('session/closed_sessions.html', **locals())

    def create(self):
        return render_template('session/create_session.html')

    def restore(self):
        return render_template('session/restore_session.html')