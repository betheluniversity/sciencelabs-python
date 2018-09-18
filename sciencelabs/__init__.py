# Global
import logging

# Packages
from flask import Flask, session, request
from raven.contrib.flask import Sentry
from sqlalchemy import create_engine
from datetime import datetime
import json

# Local
from app_settings import app_settings
from sciencelabs.db_repository.user_functions import User
from sciencelabs.db_repository.schedule_functions import Schedule

app = Flask(__name__)
app.config.from_object('config.config')

#sentry = Sentry(app, dsn=app.config['SENTRY_URL'], logging=True, level=logging.INFO)

db = create_engine(app_settings['DATABASE_KEY'])
conn = db.connect()

from sciencelabs.views import View
from sciencelabs.sessions import SessionView
from sciencelabs.reports import ReportView
from sciencelabs.term_startup import TermStartupView
from sciencelabs.users import UsersView
from sciencelabs.email_tab import EmailView
from sciencelabs.course import CourseView
from sciencelabs.schedule import ScheduleView
from sciencelabs.profile import ProfileView
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
        'now': datetime.now()
    })

    return to_return


@app.before_first_request
def create_semester_selector():
    semester_list = Schedule().get_semesters()
    session['SEMESTER-LIST'] = {}
    # Adds all semesters to a dictionary
    for semester in semester_list:
        session['SEMESTER-LIST'][semester.id] = {'id': semester.id, 'term': semester.term, 'year': semester.year, 'active': semester.active}
        # Sets the current active semester to 'SELECTED-SEMESTER'
        if semester.active == 1:
            session['SELECTED-SEMESTER'] = semester.id


@app.route("/set-semester", methods=["POST"])
def set_semester_selector():
    semester_id = str(json.loads(request.data).get('id'))
    # Makes sure that semester_id is valid (always should be but just in case)
    if semester_id in session['SEMESTER-LIST']:
        # Sets the attribute 'active' of all the semesters to 0 so none are active
        for semester in session['SEMESTER-LIST']:
            session['SEMESTER-LIST'][semester]['active'] = 0
        # Activates the specified semester
        session['SEMESTER-LIST'][semester_id]['active'] = 1
        # Sets the SELECTED-SEMESTER
        session['SELECTED-SEMESTER'] = semester_id
        # Lets the session know it was modified
        session.modified = True
        return 'success'
    else:
        return 'error'


# TODO IN PROGRESS LOGOUT METHOD
@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    pass


def datetimeformat(value, custom_format='%l:%M%p'):
    if value:
        return (datetime.min + value).strftime(custom_format)
    else:
        return '???'


app.jinja_env.filters['datetimeformat'] = datetimeformat
app.jinja_env.globals.update(app_settings=app_settings)

if __name__ == "__main__":
    app.run()
