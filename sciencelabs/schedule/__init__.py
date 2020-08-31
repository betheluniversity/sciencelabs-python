# Packages
from flask import render_template, redirect, url_for, request
from flask_classy import FlaskView, route

# Local
from sciencelabs.db_repository.schedule_functions import Schedule
from sciencelabs.db_repository.course_functions import Course
from sciencelabs.db_repository.session_functions import Session
from sciencelabs.sciencelabs_controller import ScienceLabsController


class ScheduleView(FlaskView):
    def __init__(self):
        self.schedule = Schedule()
        self.course = Course()
        self.session = Session()
        self.slc = ScienceLabsController()

    def index(self):
        self.slc.check_roles_and_route(['Administrator', 'Lead Tutor', 'Tutor', 'Professor'])

        active_semester = self.schedule.get_active_semester()
        schedules = self.schedule.get_schedule_tab_info()
        schedule_tutors_and_courses = {}
        for schedule in schedules:
            schedule_tutors_and_courses[schedule] = {
                'tutors': self.schedule.get_schedule_tutors(schedule.id),
                'courses': self.schedule.get_schedule_courses(schedule.id)
            }
        return render_template('schedule/schedules.html', **locals())

    @route('/create')
    def create_new_schedule(self):
        self.slc.check_roles_and_route(['Administrator'])

        active_semester = self.schedule.get_active_semester()
        course_list = self.course.get_semester_courses(active_semester.id)
        lead_list = self.schedule.get_registered_leads()
        tutor_list = self.schedule.get_registered_tutors()
        return render_template('schedule/create_new_schedule.html', **locals())

    @route("/edit/<int:schedule_id>")
    def edit_schedule(self, schedule_id):
        self.slc.check_roles_and_route(['Administrator'])

        active_semester = self.schedule.get_active_semester()
        schedule = self.schedule.get_schedule(schedule_id)
        course_list = self.course.get_semester_courses(active_semester.id)
        schedule_course_ids = self.course.get_schedule_course_ids(schedule_id)
        lead_ids = self.schedule.get_scheduled_lead_ids(schedule_id)
        tutor_ids = self.schedule.get_scheduled_tutor_ids(schedule_id)
        lead_list = self.schedule.get_registered_leads()  # used for adding tutors to session
        tutor_list = self.schedule.get_registered_tutors()
        return render_template('schedule/edit_schedule.html', **locals())

    def delete_schedule(self, schedule_id):
        self.slc.check_roles_and_route(['Administrator'])

        try:
            self.schedule.delete_schedule(schedule_id)
            self.slc.set_alert('success', 'Deleted schedule successfully!')
        except Exception as error:
            self.slc.set_alert('danger', 'Failed to delete schedule: {0}'.format(str(error)))
        return redirect(url_for('ScheduleView:index'))

    @route("/save-schedule-edits", methods=['post'])
    def save_schedule_edits(self):
        self.slc.check_roles_and_route(['Administrator'])

        active_semester = self.schedule.get_active_semester()
        term_start_date = active_semester.startDate
        term_end_date = active_semester.endDate
        term_id = active_semester.id
        form = request.form
        schedule_id = form.get('schedule-id')
        name = form.get('name')
        room = form.get('room')
        start_time = form.get('start-time')
        end_time = form.get('end-time')
        day_of_week = int(form.get('day-of-week'))
        leads = form.getlist('leads')
        tutors = form.getlist('tutors')
        courses = form.getlist('courses')
        try:
            # This returns True if it executes successfully
            self.schedule.edit_schedule(term_start_date, term_end_date, term_id, schedule_id, name, room,
                                        start_time, end_time, day_of_week, leads, tutors, courses)
            self.slc.set_alert('success', '{0} Schedule edited successfully!'.format(name))
            return redirect(url_for('ScheduleView:index'))
        except Exception as error:
            self.slc.set_alert('danger', 'Failed to edit schedule: {0}'.format(str(error)))
            return redirect(url_for('ScheduleView:edit_schedule', schedule_id=schedule_id))

    @route('/create-schedule-submit', methods=['post'])
    def create_schedule_submit(self):
        self.slc.check_roles_and_route(['Administrator'])

        try:
            active_semester = self.schedule.get_active_semester()
            term = active_semester.term
            term_start_date = active_semester.startDate
            term_end_date = active_semester.endDate
            term_id = active_semester.id
            form = request.form
            name = form.get('name')
            room = form.get('room')
            start_time = form.get('start-time')
            end_time = form.get('end-time')
            day_of_week = int(form.get('day-of-week'))
            leads = form.getlist('leads')
            tutors = form.getlist('tutors')
            courses = form.getlist('courses')
            self.schedule.create_schedule(term, term_start_date, term_end_date, term_id, name, room,
                                                    start_time, end_time, day_of_week, leads, tutors, courses)
            self.slc.set_alert('success', '{0} Schedule created successfully!'.format(name))
            return redirect(url_for('ScheduleView:index'))
        except Exception as error:
            self.slc.set_alert('danger', 'Failed to create schedule: {0}'.format(str(error)))
            return redirect(url_for('ScheduleView:create_new_schedule'))

    @route('zoom-setup')
    def zoom_setup(self):
        self.slc.check_roles_and_route(['Administrator', 'Lead Tutor', 'Tutor', 'Professor'])

        active_semester = self.schedule.get_active_semester()
        schedules = self.schedule.get_schedule_tab_info()
        schedule_tutors_and_courses = {}
        for schedule in schedules:
            schedule_tutors_and_courses[schedule] = {
                'tutors': self.schedule.get_schedule_tutors(schedule.id),
                'courses': self.schedule.get_schedule_courses(schedule.id)
            }

        return render_template('schedule/zoom_setup.html', **locals(), get_zoom=self.schedule.get_first_session_by_schedule)

    @route('save-zoom-urls', methods=['POST'])
    def save_zoom_urls(self):
        self.slc.check_roles_and_route(['Administrator'])

        schedules = self.schedule.get_schedule_tab_info()
        form = request.form
        for schedule_id in form:
            sessions = self.schedule.get_sessions_by_schedule(schedule_id)
            for session in sessions:
                self.session.update_zoom_url(session.id, form[schedule_id])

        self.slc.set_alert('success', 'The zoom urls were saved successfully!')

        return redirect(url_for('ScheduleView:zoom_setup'))