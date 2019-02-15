# Packages
from flask import Flask, request
from flask import session as flask_session
from raven.contrib.flask import Sentry
from datetime import datetime

app = Flask(__name__)
app.config.from_object('config')

# Local
from sciencelabs.db_repository import db_session
from sciencelabs.db_repository.user_functions import User
from sciencelabs.db_repository.schedule_functions import Schedule

# sentry = Sentry(app, dsn=app.config['SENTRY_URL'], logging=True, level=logging.INFO)

from sciencelabs.views import View
from sciencelabs.sessions import SessionView
from sciencelabs.reports import ReportView
from sciencelabs.term_startup import TermStartupView
from sciencelabs.users import UsersView
from sciencelabs.email_tab import EmailView
from sciencelabs.course import CourseView
from sciencelabs.schedule import ScheduleView
from sciencelabs.profile import ProfileView
from sciencelabs.sciencelabs_controller import ScienceLabsController as slc
View.register(app)
SessionView.register(app)
ReportView.register(app)
TermStartupView.register(app)
UsersView.register(app)
EmailView.register(app)
CourseView.register(app)
ScheduleView.register(app)
ProfileView.register(app)


# This makes these variables open to use everywhere
@app.context_processor
def utility_processor():
    to_return = {}
    to_return.update({
        'now': datetime.now(),
        'lab_title': app.config['LAB_TITLE'],
        'lab_base_url': app.config['LAB_BASE_URL'],
        'alert': slc().get_alert()
    })

    return to_return


def datetimeformat(value, custom_format='%l:%M%p'):
    if value:
        return (datetime.min + value).strftime(custom_format)
    else:
        return '???'


app.jinja_env.filters['datetimeformat'] = datetimeformat


@app.before_request
def before_request():
    if 'assets' in request.path or '/cron/' in request.path or '/checkin/' in request.path or '/student-attendance/' in request.path or '/tutor-attendance/' in request.path:
        pass
    else:
        active_semester = Schedule().get_active_semester()
        if 'USERNAME' not in flask_session.keys():
            if app.config['ENVIRON'] == 'prod':
                username = request.environ.get('REMOTE_USER')
            else:
                username = app.config['TEST_USERNAME']
            current_user = User().get_user_by_username(username)
            if not current_user:
                current_user = User().create_user_at_sign_in(username, active_semester)
            flask_session['USERNAME'] = current_user.username
            flask_session['NAME'] = current_user.firstName + ' ' + current_user.lastName
            flask_session['USER-ROLES'] = []
            user_roles = User().get_user_roles(current_user.id)
            for role in user_roles:
                flask_session['USER-ROLES'].append(role.name)
        if 'NAME' not in flask_session.keys():
            flask_session['NAME'] = flask_session['USERNAME']
        if 'USER-ROLES' not in flask_session.keys():
            flask_session['USER-ROLES'] = ['STUDENT']
        if 'ADMIN-VIEWER' not in flask_session.keys():
            flask_session['ADMIN-VIEWER'] = False
        if 'SEMESTER-LIST' not in flask_session.keys():
            semester_list = Schedule().get_semesters()
            flask_session['SEMESTER-LIST'] = []
            # Adds all semesters to a dictionary
            for semester in semester_list:
                flask_session['SEMESTER-LIST'].append(
                    {'id': semester.id, 'term': semester.term, 'year': semester.year, 'active': semester.active})
                # Sets the current active semester to 'SELECTED-SEMESTER'
                if semester.active == 1:
                    flask_session['SELECTED-SEMESTER'] = semester.id
        if 'SELECTED-SEMESTER' not in flask_session.keys():
            flask_session['SELECTED-SEMESTER'] = active_semester.id
        if 'ALERT' not in flask_session.keys():
            flask_session['ALERT'] = None


@app.after_request
def close_db_session(response):
    # This closes the db session to allow the data to propogate to all threads. It's available for use again right away.
    db_session.close()
    return response


if __name__ == "__main__":
    app.run()
