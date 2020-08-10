import re

# Packages
from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, request, json, make_response
from flask import session as flask_session
from flask_classy import FlaskView, route

# Local
from sciencelabs.db_repository.session_functions import Session
from sciencelabs.db_repository.user_functions import User
from sciencelabs.db_repository.schedule_functions import Schedule
from sciencelabs.db_repository.course_functions import Course
from sciencelabs.sciencelabs_controller import ScienceLabsController
from sciencelabs.email_tab import EmailController
from sciencelabs.wsapi.wsapi_controller import WSAPIController
from sciencelabs import app


class SessionView(FlaskView):
    def __init__(self):
        self.user = User()
        self.session = Session()
        self.schedule = Schedule()
        self.course = Course()
        self.slc = ScienceLabsController()
        self.email = EmailController()
        self.wsapi = WSAPIController()

    def index(self):
        self.slc.check_roles_and_route(['Administrator', 'Lead Tutor'])

        semester = self.schedule.get_active_semester()
        sessions = self.session.get_available_sessions(semester.id)
        open_sessions = self.session.get_open_sessions()
        sessions_and_tutors = {available_session: self.session.get_session_tutors(available_session.id) for available_session in sessions}
        return render_template('sessions/available_sessions.html', **locals(), are_reservations=self.session.get_session_reservations)

    @route('/closed')
    def closed(self):
        self.slc.check_roles_and_route(['Administrator'])

        sessions = self.session.get_closed_sessions(flask_session['SELECTED-SEMESTER'])
        sessions_and_tutors = {closed_session: self.session.get_session_tutors(closed_session.id) for closed_session in sessions}
        semester = self.schedule.get_semester(flask_session['SELECTED-SEMESTER'])
        return render_template('sessions/closed_sessions.html', **locals())

    def create(self):
        self.slc.check_roles_and_route(['Administrator'])

        active_semester = self.schedule.get_active_semester()
        lead_list = self.schedule.get_registered_leads()
        tutor_list = self.schedule.get_registered_tutors()
        course_list = self.course.get_semester_courses(active_semester.id)
        return render_template('sessions/create_session.html', **locals())

    def deleted(self):
        self.slc.check_roles_and_route(['Administrator'])

        sessions = self.session.get_deleted_sessions(flask_session['SELECTED-SEMESTER'])
        semester = self.schedule.get_semester(flask_session['SELECTED-SEMESTER'])
        sessions_and_tutors = {deleted_session: self.session.get_session_tutors(deleted_session.id) for deleted_session in sessions}
        return render_template('sessions/restore_session.html', **locals())

    @route('/edit/<int:session_id>')
    def edit_session(self, session_id):
        self.slc.check_roles_and_route(['Administrator', 'Lead Tutor'])

        session_info = self.session.get_session(session_id)

        tutor_sessions = self.session.get_tutor_sessions(session_id)
        tutor_info = {tutor_session: self.user.get_user(tutor_session.tutorId) for tutor_session in tutor_sessions}

        lead_ids = self.session.get_session_lead_ids(session_id)
        tutor_ids = self.session.get_session_tutor_ids(session_id)
        lead_list = self.schedule.get_registered_leads()  # used for adding tutors to session
        tutor_list = self.schedule.get_registered_tutors()

        student_sessions = self.session.get_student_sessions(session_id)
        student_info = {}
        for student_session in student_sessions:
            student_info[student_session] = {
                'student': self.user.get_user(student_session.studentId),
                'courses': self.session.get_studentsession_courses(student_session.id)
            }

        course_list = self.course.get_semester_courses(flask_session['SELECTED-SEMESTER'])
        session_course_ids = self.course.get_session_course_ids(session_id)
        session_courses = self.session.get_session_courses(session_id)
        return render_template('sessions/edit_session.html', **locals())

    @route('/attendance/edit/<int:student_session_id>')
    def edit_student(self, student_session_id):
        self.slc.check_roles_and_route(['Administrator', 'Lead Tutor'])

        student = self.session.get_student_session_info(student_session_id)
        student_courses = self.course.get_student_courses(student.id, flask_session['SELECTED-SEMESTER'])
        session_courses = self.session.get_studentsession_courses(student_session_id)
        session_course_ids = [course.id for course in session_courses]
        other_course = self.session.get_other_course(student_session_id)
        return render_template('sessions/edit_student.html', **locals())

    @route('/attendance/student/<int:session_id>')
    def add_student(self, session_id):
        self.slc.check_roles_and_route(['Administrator', 'Lead Tutor'])

        student_list = self.schedule.get_registered_students()
        return render_template('sessions/add_student.html', **locals())

    @route('/addanon/<int:session_id>')
    def add_anonymous(self, session_id):
        self.slc.check_roles_and_route(['Administrator', 'Lead Tutor'])

        session_info = self.session.get_session(session_id)
        return render_template('sessions/add_anonymous.html', **locals())

    @route('/attendance/tutor/edit/<int:tutor_session_id>')
    def edit_tutor(self, tutor_session_id):
        self.slc.check_roles_and_route(['Administrator', 'Lead Tutor'])

        tutor = self.session.get_tutor_session_info(tutor_session_id)
        return render_template('sessions/edit_tutor.html', **locals())

    @route('/addattendance/tutor/<int:session_id>')
    def add_tutor(self, session_id):
        self.slc.check_roles_and_route(['Administrator', 'Lead Tutor'])

        tutor_list = self.schedule.get_registered_tutors()
        return render_template('sessions/add_tutor.html', **locals())

    def delete_session(self, session_id):
        self.slc.check_roles_and_route(['Administrator'])

        session_info = self.session.get_session(session_id)
        return render_template('sessions/delete_session.html', **locals())

    def delete_confirmed(self, session_id):
        self.slc.check_roles_and_route(['Administrator'])

        try:
            self.session.delete_session(session_id)
            self.slc.set_alert('success', 'Session deleted successfully!')
            return redirect(url_for('SessionView:closed'))
        except Exception as error:
            self.slc.set_alert('danger', 'Failed to delete session: {0}'.format(str(error)))
            return redirect(url_for('SessionView:delete_session', session_id=session_id))

    @route('/save-session-edits', methods=['post'])
    def save_session_edits(self):
        self.slc.check_roles_and_route(['Administrator', 'Lead Tutor'])

        form = request.form
        session_id = form.get('session-id')
        name = form.get('name')
        room = form.get('room')
        semester_id = form.get('semester-select')
        if not semester_id:
            active_semester = self.schedule.get_active_semester()
            semester_id = active_semester.id
        date = form.get('date')
        db_date = datetime.strptime(date, "%m/%d/%Y").strftime("%Y-%m-%d")
        scheduled_start = form.get('scheduled-start') or None
        scheduled_end = form.get('scheduled-end') or None
        leads = form.getlist('leads')
        tutors = form.getlist('tutors')
        capacity = int(form.get('capacity'))
        actual_start = form.get('actual-start') or None
        actual_end = form.get('actual-end') or None
        courses = form.getlist('courses')
        comments = form.get('comments')
        anon_students = form.get('anon-students')

        if capacity == 0:
            self.slc.set_alert('danger', 'Failed to edit session: Capacity should be greater than 0')
            return redirect(url_for('SessionView:edit_session', session_id=session_id))

        session = self.session.get_session(session_id)
        if session.capacity > capacity:
            if session.capacity - self.session.get_seats_remaining(session_id) > capacity:
                self.slc.set_alert('danger', 'Failed to edit session: More students have reserved this session than '
                                             'the new capacity allows.')
                return redirect(url_for('SessionView:edit_session', session_id=session_id))
        else:
            self.session.create_seats(session.capacity, capacity)
        try:
            self.session.edit_session(session_id, semester_id, db_date, scheduled_start, scheduled_end, capacity,
                                                actual_start, actual_end, room, comments, anon_students, name, leads,
                                                tutors, courses)
            self.slc.set_alert('success', '{0} ({1}) edited successfully!'.format(name, date))
            return redirect(url_for('SessionView:closed'))
        except Exception as error:
            self.slc.set_alert('danger', 'Failed to edit session: {0}'.format(str(error)))
            return redirect(url_for('SessionView:edit_session', session_id=session_id))

    @route('/save-student-edits/<int:session_id>', methods=['post'])
    def save_student_edits(self, session_id):
        self.slc.check_roles_and_route(['Administrator', 'Lead Tutor'])

        form = request.form
        student_session_id = form.get('student-session-id')
        time_in = form.get('time-in') or None
        time_out = form.get('time-out') or None
        student_courses = form.getlist('course')
        other_check = form.get('other-check')
        other_course = form.get('other-name')
        if not other_check:
            other_course = None
        try:
            # Returns True if successful
            self.session.edit_student_session(student_session_id, time_in, time_out, other_course,
                                                        student_courses)
            self.slc.set_alert('success', 'Edited student successfully!')
            return redirect(url_for('SessionView:edit_session', session_id=session_id))
        except Exception as error:
            self.slc.set_alert('danger', 'Failed to edit student: {0}'.format(str(error)))
            return redirect(url_for('SessionView:edit_student', student_session_id=student_session_id))

    @route('/save-tutor-edits', methods=['post'])
    def save_tutor_edits(self):
        self.slc.check_roles_and_route(['Administrator', 'Lead Tutor'])

        form = request.form
        tutor_session_id = form.get('tutor-session-id')
        session_id = form.get('session-id')
        time_in = form.get('time-in') or None
        time_out = form.get('time-out') or None
        lead_check = form.get('lead')
        lead = 1 if lead_check else 0
        try:
            self.session.edit_tutor_session(tutor_session_id, time_in, time_out, lead)
            self.slc.set_alert('success', 'Tutor edited successfully!')
            return redirect(url_for('SessionView:edit_session', session_id=session_id))
        except Exception as error:
            self.slc.set_alert('danger', 'Failed to edit tutor: {0}'.format(str(error)))
            return redirect(url_for('SessionView:edit_tutor', tutor_session_id=tutor_session_id))

    def delete_student_from_session(self, student_session_id, session_id):
        self.slc.check_roles_and_route(['Administrator'])

        try:
            self.session.delete_student_from_session(student_session_id)
            self.slc.set_alert('success', 'Student deleted successfully!')
        except Exception as error:
            self.slc.set_alert('danger', 'Failed to delete student: {0}'.format(str(error)))
        return redirect(url_for('SessionView:edit_session', session_id=session_id))

    def delete_tutor_from_session(self, tutor_session_id, session_id):
        self.slc.check_roles_and_route(['Administrator'])

        try:
            self.session.delete_tutor_from_session(tutor_session_id)
            self.slc.set_alert('success', 'Tutor deleted successfully!')
        except Exception as error:
            self.slc.set_alert('danger', 'Failed to delete tutor: {0}'.format(str(error)))
        return redirect(url_for('SessionView:edit_session', session_id=session_id))

    @route('/add-student-submit', methods=['post'])
    def add_student_submit(self):
        self.slc.check_roles_and_route(['Administrator', 'Lead Tutor'])

        form = request.form
        session_id = form.get('session-id')
        student_id = form.get('choose-student')
        try:
            self.session.add_student_to_session(session_id, student_id)
            self.slc.set_alert('success', 'Student added successfully!')
            return redirect(url_for('SessionView:edit_session', session_id=session_id))
        except Exception as error:
            self.slc.set_alert('danger', 'Failed to add student: {0}'.format(str(error)))
            return redirect(url_for('SessionView:add_student', session_id=session_id))

    @route('/add-anon-submit', methods=['post'])
    def add_anon_submit(self):
        self.slc.check_roles_and_route(['Administrator', 'Lead Tutor'])

        form = request.form
        session_id = form.get('session-id')
        anon_students = form.get('anon-students')
        try:
            self.session.add_anonymous_to_session(session_id, anon_students)
            self.slc.set_alert('success', 'Anonymous students edited successfully!')
            return redirect(url_for('SessionView:edit_session', session_id=session_id))
        except Exception as error:
            self.slc.set_alert('danger', 'Failed to edit anonymous students: {0}'.format(str(error)))
            return redirect(url_for('SessionView:add_anonymous', session_id=session_id))

    @route('/add-tutor-submit', methods=['post'])
    def add_tutor_submit(self):
        self.slc.check_roles_and_route(['Administrator', 'Lead Tutor'])

        form = request.form
        session_id = form.get('session-id')
        tutor_id = form.get('choose-tutor')
        time_in = form.get('time-in') or None
        time_out = form.get('time-out') or None
        lead_check = form.get('lead')
        lead = 1 if lead_check else 0
        try:
            self.session.add_tutor_to_session(session_id, tutor_id, time_in, time_out, lead)
            self.slc.set_alert('success', 'Tutor added successfully!')
            return redirect(url_for('SessionView:edit_session', session_id=session_id))
        except Exception as error:
            self.slc.set_alert('danger', 'Failed to add tutor: {0}'.format(str(error)))
            return redirect(url_for('SessionView:add_tutor', session_id=session_id))

    @route('/create-session-submit', methods=['post'])
    def create_session_submit(self):
        self.slc.check_roles_and_route(['Administrator'])

        form = request.form
        name = form.get('name')
        room = form.get('room')
        semester_id = form.get('semester-select')
        date = form.get('date')
        db_date = datetime.strptime(date, "%m/%d/%Y").strftime("%Y-%m-%d")
        scheduled_start = form.get('scheduled-start') or None
        scheduled_end = form.get('scheduled-end') or None
        leads = form.getlist('choose-leads')
        tutors = form.getlist('choose-tutors')
        capacity = int(form.get('capacity'))
        actual_start = form.get('actual-start') or None
        actual_end = form.get('actual-end') or None
        courses = form.getlist('courses')
        comments = form.get('comments')
        anon_students = form.get('anon-students')

        if capacity == 0:
            self.slc.set_alert('danger', 'Failed to create session: Capacity should be greater than 0')
            return redirect(url_for('SessionView:create'))

        # Check to see if the session being created is a past session with no actual times. This shouldn't be allowed.
        active_semester = self.schedule.get_active_semester()
        if int(semester_id) != active_semester.id and (not actual_start or not actual_end):
            self.slc.set_alert('danger', 'You are creating a past session with no actual times. '
                                         'You either need to update the semester to create a session for the current '
                                         'semester OR give the past session actual start and end times.')
            return redirect(url_for('SessionView:create'))

        try:
            self.session.create_new_session(semester_id, db_date, scheduled_start, scheduled_end, capacity,
                                                      actual_start, actual_end, room, comments, anon_students, name,
                                                      leads, tutors, courses)
            self.slc.set_alert('success', 'Session {0} ({1}) created successfully!'.format(name, date))
            if actual_start or actual_end:  # Past session, so go to closed to view
                return redirect(url_for('SessionView:closed'))
            else:  # Future session, so go to available to view
                return redirect(url_for('SessionView:index'))
        except Exception as error:
            self.slc.set_alert('danger', 'Failed to create session: {0}'.format(str(error)))
            return redirect(url_for('SessionView:create'))

    @route('/view/<int:session_id>')
    def view_session(self, session_id):
        session_students = self.session.get_session_students(session_id)
        students_and_courses = {student: self.session.get_student_session_courses(session_id, student.id) for student in session_students}
        session_tutors = self.session.get_session_tutors(session_id)
        return render_template('sessions/view_session.html', **locals())

    @route('/view-reservations/<int:session_id>')
    def view_session_reservations(self, session_id):
        reservation_sessions = self.session.get_session_reservations(session_id)
        session = self.session.get_session(session_id)
        return render_template('sessions/view_reservations.html', **locals(),
                               get_reservation_courses=self.session.get_reservation_courses,
                               get_user=self.user.get_user, get_course=self.course.get_course)

    def open_session(self, session_id, session_hash):
        self.slc.check_roles_and_route(['Administrator', 'Lead Tutor'])

        lab_session = self.session.get_session(session_id)

        if lab_session.date.strftime("%m/%d/%Y") == datetime.now().strftime("%m/%d/%Y"):

            if self._check_session_time(lab_session):  # returns true if session is started within an hour window
                opener = self.user.get_user_by_username(flask_session['USERNAME'])
                self.session.start_open_session(session_id, opener.id)
                self.session.tutor_sign_in(session_id, opener.id)
                self.slc.set_alert('success', 'Session {0} ({1}) opened successfully'.format(lab_session.name, lab_session.date.strftime('%m/%d/%Y')))

                return redirect(url_for('SessionView:student_attendance_passthrough', session_id=session_id, session_hash=session_hash))

            else:  # After alert is set it will jump down and return to the session home page
                self.slc.set_alert('danger', 'Session {0} ({1}) does not start at this time'.format(lab_session.name, lab_session.date.strftime('%m/%d/%Y')))

        else:  # Set alert and return to session home page
            self.slc.set_alert('danger', 'Session {0} ({1}) is not scheduled for today'.format(lab_session.name, lab_session.date.strftime('%m/%d/%Y')))

        return redirect(url_for('SessionView:index'))

    def _check_session_time(self, lab_session):
        session_start_time = lab_session.schedStartTime
        start_plus_hour = session_start_time + timedelta(hours=1)
        start_minus_hour = session_start_time - timedelta(hours=1)
        now = datetime.time(datetime.now())
        if start_minus_hour < timedelta(hours=now.hour, minutes=now.minute, seconds=now.second) < start_plus_hour:
            return True  # Return true if session start time is within the hour
        return False

    @route('/no-cas/student-attendance-passthrough/<int:session_id>/<session_hash>', methods=['get', 'post'])
    def student_attendance_passthrough(self, session_id, session_hash):
        return self._logout_open_session(
            url_for('SessionView:student_attendance', session_id=session_id, session_hash=session_hash))

    @route('/no-cas/student-attendance/<int:session_id>/<session_hash>', methods=['get', 'post'])
    def student_attendance(self, session_id, session_hash):
        self._session_clear_save_alert()

        session_info = self.session.get_session(session_id)
        students = self.session.get_session_students(session_id)
        students_and_courses = {student: self.session.get_student_session_courses(session_id, student.id) for student in students}
        # This is for development - allows us to pick a student to sign in as
        all_students = self.user.get_all_current_students()
        # If prod, we send through a route to get CAS auth, else we go straight to student sign in
        if app.config['ENVIRON'] == 'prod':
            submit_url = url_for('SessionView:authenticate_sign_in', session_id=session_id, session_hash=session_hash, user_type='student')
        else:
            submit_url = url_for('SessionView:student_sign_in', session_id=session_info.id, session_hash=session_info.hash, card_id='cas-auth')

        return render_template('sessions/student_attendance.html', **locals())

    @route('/no-cas/tutor-attendance-passthrough/<int:session_id>/<session_hash>', methods=['get', 'post'])
    def tutor_attendance_passthrough(self, session_id, session_hash):
        return self._logout_open_session(
            url_for('SessionView:tutor_attendance', session_id=session_id, session_hash=session_hash))

    @route('/no-cas/tutor-attendance/<int:session_id>/<session_hash>', methods=['get', 'post'])
    def tutor_attendance(self, session_id, session_hash):
        self._session_clear_save_alert()

        session_info = self.session.get_session(session_id)
        course_info = self.course.get_active_course_info()
        tutors = self.session.get_session_tutors(session_id)
        # This is for development - allows us to pick a tutor to sign in as
        all_tutors = self.user.get_all_current_tutors()
        # If prod, we send through a route to get CAS auth, else we go straight to tutor sign in
        if app.config['ENVIRON'] == 'prod':
            submit_url = url_for('SessionView:authenticate_sign_in', session_id=session_info.id, session_hash=session_info.hash, user_type='tutor')
        else:
            submit_url = url_for('SessionView:tutor_sign_in', session_id=session_info.id, session_hash=session_info.hash, card_id='cas-auth')

        return render_template('sessions/tutor_attendance.html', **locals())

    @route('/close-session/<int:session_id>/<session_hash>', methods=['get', 'post'])
    def close_open_session(self, session_id, session_hash):
        self.slc.check_roles_and_route(['Administrator', 'Lead Tutor'])

        session_info = self.session.get_session(session_id)
        course_info = self.course.get_active_course_info()
        return render_template('sessions/close_open_session.html', **locals())

    @route('/no-cas/confirm-close', methods=['post'])
    def confirm_close(self):
        self.slc.check_roles_and_route(['Administrator', 'Lead Tutor'])

        form = request.form
        session_id = form.get('session-id')
        session_hash = form.get('session-hash')
        comments = form.get('comments')
        try:
            self.session.close_open_session(session_id, comments)
            self.email.close_session_email(session_id)
            self.slc.set_alert('success', 'Session closed successfully!')
            return redirect(url_for("SessionView:index"))
        except Exception as error:
            self.slc.set_alert('danger', 'Failed to close session: {0}'.format(str(error)))
            return redirect(url_for('SessionView:close_open_session', session_id=session_id, session_hash=session_hash))

    def restore_deleted_session(self, session_id):
        self.slc.check_roles_and_route(['Administrator'])

        try:
            self.session.restore_deleted_session(session_id)
            self.slc.set_alert('success', 'Session restored successfully!')
            return redirect(url_for('SessionView:index'))
        except Exception as error:
            self.slc.set_alert('danger', 'Failed to restore session: {0}'.format(str(error)))
            return redirect(url_for('SessionView:deleted'))

    @route('/no-cas/checkin/<int:session_id>/<session_hash>/<card_id>', methods=['get', 'post'])
    def student_sign_in(self, session_id, session_hash, card_id):
        semester = self.schedule.get_active_semester()
        # Card id gets passed in as none if not used, otherwise its a 5-digit number
        if card_id != 'cas-auth':  # This is the same regardless of prod/dev
            try:
                student_info = self.wsapi.get_user_from_prox(card_id)
                username = student_info['username']
            except:
                self.slc.set_alert('danger', 'Card not recognized. Please try again or click the button below to enter '
                                             'your Bethel username and password.')
                return redirect(url_for('SessionView:student_attendance_passthrough', session_id=session_id, session_hash=session_hash))
            student = self.user.get_user_by_username(username)

        # No card so now we get the user via CAS
        else:
            if app.config['ENVIRON'] != 'prod':  # If we are in dev env we grab the student selected from the dropdown.
                form = request.form
                student_choice = form.get('selected-student')
                if student_choice == '-1':
                    self.slc.set_alert('danger', 'Invalid Student')
                    return redirect(url_for('SessionView:student_attendance_passthrough', session_id=session_id, session_hash=session_hash))
                student = self.user.get_user(student_choice)
                username = student.username
            else:
                username = flask_session['USERNAME']
                student = self.user.get_user_by_username(username)

        # Check if student exists in the system
        if not student:
            student = self.user.create_user_at_sign_in(username, semester)

        # Check if student has been deactivated at some point
        if student.deletedAt != None:
            self.user.activate_existing_user(student.username)
            self.user.create_user_courses(student.username, student.id, semester.id)

        # Check if student is already signed in
        if self.session.student_currently_signed_in(session_id, student.id):
            self.slc.set_alert('danger', 'Student currently signed in')
            return redirect(url_for('SessionView:student_attendance_passthrough', session_id=session_id, session_hash=session_hash))
        student_courses = self.user.get_student_courses(student.id, semester.id)
        time_in = datetime.now().strftime("%I:%M%p")

        # Check to make sure the user has the Student role, add it if they don't
        self.user.check_or_create_student_role(student.id)

        # clear the session
        self._session_clear_save_alert()

        return render_template('sessions/student_sign_in.html', **locals())

    # This method is CAS authenticated to get the user's info, but none of the other sign in methods are
    @route('/authenticate-sign-in/<session_id>/<session_hash>/<user_type>', methods=['get', 'post'])
    def authenticate_sign_in(self, session_id, session_hash, user_type):
        asdf = "This is jsut here to make a break point"
        return self._logout_open_session(url_for('SessionView:store_username', session_id=session_id, session_hash=session_hash, user_type=user_type, username=flask_session.get('USERNAME')))

    @route('/no-cas/store-username/<session_id>/<session_hash>/<user_type>/<username>', methods=['get'])
    def store_username(self, session_id, session_hash, user_type, username):
        # this entire method is used to store the username, then act as a passthrough
        flask_session['USERNAME'] = username

        if user_type == 'tutor':
            route_url = 'SessionView:tutor_sign_in'
        else:
            route_url = 'SessionView:student_sign_in'

        return redirect(url_for(route_url, session_id=session_id, session_hash=session_hash, card_id='cas-auth'))

    @route('/no-cas/checkin/confirm', methods=['post'])
    def student_sign_in_confirm(self):
        form = request.form
        session_id = form.get('sessionID')
        username = form.get('username')
        student_id = form.get('studentID')
        json_courses = form.get('jsonCourseIDs')
        student_courses = json.loads(json_courses)
        other_course_check = 1 if form.get('otherCourseCheck') == 'true' else 0
        other_course_name = form.get('otherCourseName')
        time_in = form.get('timeIn')
        if not student_courses and other_course_name == '':
            self.slc.set_alert('danger', 'You must pick the courses you are here for or select \'Other\' and fill in the field.')
            # Need to set the username here because it gets cleared, but we need it to reload the page
            flask_session['USERNAME'] = username
            return 'failed'
        self.session.student_sign_in(session_id, student_id, student_courses, other_course_check, other_course_name, time_in)

        return 'success'

    @route('/no-cas/student-sign-out/<session_id>/<student_id>/<session_hash>', methods=['get'])
    def student_sign_out(self, session_id, student_id, session_hash):
        self.session.student_sign_out(session_id, student_id)
        return redirect(url_for('SessionView:student_attendance_passthrough', session_id=session_id, session_hash=session_hash))

    @route('/no-cas/tutor-sign-in/<int:session_id>/<session_hash>/<card_id>', methods=['get', 'post'])
    def tutor_sign_in(self, session_id, session_hash, card_id):
        if card_id != 'cas-auth':  # This is the same regardless of prod/dev
            try:
                tutor_info = self.wsapi.get_user_from_prox(card_id)
            except:
                self.slc.set_alert('danger', 'Card not recognized. Please try again or click the button below to enter '
                                             'your Bethel username and password.')
                return redirect(url_for('SessionView:tutor_attendance_passthrough', session_id=session_id, session_hash=session_hash))
            tutor = self.user.get_user_by_username(tutor_info['username'])
        else:
            if app.config['ENVIRON'] == 'prod':
                tutor = self.user.get_user_by_username(flask_session['USERNAME'])
            else:
                form = request.form
                tutor_id = form.get('selected-tutor')
                if tutor_id == '-1':
                    self.slc.set_alert('danger', 'Invalid Tutor')
                    return redirect(url_for('SessionView:tutor_attendance_passthrough', session_id=session_id, session_hash=session_hash))
                tutor = self.user.get_user(tutor_id)
        if not tutor or not self.user.user_is_tutor(tutor.id):
            self.slc.set_alert('danger', 'This user is not a registered tutor (did you mean to sign in as a student?)')
            return redirect(url_for('SessionView:tutor_attendance_passthrough', session_id=session_id, session_hash=session_hash))
        if self.session.tutor_currently_signed_in(session_id, tutor.id):
            self.slc.set_alert('danger', 'Tutor currently signed in')
            return redirect(url_for('SessionView:tutor_attendance_passthrough', session_id=session_id, session_hash=session_hash))
        self.session.tutor_sign_in(session_id, tutor.id)

        return redirect(url_for('SessionView:tutor_attendance_passthrough', session_id=session_id, session_hash=session_hash))

    @route('/no-cas/tutor-sign-out/<session_id>/<tutor_id>/<session_hash>', methods=['get'])
    def tutor_sign_out(self, session_id, tutor_id, session_hash):
        result = self.session.tutor_sign_out(session_id, tutor_id)
        if not result:
            self.slc.set_alert('danger', 'Tutor sign out failed. Please try again.')
        return redirect(url_for('SessionView:tutor_attendance_passthrough', session_id=session_id, session_hash=session_hash))

    # Verifying here on the back end to hide the encoding for the id card numbers
    # TODO: refactor to redirect from here instead of in the JS
    @route('/no-cas/verify-scanner', methods=['post'])
    def verify_scanner(self):
        form = request.form
        scan = form.get("scan")
        card_id = re.search("\[\[(.+?)\]\]", scan)
        if card_id:
            return card_id.group(1)
        else:
            return 'failed'

    def _logout_open_session(self, service_path):
        # Alerts getting cleared out during open session logouts, so in those cases we're saving the alert.
        self._session_clear_save_alert()

        resp = make_response(redirect(app.config['LOGOUT_URL'] + '?service=' + request.host_url[:-1] + service_path))
        resp.set_cookie('MOD_AUTH_CAS_S', '', expires=0, path='/')
        resp.set_cookie('MOD_AUTH_CAS', '', expires=0, path='/')
        return resp

    def _session_clear_save_alert(self):
        alert = flask_session['ALERT']
        flask_session.clear()
        flask_session['ALERT'] = alert
