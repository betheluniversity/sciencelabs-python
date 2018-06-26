# Packages
from flask import render_template
from flask_classy import FlaskView, route

# Local
from sciencelabs.schedule.schedule_controller import ScheduleController


class ScheduleView(FlaskView):
    def __init__(self):
        self.base = ScheduleController()

    def index(self):
        return render_template('schedule/base.html')

    @route('/create')
    def create_new_schedule(self):
        return render_template('schedule/create_new_schedule.html')
