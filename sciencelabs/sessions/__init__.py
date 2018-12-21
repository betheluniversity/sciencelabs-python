# Packages
from datetime import datetime
from flask import render_template, redirect, url_for, request, session, json
from flask_classy import FlaskView, route

# Local
from sciencelabs.db_repository.session_functions import Session
from sciencelabs.db_repository.user_functions import User
from sciencelabs.db_repository.schedule_functions import Schedule
from sciencelabs.db_repository.course_functions import Course
from sciencelabs.alerts.alerts import *
from sciencelabs.sciencelabs_controller import requires_auth
from sciencelabs.sciencelabs_controller import ScienceLabsController
from sciencelabs.email_tab import EmailController
from sciencelabs import app


class SessionView(FlaskView):
    def __init__(self):
        self.user = User()
        self.session = Session()
        self.schedule = Schedule()
        self.course = Course()
        self.slc = ScienceLabsController()
        self.email = EmailController()

    def index(self):
        self.slc.check_roles_and_route(['Administrator', 'Lead Tutor'])

        current_alert = get_alert()
        semester = self.schedule.get_active_semester()
        sessions = self.session.get_available_sessions(semester.id)
        open_sessions = self.session.get_open_sessions()
        sessions_and_tutors = {}
        for available_session in sessions:
            sessions_and_tutors[available_session] = self.session.get_session_tutors(available_session.id)
        return render_template('session/available_sessions.html', **locals())

    @route('/closed')
    def closed(self):
        self.slc.check_roles_and_route(['Administrator'])

        current_alert = get_alert()
        sessions = self.session.get_closed_sessions(session['SELECTED-SEMESTER'])
        sessions_and_tutors = {}
        for closed_session in sessions:
            sessions_and_tutors[closed_session] = self.session.get_session_tutors(closed_session.id)
        semester = self.schedule.get_semester(session['SELECTED-SEMESTER'])
        return render_template('session/closed_sessions.html', **locals())

    def create(self):
        self.slc.check_roles_and_route(['Administrator'])

        current_alert = get_alert()
        active_semester = self.schedule.get_active_semester()
        lead_list = self.schedule.get_registered_leads()
        tutor_list = self.schedule.get_registered_tutors()
        course_list = self.course.get_semester_courses(active_semester.id)
        return render_template('session/create_session.html', **locals())

    def deleted(self):
        self.slc.check_roles_and_route(['Administrator'])

        current_alert = get_alert()
        sessions = self.session.get_deleted_sessions(session['SELECTED-SEMESTER'])
        semester = self.schedule.get_semester(session['SELECTED-SEMESTER'])
        sessions_and_tutors = {}
        for closed_session in sessions:
            sessions_and_tutors[closed_session] = self.session.get_session_tutors(closed_session.id)
        return render_template('session/restore_session.html', **locals())

    @route('/edit/<int:session_id>')
    def edit_session(self, session_id):
        self.slc.check_roles_and_route(['Administrator'])

        current_alert = get_alert()
        session_info = self.session.get_session(session_id)
        session_tutors = self.session.get_session_tutors(session_id)
        tutor_names = self.session.get_session_tutor_names(session_id)  # used for a logic check in template
        lead_list = self.schedule.get_registered_leads()  # used for adding tutors to session
        tutor_list = self.schedule.get_registered_tutors()
        session_students = self.session.get_session_students(session_id)
        students_and_courses = {}
        for student in session_students:
            students_and_courses[student] = self.session.get_student_session_courses(session_id, student.id)
        course_list = self.course.get_semester_courses(session['SELECTED-SEMESTER'])
        session_courses = self.session.get_session_courses(session_id)
        return render_template('session/edit_session.html', **locals())

    @route('/attendance/edit/<int:student_id>/<int:session_id>')
    def edit_student(self, student_id, session_id):
        self.slc.check_roles_and_route(['Administrator'])

        student = self.session.get_student_session_info(student_id, session_id)
        student_courses = self.course.get_student_courses(student_id, session['SELECTED-SEMESTER'])
        session_courses = self.session.get_student_session_courses(session_id, student_id)
        other_course = self.session.get_other_course(session_id, student_id)
        current_alert = get_alert()
        return render_template('session/edit_student.html', **locals())

    @route('/attendance/student/<int:session_id>')
    def add_student(self, session_id):
        self.slc.check_roles_and_route(['Administrator'])

        current_alert = get_alert()
        student_list = self.schedule.get_registered_students()
        return render_template('session/add_student.html', **locals())

    @route('/addanon/<int:session_id>')
    def add_anonymous(self, session_id):
        self.slc.check_roles_and_route(['Administrator'])

        current_alert = get_alert()
        session_info = self.session.get_session(session_id)
        return render_template('session/add_anonymous.html', **locals())

    @route('/attendance/tutor/edit/<int:tutor_id>/<int:session_id>')
    def edit_tutor(self, tutor_id, session_id):
        self.slc.check_roles_and_route(['Administrator'])

        current_alert = get_alert()
        tutor = self.session.get_tutor_session_info(tutor_id, session_id)
        return render_template('session/edit_tutor.html', **locals())

    @route('/addattendance/tutor/<int:session_id>')
    def add_tutor(self, session_id):
        self.slc.check_roles_and_route(['Administrator'])

        current_alert = get_alert()
        tutor_list = self.schedule.get_registered_tutors()
        return render_template('session/add_tutor.html', **locals())

    def delete_session(self, session_id):
        self.slc.check_roles_and_route(['Administrator'])

        current_alert = get_alert()
        session_info = self.session.get_session(session_id)
        return render_template('session/delete_session.html', **locals())

    def delete_confirmed(self, session_id):
        self.slc.check_roles_and_route(['Administrator'])

        try:
            self.session.delete_session(session_id)
            set_alert('success', 'Session deleted successfully!')
            return redirect(url_for('SessionView:closed'))
        except Exception as error:
            set_alert('danger', 'Failed to delete session: ' + str(error))
            return redirect(url_for('SessionView:delete_session', session_id=session_id))

    @route('/save_session_edits', methods=['post'])
    def save_session_edits(self):
        self.slc.check_roles_and_route(['Administrator'])

        try:
            form = request.form
            session_id = form.get('session-id')
            name = form.get('name')
            room = form.get('room')
            semester_id = form.get('semester-select')
            date = form.get('date')
            db_date = datetime.strptime(date, "%a %b %d %Y").strftime("%Y-%m-%d")
            scheduled_start = form.get('scheduled-start') or None
            scheduled_end = form.get('scheduled-end') or None
            leads = form.getlist('leads')
            tutors = form.getlist('tutors')
            actual_start = form.get('actual-start') or None
            actual_end = form.get('actual-end') or None
            courses = form.getlist('courses')
            comments = form.get('comments')
            anon_students = form.get('anon-students')
            # Returns True if successful
            success = self.session.edit_session(session_id, semester_id, db_date, scheduled_start, scheduled_end,
                                                actual_start, actual_end, room, comments, anon_students, name, leads,
                                                tutors, courses)
            if success:
                set_alert('success', 'Session edited successfully!')
                return redirect(url_for('SessionView:closed'))
            else:
                raise Exception
        except Exception as error:
            set_alert('danger', 'Failed to edit session: ' + str(error))
            return redirect(url_for('SessionView:edit_session', session_id=session_id))


    @route('/save_student_edits/<int:session_id>', methods=['post'])
    def save_student_edits(self, session_id):
        self.slc.check_roles_and_route(['Administrator'])

        try:
            form = request.form
            student_id = form.get('student-id')
            time_in = form.get('time-in') or None
            time_out = form.get('time-out') or None
            student_courses = form.getlist('course')
            other_check = form.get('other-check')
            other_course = form.get('other-name')
            if not other_check:
                other_course = None
            # Returns True if successful
            success = self.session.edit_student_session(session_id, student_id, time_in, time_out, other_course,
                                                        student_courses)
            if success:
                set_alert('success', 'Edited student successfully!')
                return redirect(url_for('SessionView:edit_session', session_id=session_id))
            else:
                raise Exception
        except Exception as error:
            set_alert('danger', 'Failed to edit student: ' + str(error))
            return redirect(url_for('SessionView:edit_student', student_id=student_id, session_id=session_id))

    @route('/save_tutor_edits', methods=['post'])
    def save_tutor_edits(self):
        self.slc.check_roles_and_route(['Administrator'])

        try:
            form = request.form
            session_id = form.get('session-id')
            tutor_id = form.get('tutor-id')
            time_in = form.get('time-in') or None
            time_out = form.get('time-out') or None
            lead_check = form.get('lead')
            lead = 0
            if lead_check:
                lead = 1
            self.session.edit_tutor_session(session_id, tutor_id, time_in, time_out, lead)
            set_alert('success', 'Tutor edited successfully!')
            return redirect(url_for('SessionView:edit_session', session_id=session_id))
        except Exception as error:
            set_alert('danger', 'Failed to edit tutor: ' + str(error))
            return redirect(url_for('SessionView:edit_tutor', tutor_id=tutor_id, session_id=session_id))

    def delete_student_from_session(self, student_id, session_id):
        self.slc.check_roles_and_route(['Administrator'])

        try:
            self.session.delete_student_from_session(student_id, session_id)
            set_alert('success', 'Student deleted successfully!')
        except Exception as error:
            set_alert('danger', 'Failed to delete student: ' + str(error))
        return redirect(url_for('SessionView:edit_session', session_id=session_id))

    def delete_tutor_from_session(self, tutor_id, session_id):
        self.slc.check_roles_and_route(['Administrator'])

        try:
            self.session.delete_tutor_from_session(tutor_id, session_id)
            set_alert('success', 'Tutor deleted successfully!')
        except Exception as error:
            set_alert('danger', 'Failed to delete tutor: ' + str(error))
        return redirect(url_for('SessionView:edit_session', session_id=session_id))

    @route('/add_student_submit', methods=['post'])
    def add_student_submit(self):
        self.slc.check_roles_and_route(['Administrator'])

        try:
            form = request.form
            session_id = form.get('session-id')
            student_id = form.get('choose-student')
            self.session.add_student_to_session(session_id, student_id)
            set_alert('success', 'Student added successfully!')
            return redirect(url_for('SessionView:edit_session', session_id=session_id))
        except Exception as error:
            set_alert('danger', 'Failed to add student: ' + str(error))
            return redirect(url_for('SessionView:add_student', session_id=session_id))

    @route('/add_anon_submit', methods=['post'])
    def add_anon_submit(self):
        self.slc.check_roles_and_route(['Administrator'])

        try:
            form = request.form
            session_id = form.get('session-id')
            anon_students = form.get('anon-students')
            self.session.add_anonymous_to_session(session_id, anon_students)
            set_alert('success', 'Anonymous students edited successfully!')
            return redirect(url_for('SessionView:edit_session', session_id=session_id))
        except Exception as error:
            set_alert('danger', 'Failed to edit anonymous students: ' + str(error))
            return redirect(url_for('SessionView:add_anonymous', session_id=session_id))

    @route('/add_tutor_submit', methods=['post'])
    def add_tutor_submit(self):
        self.slc.check_roles_and_route(['Administrator'])

        try:
            form = request.form
            session_id = form.get('session-id')
            tutor_id = form.get('choose-tutor')
            time_in = form.get('time-in') or None
            time_out = form.get('time-out') or None
            lead_check = form.get('lead')
            lead = 0
            if lead_check:
                lead = 1
            self.session.add_tutor_to_session(session_id, tutor_id, time_in, time_out, lead)
            set_alert('success', 'Tutor added successfully!')
            return redirect(url_for('SessionView:edit_session', session_id=session_id))
        except Exception as error:
            set_alert('danger', 'Failed to add tutor: ' + str(error))
            return redirect(url_for('SessionView:add_tutor', session_id=session_id))

    @route('/create_session_submit', methods=['post'])
    def create_session_submit(self):
        self.slc.check_roles_and_route(['Administrator'])

        try:
            form = request.form
            name = form.get('name')
            room = form.get('room')
            semester_id = form.get('semester-select')
            date = form.get('date')
            db_date = datetime.strptime(date, "%a %b %d %Y").strftime("%Y-%m-%d")
            scheduled_start = form.get('scheduled-start') or None
            scheduled_end = form.get('scheduled-end') or None
            leads = form.getlist('choose-leads')
            tutors = form.getlist('choose-tutors')
            actual_start = form.get('actual-start') or None
            actual_end = form.get('actual-end') or None
            courses = form.getlist('courses')
            comments = form.get('comments')
            anon_students = form.get('anon-students')
            if leads == []:
                set_alert('danger', 'You must choose a Lead Tutor')
                return redirect(url_for('SessionView:create'))
            # Returns True if successful
            success = self.session.create_new_session(semester_id, db_date, scheduled_start, scheduled_end,
                                                      actual_start, actual_end, room, comments, anon_students, name,
                                                      leads, tutors, courses)
            if success:
                set_alert('success', 'Session created successfully!')
                return redirect(url_for('SessionView:closed'))
            else:
                raise Exception
        except Exception as error:
            set_alert('danger', 'Failed to create session: ' + str(error))
            return redirect(url_for('SessionView:create'))

    @route('/view/<int:session_id>')
    def view_session(self, session_id):
        session_students = self.session.get_session_students(session_id)
        students_and_courses = {}
        for student in session_students:
            students_and_courses[student] = self.session.get_student_session_courses(session_id, student.id)
        session_tutors = self.session.get_session_tutors(session_id)
        return render_template('session/view_session.html', **locals())

    # TODO: hash and CAS authentications

    def open_session(self, session_id, session_hash):
        self.slc.check_roles_and_route(['Administrator', 'Lead Tutor'])

        opener = self.user.get_user_by_username(session['USERNAME'])
        self.session.start_open_session(session_id, opener.id)
        self.session.tutor_sign_in(session_id, opener.id)
        return redirect(url_for('SessionView:student_attendance', session_id=session_id, session_hash=session_hash))

    @route('/student_attendance/<int:session_id>/<session_hash>', methods=['get', 'post'])
    def student_attendance(self, session_id, session_hash):
        self.slc.check_roles_and_route(['Administrator', 'Lead Tutor'])

        current_alert = get_alert()
        session_info = self.session.get_session(session_id)
        students = self.session.get_session_students(session_id)
        # TODO: Talk to Caleb - this is not how we do it in other places, but this is probably better (preserves MVC)
        students_and_courses = {}
        for student in students:
            students_and_courses[student] = self.session.get_student_session_courses(session_id, student.id)
        all_students = self.user.get_all_current_students()
        env = app.config['ENVIRON']
        return render_template('session/student_attendance.html', **locals())

    @route('/tutor_attendance/<int:session_id>/<session_hash>', methods=['get', 'post'])
    def tutor_attendance(self, session_id, session_hash):
        self.slc.check_roles_and_route(['Administrator', 'Lead Tutor'])

        current_alert = get_alert()
        session_info = self.session.get_session(session_id)
        course_info = self.course.get_active_course_info(session_info.semester_id)
        tutors = self.session.get_session_tutors(session_id)
        all_tutors = self.user.get_all_current_tutors()
        env = app.config['ENVIRON']
        return render_template('session/tutor_attendance.html', **locals())

    @route('/close_session/<int:session_id>/<session_hash>', methods=['get', 'post'])
    def close_open_session(self, session_id, session_hash):
        self.slc.check_roles_and_route(['Administrator', 'Lead Tutor'])

        current_alert = get_alert()
        session_info = self.session.get_session(session_id)
        course_info = self.course.get_active_course_info(session_info.semester_id)
        return render_template('session/close_open_session.html', **locals())

    @route('/confirm_close', methods=['post'])
    def confirm_close(self):
        self.slc.check_roles_and_route(['Administrator', 'Lead Tutor'])

        try:
            form = request.form
            session_id = form.get('session-id')
            session_hash = form.get('session-hash')
            comments = form.get('comments')
            self.session.close_open_session(session_id, comments)
            # TODO STILL HAVE TO CONNECT THIS, BUT EVERYTHING SHOULD BE SETUP
            # Send the email here?
            # Use these variables to do so
            ##################
            user = self.user
            session_ = self.session
            courses = self.course
            tutors = session_.get_session_tutors(session_id)
            session_students = session_.get_session_students(session_id)
            session_courses = session_.get_session_courses(session_id)
            sess = session_.get_session(session_id)
            ##################
            subject = "{" + app.config['LAB_TITLE'] + "} " + sess.name + " (" + sess.date.strftime('%m/%d/%Y') + ")"
            recipients = app.config['TEST_EMAILS'] # TODO update with lab admins and profs
            self.email.send_message(subject, render_template('session/email.html', **locals()), recipients, None, True)
            set_alert('success', 'Session closed successfully!')
            return redirect(url_for("SessionView:index"))
        except Exception as error:
            set_alert('danger', 'Failed to close session: ' + str(error))
            return redirect(url_for('SessionView:close_open_session', session_id=session_id, session_hash=session_hash))

    def restore_deleted_session(self, session_id):
        self.slc.check_roles_and_route(['Administrator'])

        try:
            self.session.restore_deleted_session(session_id)
            set_alert('success', 'Session restored successfully!')
            return redirect(url_for('SessionView:index'))
        except Exception as error:
            set_alert('danger', 'Failed to restore session: ' + str(error))
            return redirect(url_for('SessionView:deleted'))

    @route('/checkin/<int:session_id>/<session_hash>', methods=['get', 'post'])
    def student_sign_in(self, session_id, session_hash):
        semester = self.schedule.get_active_semester()
        if app.config['ENVIRON'] == 'prod':
            username = session['USERNAME']
            user = self.user.get_user_by_username(username)
            if not user:
                user = self.user.create_user_at_sign_in(username, semester)
        else:  # If we are in dev env we grab the student selected from the dropdown.
            form = request.form
            student = form.get('selected-student')
            if student == '-1':
                set_alert('danger', 'Invalid Student')
                return redirect(url_for('SessionView:student_attendance', session_id=session_id, session_hash=session_hash))
            user = self.user.get_user(student)
            session['STUDENT-SIGN-IN-TEST'] = True
            session['PREVIOUS-USERNAME'] = session['USERNAME']
            session['PREVIOUS-ROLES'] = session['USER-ROLES']
            session['PREVIOUS-NAME'] = session['NAME']

            session['USERNAME'] = user.username
            session['NAME'] = user.firstName + ' ' + user.lastName
            session['USER-ROLES'] = []
            user_roles = User().get_user_roles(user.id)
            for role in user_roles:
                session['USER-ROLES'].append(role.name)

        if self.session.student_currently_signed_in(session_id, user.id):
            set_alert('danger', 'Student currently signed in')
            return redirect(url_for('SessionView:student_attendance', session_id=session_id, session_hash=session_hash))
        student_courses = self.user.get_student_courses(user.id, semester.id)
        time_in = datetime.now().strftime("%I:%M%p")
        return render_template('session/student_sign_in.html', **locals())

    @route('/checkin/confirm', methods=['post'])
    def student_sign_in_confirm(self):
        form = request.form
        session_id = form.get('sessionID')
        session_hash = form.get('sessionHash')
        student_id = form.get('studentID')
        json_courses = form.get('jsonCourseIDs')
        student_courses = json.loads(json_courses)
        other_course_check = 1 if form.get('otherCourseCheck') == 'true' else 0
        other_course_name = form.get('otherCourseName')
        time_in = form.get('timeIn')
        if session['STUDENT-SIGN-IN-TEST']:
            session['STUDENT-SIGN-IN-TEST'] = False
            session['USERNAME'] = session['PREVIOUS-USERNAME']
            session['USER-ROLES'] = session['PREVIOUS-ROLES']
            session['NAME'] = session['PREVIOUS-NAME']
        else:
            # TODO MIGHT HAVE TO CHANGE THIS FROM CLEARED TO ONLY CLEARING SPECIFIC THINGS?
            session.clear()

        self.session.student_sign_in(session_id, student_id, student_courses, other_course_check, other_course_name, time_in)
        return redirect(url_for('SessionView:student_attendance', session_id=session_id, session_hash=session_hash))

    def student_sign_out(self, session_id, student_id, session_hash):
        self.session.student_sign_out(session_id, student_id)
        return redirect(url_for('SessionView:student_attendance', session_id=session_id, session_hash=session_hash))

    @route('/tutor_sign_in/<int:session_id>/<session_hash>', methods=['post'])
    def tutor_sign_in(self, session_id, session_hash):
        if app.config['ENVIRON'] == 'prod':
            username = session['USERNAME']
            user = self.user.get_user_by_username(username)
        else:
            form = request.form
            tutor_id = form.get('selected-tutor')
            if tutor_id == '-1':
                set_alert('danger', 'Invalid Tutor')
                return redirect(url_for('SessionView:tutor_attendance', session_id=session_id, session_hash=session_hash))
            user = self.user.get_user(tutor_id)
        if self.session.tutor_currently_signed_in(session_id, user.id):
            set_alert('danger', 'Tutor currently signed in')
            return redirect(url_for('SessionView:tutor_attendance', session_id=session_id, session_hash=session_hash))
        self.session.tutor_sign_in(session_id, user.id)
        return redirect(url_for('SessionView:tutor_attendance', session_id=session_id, session_hash=session_hash))

    def tutor_sign_out(self, session_id, tutor_id, session_hash):
        self.session.tutor_sign_out(session_id, tutor_id)
        return redirect(url_for('SessionView:tutor_attendance', session_id=session_id, session_hash=session_hash))

    @requires_auth
    @route('/cron_close_sessions', methods=['get'])
    def cron_close_sessions(self):
        try:
            # TODO: Email here too
            return self.session.close_open_sessions_cron()
        except Exception as error:
            return 'failed: ' + str(error)
