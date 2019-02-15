import re

# Packages
from datetime import datetime
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
        sessions_and_tutors = {}
        for available_session in sessions:
            sessions_and_tutors[available_session] = self.session.get_session_tutors(available_session.id)
        return render_template('sessions/available_sessions.html', **locals())

    @route('/closed')
    def closed(self):
        self.slc.check_roles_and_route(['Administrator'])

        sessions = self.session.get_closed_sessions(flask_session['SELECTED-SEMESTER'])
        sessions_and_tutors = {}
        for closed_session in sessions:
            sessions_and_tutors[closed_session] = self.session.get_session_tutors(closed_session.id)
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
        sessions_and_tutors = {}
        for closed_session in sessions:
            sessions_and_tutors[closed_session] = self.session.get_session_tutors(closed_session.id)
        return render_template('sessions/restore_session.html', **locals())

    @route('/edit/<int:session_id>')
    def edit_session(self, session_id):
        self.slc.check_roles_and_route(['Administrator'])

        session_info = self.session.get_session(session_id)
        session_tutors = self.session.get_session_tutors(session_id)
        lead_ids = self.session.get_session_lead_ids(session_id)
        tutor_ids = self.session.get_session_tutor_ids(session_id)
        lead_list = self.schedule.get_registered_leads()  # used for adding tutors to session
        tutor_list = self.schedule.get_registered_tutors()
        session_students = self.session.get_session_students(session_id)
        students_and_courses = {}
        for student in session_students:
            students_and_courses[student] = self.session.get_student_session_courses(session_id, student.id)
        course_list = self.course.get_semester_courses(flask_session['SELECTED-SEMESTER'])
        session_courses = self.session.get_session_courses(session_id)
        return render_template('sessions/edit_session.html', **locals())

    @route('/attendance/edit/<int:student_id>/<int:session_id>')
    def edit_student(self, student_id, session_id):
        self.slc.check_roles_and_route(['Administrator'])

        student = self.session.get_student_session_info(student_id, session_id)
        student_courses = self.course.get_student_courses(student_id, flask_session['SELECTED-SEMESTER'])
        session_courses = self.session.get_student_session_courses(session_id, student_id)
        other_course = self.session.get_other_course(session_id, student_id)
        return render_template('sessions/edit_student.html', **locals())

    @route('/attendance/student/<int:session_id>')
    def add_student(self, session_id):
        self.slc.check_roles_and_route(['Administrator'])

        student_list = self.schedule.get_registered_students()
        return render_template('sessions/add_student.html', **locals())

    @route('/addanon/<int:session_id>')
    def add_anonymous(self, session_id):
        self.slc.check_roles_and_route(['Administrator'])

        session_info = self.session.get_session(session_id)
        return render_template('sessions/add_anonymous.html', **locals())

    @route('/attendance/tutor/edit/<int:tutor_id>/<int:session_id>')
    def edit_tutor(self, tutor_id, session_id):
        self.slc.check_roles_and_route(['Administrator'])

        tutor = self.session.get_tutor_session_info(tutor_id, session_id)
        return render_template('sessions/edit_tutor.html', **locals())

    @route('/addattendance/tutor/<int:session_id>')
    def add_tutor(self, session_id):
        self.slc.check_roles_and_route(['Administrator'])

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
            self.slc.set_alert('danger', 'Failed to delete session: ' + str(error))
            return redirect(url_for('SessionView:delete_session', session_id=session_id))

    @route('/save_session_edits', methods=['post'])
    def save_session_edits(self):
        self.slc.check_roles_and_route(['Administrator'])

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
        try:
            # Returns True if successful
            self.session.edit_session(session_id, semester_id, db_date, scheduled_start, scheduled_end,
                                                actual_start, actual_end, room, comments, anon_students, name, leads,
                                                tutors, courses)
            self.slc.set_alert('success', 'Session edited successfully!')
            return redirect(url_for('SessionView:closed'))
        except Exception as error:
            self.slc.set_alert('danger', 'Failed to edit session: ' + str(error))
            return redirect(url_for('SessionView:edit_session', session_id=session_id))

    @route('/save_student_edits/<int:session_id>', methods=['post'])
    def save_student_edits(self, session_id):
        self.slc.check_roles_and_route(['Administrator'])

        form = request.form
        student_id = form.get('student-id')
        time_in = form.get('time-in') or None
        time_out = form.get('time-out') or None
        student_courses = form.getlist('course')
        other_check = form.get('other-check')
        other_course = form.get('other-name')
        if not other_check:
            other_course = None
        try:
            # Returns True if successful
            self.session.edit_student_session(session_id, student_id, time_in, time_out, other_course,
                                                        student_courses)
            self.slc.set_alert('success', 'Edited student successfully!')
            return redirect(url_for('SessionView:edit_session', session_id=session_id))
        except Exception as error:
            self.slc.set_alert('danger', 'Failed to edit student: ' + str(error))
            return redirect(url_for('SessionView:edit_student', student_id=student_id, session_id=session_id))

    @route('/save_tutor_edits', methods=['post'])
    def save_tutor_edits(self):
        self.slc.check_roles_and_route(['Administrator'])

        form = request.form
        session_id = form.get('session-id')
        tutor_id = form.get('tutor-id')
        time_in = form.get('time-in') or None
        time_out = form.get('time-out') or None
        lead_check = form.get('lead')
        lead = 0
        if lead_check:
            lead = 1
        try:
            self.session.edit_tutor_session(session_id, tutor_id, time_in, time_out, lead)
            self.slc.set_alert('success', 'Tutor edited successfully!')
            return redirect(url_for('SessionView:edit_session', session_id=session_id))
        except Exception as error:
            self.slc.set_alert('danger', 'Failed to edit tutor: ' + str(error))
            return redirect(url_for('SessionView:edit_tutor', tutor_id=tutor_id, session_id=session_id))

    def delete_student_from_session(self, student_id, session_id):
        self.slc.check_roles_and_route(['Administrator'])

        try:
            self.session.delete_student_from_session(student_id, session_id)
            self.slc.set_alert('success', 'Student deleted successfully!')
        except Exception as error:
            self.slc.set_alert('danger', 'Failed to delete student: ' + str(error))
        return redirect(url_for('SessionView:edit_session', session_id=session_id))

    def delete_tutor_from_session(self, tutor_id, session_id):
        self.slc.check_roles_and_route(['Administrator'])

        try:
            self.session.delete_tutor_from_session(tutor_id, session_id)
            self.slc.set_alert('success', 'Tutor deleted successfully!')
        except Exception as error:
            self.slc.set_alert('danger', 'Failed to delete tutor: ' + str(error))
        return redirect(url_for('SessionView:edit_session', session_id=session_id))

    @route('/add_student_submit', methods=['post'])
    def add_student_submit(self):
        self.slc.check_roles_and_route(['Administrator'])

        form = request.form
        session_id = form.get('session-id')
        student_id = form.get('choose-student')
        try:
            self.session.add_student_to_session(session_id, student_id)
            self.slc.set_alert('success', 'Student added successfully!')
            return redirect(url_for('SessionView:edit_session', session_id=session_id))
        except Exception as error:
            self.slc.set_alert('danger', 'Failed to add student: ' + str(error))
            return redirect(url_for('SessionView:add_student', session_id=session_id))

    @route('/add_anon_submit', methods=['post'])
    def add_anon_submit(self):
        self.slc.check_roles_and_route(['Administrator'])

        form = request.form
        session_id = form.get('session-id')
        anon_students = form.get('anon-students')
        try:
            self.session.add_anonymous_to_session(session_id, anon_students)
            self.slc.set_alert('success', 'Anonymous students edited successfully!')
            return redirect(url_for('SessionView:edit_session', session_id=session_id))
        except Exception as error:
            self.slc.set_alert('danger', 'Failed to edit anonymous students: ' + str(error))
            return redirect(url_for('SessionView:add_anonymous', session_id=session_id))

    @route('/add_tutor_submit', methods=['post'])
    def add_tutor_submit(self):
        self.slc.check_roles_and_route(['Administrator'])

        form = request.form
        session_id = form.get('session-id')
        tutor_id = form.get('choose-tutor')
        time_in = form.get('time-in') or None
        time_out = form.get('time-out') or None
        lead_check = form.get('lead')
        lead = 0
        if lead_check:
            lead = 1
        try:
            self.session.add_tutor_to_session(session_id, tutor_id, time_in, time_out, lead)
            self.slc.set_alert('success', 'Tutor added successfully!')
            return redirect(url_for('SessionView:edit_session', session_id=session_id))
        except Exception as error:
            self.slc.set_alert('danger', 'Failed to add tutor: ' + str(error))
            return redirect(url_for('SessionView:add_tutor', session_id=session_id))

    @route('/create_session_submit', methods=['post'])
    def create_session_submit(self):
        self.slc.check_roles_and_route(['Administrator'])

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
            self.slc.set_alert('danger', 'You must choose a Lead Tutor')
            return redirect(url_for('SessionView:create'))
        try:
            # Returns True if successful
            self.session.create_new_session(semester_id, db_date, scheduled_start, scheduled_end,
                                                      actual_start, actual_end, room, comments, anon_students, name,
                                                      leads, tutors, courses)
            self.slc.set_alert('success', 'Session created successfully!')
            return redirect(url_for('SessionView:closed'))
        except Exception as error:
            self.slc.set_alert('danger', 'Failed to create session: ' + str(error))
            return redirect(url_for('SessionView:create'))

    @route('/view/<int:session_id>')
    def view_session(self, session_id):
        session_students = self.session.get_session_students(session_id)
        students_and_courses = {}
        for student in session_students:
            students_and_courses[student] = self.session.get_student_session_courses(session_id, student.id)
        session_tutors = self.session.get_session_tutors(session_id)
        return render_template('sessions/view_session.html', **locals())

    def open_session(self, session_id, session_hash):
        self.slc.check_roles_and_route(['Administrator', 'Lead Tutor'])

        lab_session = self.session.get_session(session_id)
        opener = self.user.get_user_by_username(flask_session['USERNAME'])
        self.session.start_open_session(session_id, opener.id)
        self.session.tutor_sign_in(session_id, opener.id)
        self.slc.set_alert('success', 'Session ' + lab_session.name + ' (' + lab_session.date.strftime('%m/%d/%Y') +
                           ') opened successfully')
        self.logout()
        return redirect(url_for('SessionView:student_attendance', session_id=session_id, session_hash=session_hash))

    @route('/student-attendance/<int:session_id>/<session_hash>', methods=['get', 'post'])
    def student_attendance(self, session_id, session_hash):
        session_info = self.session.get_session(session_id)
        students = self.session.get_session_students(session_id)
        students_and_courses = {}
        for student in students:
            students_and_courses[student] = self.session.get_student_session_courses(session_id, student.id)
        # This is for development - allows us to pick a student to sign in as
        all_students = self.user.get_all_current_students()
        env = app.config['ENVIRON']
        self.logout()
        return render_template('sessions/student_attendance.html', **locals())

    @route('/tutor-attendance/<int:session_id>/<session_hash>', methods=['get', 'post'])
    def tutor_attendance(self, session_id, session_hash):
        session_info = self.session.get_session(session_id)
        course_info = self.course.get_active_course_info()
        tutors = self.session.get_session_tutors(session_id)
        # This is for development - allows us to pick a tutor to sign in as
        all_tutors = self.user.get_all_current_tutors()
        env = app.config['ENVIRON']
        self.logout()
        return render_template('sessions/tutor_attendance.html', **locals())

    @route('/close_session/<int:session_id>/<session_hash>', methods=['get', 'post'])
    def close_open_session(self, session_id, session_hash):
        if app.config['ENVIRON'] != 'prod':
            user = self.user.get_user_by_username(app.config['TEST_USERNAME'])
        else:
            user = self.user.get_user_by_username(request.environ.get('REMOTE_USER'))
        flask_session['USERNAME'] = user.username
        flask_session['NAME'] = user.firstName + ' ' + user.lastName
        flask_session['USER-ROLES'] = []
        user_roles = self.user.get_user_roles(user.id)
        for role in user_roles:
            flask_session['USER-ROLES'].append(role.name)
        session_info = self.session.get_session(session_id)
        course_info = self.course.get_active_course_info()
        return render_template('sessions/close_open_session.html', **locals())

    @route('/confirm_close', methods=['post'])
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
            self.slc.set_alert('danger', 'Failed to close session: ' + str(error))
            return redirect(url_for('SessionView:close_open_session', session_id=session_id, session_hash=session_hash))

    def restore_deleted_session(self, session_id):
        self.slc.check_roles_and_route(['Administrator'])

        try:
            self.session.restore_deleted_session(session_id)
            self.slc.set_alert('success', 'Session restored successfully!')
            return redirect(url_for('SessionView:index'))
        except Exception as error:
            self.slc.set_alert('danger', 'Failed to restore session: ' + str(error))
            return redirect(url_for('SessionView:deleted'))

    @route('/checkin/<int:session_id>/<session_hash>/<card_id>', methods=['get', 'post'])
    def student_sign_in(self, session_id, session_hash, card_id):
        semester = self.schedule.get_active_semester()
        # Card id gets passed in as none if not used, otherwise its a 5-digit number
        if card_id != 'cas-auth':  # This is the same regardless of prod/dev
            try:
                user_info = self.wsapi.get_user_from_prox(card_id)
            except:
                self.slc.set_alert('danger', 'Card not recognized')
                return redirect(url_for('SessionView:student_attendance', session_id=session_id, session_hash=session_hash))
            user = self.user.get_user_by_username(user_info['username'])
            if not user:
                user = self.user.create_user_at_sign_in(user_info['username'], semester)
        # No card so now we get the user via CAS
        else:
            if app.config['ENVIRON'] != 'prod':  # If we are in dev env we grab the student selected from the dropdown.
                form = request.form
                student = form.get('selected-student')
                if student == '-1':
                    self.slc.set_alert('danger', 'Invalid Student')
                    return redirect(url_for('SessionView:student_attendance', session_id=session_id, session_hash=session_hash))
                user = self.user.get_user(student)
            else:
                user = self.user.get_user_by_username(flask_session['USERNAME'])
        if self.session.student_currently_signed_in(session_id, user.id):
            self.slc.set_alert('danger', 'Student currently signed in')
            return redirect(url_for('SessionView:student_attendance', session_id=session_id, session_hash=session_hash))
        student_courses = self.user.get_student_courses(user.id, semester.id)
        time_in = datetime.now().strftime("%I:%M%p")
        return render_template('sessions/student_sign_in.html', **locals())

    # This method is CAS authenticated to get the user's info, but none of the other sign in methods are
    @route('/authenticate-sign-in/<session_id>/<session_hash>/<user>', methods=['get', 'post'])
    def authenticate_sign_in(self, session_id, session_hash, user):
        if user == 'tutor':
            return redirect(url_for('SessionView:tutor_sign_in', session_id=session_id, session_hash=session_hash, card_id='cas-auth'))
        else:
            return redirect(url_for('SessionView:student_sign_in', session_id=session_id, session_hash=session_hash, card_id='cas-auth'))

    @route('/checkin/confirm', methods=['post'])
    def student_sign_in_confirm(self):
        form = request.form
        session_id = form.get('sessionID')
        session_hash = form.get('sessionHash')
        card_id = form.get('cardID')
        student_id = form.get('studentID')
        json_courses = form.get('jsonCourseIDs')
        student_courses = json.loads(json_courses)
        other_course_check = 1 if form.get('otherCourseCheck') == 'true' else 0
        other_course_name = form.get('otherCourseName')
        time_in = form.get('timeIn')
        if student_courses == [] and other_course_name == '':
            self.slc.set_alert('danger', 'You must pick the courses you are here for or select \'Other\' and fill in the field.')
            return redirect(url_for('SessionView:student_sign_in', session_id=session_id, session_hash=session_hash, card_id=card_id))
        self.session.student_sign_in(session_id, student_id, student_courses, other_course_check, other_course_name, time_in)
        self.logout()
        return redirect(url_for('SessionView:student_attendance', session_id=session_id, session_hash=session_hash))

    def student_sign_out(self, session_id, student_id, session_hash):
        self.session.student_sign_out(session_id, student_id)
        return redirect(url_for('SessionView:student_attendance', session_id=session_id, session_hash=session_hash))

    @route('/tutor_sign_in/<int:session_id>/<session_hash>/<card_id>', methods=['get', 'post'])
    def tutor_sign_in(self, session_id, session_hash, card_id):
        if card_id != 'cas-auth':  # This is the same regardless of prod/dev
            try:
                user_info = self.wsapi.get_user_from_prox(card_id)
            except:
                self.slc.set_alert('danger', 'Card not recognized')
                return redirect(url_for('SessionView:tutor_attendance', session_id=session_id, session_hash=session_hash))
            user = self.user.get_user_by_username(user_info['username'])
        else:
            if app.config['ENVIRON'] == 'prod':
                username = request.environ.get('REMOTE_USER')
                user = self.user.get_user_by_username(username)
            else:
                form = request.form
                tutor_id = form.get('selected-tutor')
                if tutor_id == '-1':
                    self.slc.set_alert('danger', 'Invalid Tutor')
                    return redirect(url_for('SessionView:tutor_attendance', session_id=session_id, session_hash=session_hash))
                user = self.user.get_user(tutor_id)
        if not user or not self.user.user_is_tutor(user.id):
            self.slc.set_alert('danger', 'This user is not a registered tutor (did you mean to sign in as a student?)')
            return redirect(url_for('SessionView:tutor_attendance', session_id=session_id, session_hash=session_hash))
        if self.session.tutor_currently_signed_in(session_id, user.id):
            self.slc.set_alert('danger', 'Tutor currently signed in')
            return redirect(url_for('SessionView:tutor_attendance', session_id=session_id, session_hash=session_hash))
        self.session.tutor_sign_in(session_id, user.id)
        self.logout()
        return redirect(url_for('SessionView:tutor_attendance', session_id=session_id, session_hash=session_hash))

    def tutor_sign_out(self, session_id, tutor_id, session_hash):
        self.session.tutor_sign_out(session_id, tutor_id)
        return redirect(url_for('SessionView:tutor_attendance', session_id=session_id, session_hash=session_hash))

    @route('/verify_scanner', methods=['post'])
    def verify_scanner(self):
        form = request.form
        scan = form.get("scan")
        card_id = re.search("\[\[(.+?)\]\]", scan)
        if card_id:
            return card_id.group(1)
        else:
            return 'failed'

    # This logout method is specific to the open session
    def logout(self):
        # Alerts getting cleared out during open session logouts, so in those cases we're saving the alert.
        alert = flask_session['ALERT']
        flask_session.clear()
        flask_session['ALERT'] = alert

        resp = make_response(redirect(app.config['LOGOUT_URL']))
        resp.set_cookie('MOD_AUTH_CAS_S', '', expires=0)
        resp.set_cookie('MOD_AUTH_CAS', '', expires=0)
        return resp
