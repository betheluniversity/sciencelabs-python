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
from sciencelabs.sess import SessionView
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
    for semester in semester_list:
        session['SEMESTER-LIST'][(str(semester.id) + ';' + semester.term + ';' + str(semester.year))] = semester.active


@app.route("/set-semester", methods=["POST"])
def set_semester_selector():
    semester_id = str(json.loads(request.data).get('id'))
    term_year = str(json.loads(request.data).get('term-year'))
    term_year_list = term_year.split(" ")
    term, year = term_year_list
    semester_string = str(semester_id) + ';' + term + ';' + str(year)
    if semester_string in session['SEMESTER-LIST']:
        for semester in session['SEMESTER-LIST']:
            session['SEMESTER-LIST'][semester] = 0
        session['SEMESTER-LIST'][semester_string] = 1
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
