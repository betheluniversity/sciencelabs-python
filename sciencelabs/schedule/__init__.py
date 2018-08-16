import json

# Packages
from flask import render_template, redirect, url_for, request
from flask_classy import FlaskView, route

# Local
from sciencelabs.schedule.schedule_controller import ScheduleController
from sciencelabs.db_repository.schedule_functions import Schedule
from sciencelabs.db_repository.course_functions import Course

#######################################################################################################################
# Alert stuff helps give user info on changes they make

alert = None  # Default alert to nothing


# This method get's the current alert (if there is one) and then resets alert to nothing
def get_alert():
    global alert
    alert_return = alert
    alert = None
    return alert_return


# This method sets the alert for when one is needed next
def set_alert(message_type, message):
    global alert
    alert = {
        'type': message_type,
        'message': message
    }
#######################################################################################################################


class ScheduleView(FlaskView):
    def __init__(self):
        self.base = ScheduleController()
        self.schedule = Schedule()
        self.course = Course()

    def index(self):
        current_alert = get_alert()
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

    def delete_schedule(self, schedule_id):
        try:
            asdf
            self.schedule.delete_schedule(schedule_id)
            set_alert('success', 'Deleted schedule successfully!')
        except Exception as error:
            set_alert('danger', 'Failed to delete schedule: ' + str(error))
        return redirect(url_for('ScheduleView:index'))

    @route("/save_schedule_edits", methods=['post'])
    def save_schedule_edits(self):
        try:
            form = request.form
            schedule_id = form.get('scheduleId')
            name = form.get('scheduleName')
            room = form.get('room')
            start_time = form.get('startTime')
            end_time = form.get('endTime')
            day_of_week = int(form.get('dayOfWeek'))
            json_leads = form.get('leads')
            leads = json.loads(json_leads)
            json_tutors = form.get('tutors')
            tutors = json.loads(json_tutors)
            json_courses = form.get('courses')
            courses = json.loads(json_courses)
            self.schedule.edit_schedule(schedule_id, name, room, start_time, end_time, day_of_week)
            self.schedule.edit_lead_schedules(schedule_id, start_time, end_time, leads)
            self.schedule.edit_tutor_schedules(schedule_id, start_time, end_time, tutors)
            self.schedule.edit_schedule_courses(schedule_id, courses)
            return 'Schedule edited successfully'
        except Exception as error:
            return 'Failed to edit schedule: ' + error

    @route('/create_schedule_submit', methods=['post'])
    def create_schedule_submit(self):
        try:
            active_semester = self.schedule.get_active_semester()
            term = active_semester.term
            form = request.form
            name = form.get('scheduleName')
            room = form.get('room')
            start_time = form.get('startTime')
            end_time = form.get('endTime')
            day_of_week = form.get('dayOfWeek')
            json_leads = form.get('leads')
            leads = json.loads(json_leads)
            json_tutors = form.get('tutors')
            tutors = json.loads(json_tutors)
            json_courses = form.get('courses')
            courses = json.loads(json_courses)
            self.schedule.create_new_schedule(name, room, start_time, end_time, day_of_week, term)
            schedule_id = self.schedule.get_new_schedule_id(name, room, start_time, end_time, day_of_week, term)
            self.schedule.create_new_lead_schedules(schedule_id, start_time, end_time, leads)
            self.schedule.create_new_tutor_schedules(schedule_id, start_time, end_time, tutors)
            self.schedule.create_new_schedule_courses(schedule_id, courses)
            return 'Schedule created successfully'
        except Exception as error:
            return 'Failed to create schedule: ' + error
