# Packages
from flask import Response, request
from flask_classy import FlaskView, route
from functools import wraps

# Local
from sciencelabs.db_repository.session_functions import Session
from sciencelabs.db_repository.user_functions import User
from sciencelabs.email_tab.email_controller import EmailController
from sciencelabs import app


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == app.config['LAB_LOGIN']['username'] and password == app.config['LAB_LOGIN']['password']


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


class CronView(FlaskView):
    route_base = 'cron'

    def __init__(self):
        self.session = Session()
        self.user = User()
        self.email = EmailController()

    @requires_auth
    @route('/close-sessions', methods=['get'])
    def close_sessions(self):
        try:
            sessions_closed = self.session.close_open_sessions_cron()
            for session_closed in sessions_closed:
                self.email.close_session_email(session_closed.id)
            return 'success'
        except Exception as error:
            return 'failed: ' + str(error)

    @requires_auth
    @route('/populate-user-courses', methods=['get'])
    def populate_user_courses(self):
        try:
            return self.user.populate_user_courses_cron()
        except Exception as error:
            return 'failed: ' + str(error)

    @requires_auth
    @route('/populate-courses', methods=['get'])
    def populate_courses(self):
        try:
            return self.user.populate_courses_cron()
        except Exception as error:
            return 'failed: ' + str(error)
