# Packages
from flask import render_template
from flask_classy import FlaskView, route
from datetime import datetime

# Local
from sciencelabs.schedule.schedule_controller import ScheduleController
from sciencelabs.db_repository.schedule_functions import Schedule


class ScheduleView(FlaskView):
    def __init__(self):
        self.base = ScheduleController()

    def index(self):
        timedelta_to_time = datetime.min
        schedule_info = Schedule().get_schedule_tab_info()
        return render_template('schedule/base.html', **locals())

    @route('/create')
    def create_new_schedule(self):
        return render_template('schedule/create_new_schedule.html')
