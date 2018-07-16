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
        self.schedule = Schedule()

    def index(self):
        timedelta_to_time = datetime.min
        schedule_info = self.schedule.get_schedule_tab_info()
        # TODO
        # schedule_tutors = TutorSchedule()
        # schedule_courses = ScheduleCourseCodes()
        return render_template('schedule/schedules.html', **locals())

    @route('/create')
    def create_new_schedule(self):
        return render_template('schedule/create_new_schedule.html')

    def edit_schedule(self, schedule_id):
        timedelta_to_time = datetime.min
        schedule = Schedule().get_schedule(schedule_id)
        return render_template('schedule/edit_schedule.html', **locals())
