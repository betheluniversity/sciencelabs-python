# Packages
from flask import render_template
from flask_classy import FlaskView, route
from datetime import datetime

# Local
from sciencelabs.schedule.schedule_controller import ScheduleController
from sciencelabs.db_repository.ScheduleRepo import Schedule
from sciencelabs.db_repository.TutorSessionRepo import TutorSession


class ScheduleView(FlaskView):
    def __init__(self):
        self.base = ScheduleController()

    def index(self):
        timedelta_to_time = datetime.min
        schedule_info = Schedule().get_schedule_tab_info()
        session_tutors = TutorSession()
        return render_template('schedule/base.html', **locals())

    @route('/create')
    def create_new_schedule(self):
        return render_template('schedule/create_new_schedule.html')
