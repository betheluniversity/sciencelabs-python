# Global
import logging

# Packages
from flask import Flask
from raven.contrib.flask import Sentry
from sqlalchemy import create_engine
from datetime import datetime

# Local
from app_settings import app_settings
from sciencelabs.db_repository.user_functions import User

app = Flask(__name__)

app.config.from_object('config.config')

#sentry = Sentry(app, dsn=app.config['SENTRY_URL'], logging=True, level=logging.INFO)

db = create_engine(app_settings['DATABASE_KEY'])
conn = db.connect()

from sciencelabs.views import View
from sciencelabs.session import SessionView
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


def datetimeformat(value, custom_format='%l:%M%p'):
    if value:
        return (datetime.min + value).strftime(custom_format)
    else:
        return '???'


# app.jinja_env.globals.update(get_students_in_course=User().get_students_in_course)
app.jinja_env.filters['datetimeformat'] = datetimeformat
app.jinja_env.globals.update(app_settings=app_settings)

# this only works if it is a dict (not a normal boolean variable)
banner_connection_is_working = {
    'value': True
}

if __name__ == "__main__":
    app.run()
