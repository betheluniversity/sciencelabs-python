# Packages
from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, request, json
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
        self.slc.check_roles_and_route(['Administrator'])

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
        return render_template('schedule/edit_schedule.html', **locals(), get_session=self.schedule.get_first_session_by_schedule)

    @route("/duplicate/<int:schedule_id>")
    def duplicate_schedule(self, schedule_id):
        self.slc.check_roles_and_route(['Administrator'])

        schedule = self.schedule.get_schedule(schedule_id)
        schedule_courses = self.schedule.get_schedule_courses(schedule_id)
        schedule_courses = self.schedule.get_coursecode_ids(schedule_courses)

        schedule_session = self.schedule.get_first_session_by_schedule(schedule_id)

        tutor_sessions = self.session.get_tutor_sessions(schedule_session.id)

        leads = []
        tutors = []
        for tutor_session in tutor_sessions:
            if tutor_session.isLead == 1:
                leads.append(tutor_session.tutorId)
            else:
                tutors.append(tutor_session.tutorId)

        try:
            active_semester = self.schedule.get_active_semester()
            term = active_semester.term
            term_start_date = active_semester.startDate
            term_end_date = active_semester.endDate
            term_id = active_semester.id
            name = schedule.name
            room = schedule.room
            start_time = schedule.startTime
            end_time = schedule.endTime
            day_of_week = schedule.dayofWeek
            capacity = schedule_session.capacity
            leads = leads
            tutors = tutors
            courses = schedule_courses
            sessions = self.schedule.create_schedule(term, term_start_date, term_end_date, term_id, name, room,
                                                     start_time, end_time, day_of_week, capacity, leads, tutors,
                                                     courses)

            self.session.check_all_room_groupings(sessions)
            self.session.delete_extra_room_groupings()

            self.slc.set_alert('success', '{0} Schedule created successfully!'.format(name))

            if capacity == 0:
                self.slc.set_alert('success',
                                   '{0} Schedule created successfully! Be aware capacity set to 0.'.format(name))

            return redirect(url_for('ScheduleView:index'))
        except Exception as error:
            self.slc.set_alert('danger', 'Failed to duplicate schedule: {0}'.format(str(error)))
            return redirect(url_for('ScheduleView:index'))

    def delete_schedule(self, schedule_id):
        self.slc.check_roles_and_route(['Administrator'])

        try:
            self.schedule.delete_schedule(schedule_id)
            self.session.delete_extra_room_groupings()
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
        capacity = int(form.get('capacity'))
        leads = form.getlist('leads')
        tutors = form.getlist('tutors')
        courses = form.getlist('courses')
        sessions = self.schedule.get_sessions_by_schedule(schedule_id)
        for session in sessions:
            if session.date >= datetime.now().date():
                reserved_seats = self.session.get_num_reserved_seats(session.id)
                if session.capacity > capacity:
                    # If the session capacity is greater than the new capacity and more seats are reserved than the new
                    # capacity error out
                    if reserved_seats > capacity:
                        self.slc.set_alert('danger',
                                           'Failed to edit session: More students have reserved this session than '
                                           'the new session capacity allows.')
                        return redirect(url_for('ScheduleView:edit_schedule', schedule_id=schedule_id))
                    # Else this means there are less reservations than the new capacity so delete unused seats and shift
                    # students
                    elif reserved_seats <= capacity:
                        reservations = self.session.get_session_reservations(session.id)
                        capacity_issue = False
                        for reservation in reservations:
                            if reservation.seat_number > capacity:
                                capacity_issue = True
                                break
                        if not capacity_issue:
                            self.session.delete_seats(session.id, capacity, session.capacity)
                        else:
                            self.slc.set_alert('danger',
                                               'There are is an issue where someone has a seat number greater than '
                                               'the session capacity for the session.')
                            return redirect(url_for('SessionView:view_session_reservations', session_id=session.id))
                elif session.capacity < capacity > self.session.get_total_seats(session.id):
                    # If the new capacity is greater than the current session capacity and there are less seats than the new
                    # capacity, create new seats
                    self.session.create_seats(session.id, capacity, session.capacity + 1, False)
                elif len(self.session.get_all_session_reservations(session.id)) == 0:
                    self.session.create_seats(session_id=session.id, capacity=capacity, commit=False)
        try:
            # This returns True if it executes successfully
            sessions = self.schedule.edit_schedule(term_start_date, term_end_date, term_id, schedule_id, name, room,
                                                   start_time, end_time, day_of_week, capacity, leads, tutors, courses)

            self.session.check_all_room_groupings(sessions)
            self.session.delete_extra_room_groupings()
            self.slc.set_alert('success', '{0} Schedule edited successfully!'.format(name))

            if capacity == 0:
                self.slc.set_alert('success', '{0} Schedule edited successfully! Be aware capacity set to 0.'.format(name))

            return redirect(url_for('ScheduleView:index'))
        except Exception as error:
            for session in sessions:
                reserved_seats = self.session.get_num_reserved_seats(session.id)
                if reserved_seats <= capacity:
                    reservations = self.session.get_session_reservations(session.id)
                    capacity_issue = False
                    for reservation in reservations:
                        if reservation.seat_number > capacity:
                            capacity_issue = True
                            break
                    if not capacity_issue:
                        self.session.create_seats(session.id, capacity, session.capacity + 1, True)
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
            capacity = int(form.get('capacity'))
            leads = form.getlist('leads')
            tutors = form.getlist('tutors')
            courses = form.getlist('courses')
            sessions = self.schedule.create_schedule(term, term_start_date, term_end_date, term_id, name, room,
                                                     start_time, end_time, day_of_week, capacity, leads, tutors, courses)


            self.session.check_all_room_groupings(sessions)
            self.session.delete_extra_room_groupings()

            self.slc.set_alert('success', '{0} Schedule created successfully!'.format(name))

            if capacity == 0:
                self.slc.set_alert('success', '{0} Schedule created successfully! Be aware capacity set to 0.'.format(name))

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

    @route('view-room-groupings')
    def room_groupings(self):
        room_groupings = self.session.get_all_future_room_groupings()

        sessions = {}
        for room_group in room_groupings:
            sessions[room_group.id] = self.session.get_room_group_sessions(room_group.id)

        return render_template('schedule/view_room_groupings.html', **locals(),
                               get_session=self.session.get_one_room_group_session,
                               get_sessions=self.session.get_room_group_sessions)

    @route('save-room-grouping', methods=['POST'])
    def save_room_group_capacity(self):
        room_group_capacities = json.loads(request.data).get('capacities')

        for info in room_group_capacities:
            capacity = 0
            for session in self.session.get_room_group_sessions(info['room_group_id']):
                capacity += session.capacity
            start = (datetime.min + session.schedStartTime).time().strftime('%I:%M')
            end = (datetime.min + session.schedEndTime).time().strftime('%I:%M')
            if capacity > int(info['capacity']):
                self.slc.set_alert('danger', 'Unable to set capacity for Room Group {0} {1} {2} since total session '
                                             'capacity is greater than room group capacity. Please go fix the '
                                             'capacities of the schedules/sessions.'
                                   .format(session.date.strftime('%m/%d/%Y'), start + ' - ' + end, session.room))

                return redirect(url_for('ScheduleView:room_groupings'))
            self.session.update_room_group_capacity(info['room_group_id'], info['capacity'])

        self.slc.set_alert('success', 'Successfully updated the room group capacities.')

        return 'success'
