# Global
import logging

# Packages
from flask import Flask, session, request, redirect, url_for
from raven.contrib.flask import Sentry
from sqlalchemy import create_engine
from datetime import datetime
import json

app = Flask(__name__)
app.config.from_object('config')

# Local
from sciencelabs.db_repository.user_functions import User
from sciencelabs.db_repository.schedule_functions import Schedule

#sentry = Sentry(app, dsn=app.config['SENTRY_URL'], logging=True, level=logging.INFO)

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


@app.context_processor
def utility_processor():
    to_return = {}
    to_return.update({
        'now': datetime.now(),
        'lab_title': app.config['LAB_TITLE']
    })

    return to_return


@app.before_first_request
def create_semester_selector():
    if app.config["ENVIRON"] == 'prod':
        username = request.environ.get('REMOTE_USER')
    else:
        username = app.config['TEST_USERNAME']
    semester_list = Schedule().get_semesters()
    current_user = User().get_user_by_username(username)  # TODO: Update with CAS Authentication
    session['ALERT'] = None
    user_roles = User().get_user_roles(current_user.id)
    session['USERNAME'] = current_user.username
    session['NAME'] = current_user.firstName + ' ' + current_user.lastName
    session['ADMIN-VIEWER'] = False
    session['USER-ROLES'] = []
    for role in user_roles:
        session['USER-ROLES'].append(role.name)
    session['SEMESTER-LIST'] = []
    # Adds all semesters to a dictionary
    for semester in semester_list:
        session['SEMESTER-LIST'].append({'id': semester.id, 'term': semester.term, 'year': semester.year, 'active': semester.active})
        # Sets the current active semester to 'SELECTED-SEMESTER'
        if semester.active == 1:
            session['SELECTED-SEMESTER'] = semester.id


@app.route("/set-semester", methods=["POST"])
def set_semester_selector():
    semester_id = str(json.loads(request.data).get('id'))
    # Makes sure that semester_id is valid (always should be but just in case)
    try:
        # Sets the attribute 'active' of all the semesters to 0 so none are active
        for semester in session['SEMESTER-LIST']:
            if semester['id'] == semester_id:
                semester['active'] = 1  # activates the semester chosen
            else:
                semester['active'] = 0  # deactivates all others
        # Sets the SELECTED-SEMESTER
        session['SELECTED-SEMESTER'] = int(semester_id)
        # Lets the session know it was modified
        session.modified = True
        return 'success'
    except Exception as error:
        return error


@app.route("/reset-act-as", methods=["POST"])
def reset_act_as():
    if session['ADMIN-VIEWER']:
        try:
            session['ALERT'] = None
            session['USERNAME'] = session['ADMIN-USERNAME']
            user_info = User().get_user_by_username(session['ADMIN-USERNAME'])
            session['ADMIN-VIEWER'] = False
            session['NAME'] = user_info.firstName + ' ' + user_info.lastName
            session['USER-ROLES'] = session['ADMIN-ROLES']
            return 'success'
        except Exception as error:
            return error


# TODO IN PROGRESS LOGOUT METHOD
@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(app.config['LOGOUT_URL'])  # TODO: CAS AUTHENTICATION


def datetimeformat(value, custom_format='%l:%M%p'):
    if value:
        return (datetime.min + value).strftime(custom_format)
    else:
        return '???'


app.jinja_env.filters['datetimeformat'] = datetimeformat

if __name__ == "__main__":
    app.run()
