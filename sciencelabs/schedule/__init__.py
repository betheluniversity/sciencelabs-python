# Packages
from flask import render_template
from flask_classy import FlaskView, route

# Local
from sciencelabs.schedule.schedule_controller import ScheduleController
from sciencelabs.db_repository.schedule_functions import Schedule
from sciencelabs.db_repository.course_functions import Course


class ScheduleView(FlaskView):
    def __init__(self):
        self.base = ScheduleController()
        self.schedule = Schedule()
        self.course = Course()

    def index(self):
        active_semester = self.schedule.get_active_semester()
        schedule_info = self.schedule.get_schedule_tab_info()
        schedule_tutors = self.schedule
        schedule_courses = self.schedule
        return render_template('schedule/schedules.html', **locals())

    @route('/create')
    def create_new_schedule(self):
        active_semester = self.schedule.get_active_semester()
        course_list = self.course.get_semester_courses(active_semester.id)
        tutor_list = self.schedule.get_registered_tutors()
        return render_template('schedule/create_new_schedule.html', **locals())

    def edit_schedule(self, schedule_id):
        active_semester = self.schedule.get_active_semester()
        schedule = Schedule().get_schedule(schedule_id)
        course_list = self.course.get_semester_courses(active_semester.id)
        tutor_names = self.schedule.get_schedule_tutor_names(schedule_id)  # used for a logic check in template
        lead_list = self.schedule.get_registered_leads()  # used for adding tutors to session
        tutor_list = self.schedule.get_registered_tutors()
        return render_template('schedule/edit_schedule.html', **locals())
