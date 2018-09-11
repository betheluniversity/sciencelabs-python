# Packages
from datetime import datetime
from flask import render_template, redirect, url_for, request, session
from flask_classy import FlaskView, route

# Local
from sciencelabs.db_repository.session_functions import Session
from sciencelabs.db_repository.user_functions import User
from sciencelabs.db_repository.schedule_functions import Schedule
from sciencelabs.db_repository.course_functions import Course
from sciencelabs.alerts.alerts import *
from app_settings import app_settings



class SessionView(FlaskView):
    def __init__(self):
        self.user = User()
        self.session = Session()
        self.schedule = Schedule()
        self.course = Course()

    def index(self):
        current_alert = get_alert()
        semester = self.schedule.get_active_semester()
        semester_list = self.schedule.get_semesters()
        sessions = self.session.get_available_sessions(semester.id)
        session_tutors = self.session
        return render_template('session/available_sessions.html', **locals())

    @route('/closed')
    def closed(self):
        sessions = self.session.get_closed_sessions(session['SELECTED-SEMESTER'])
        current_alert = get_alert()
        session_tutors = self.session
        semester = self.schedule.get_semester(session['SELECTED-SEMESTER'])
        semester_list = session['SEMESTER-LIST']
        return render_template('session/closed_sessions.html', **locals())

    def create(self):
        current_alert = get_alert()
        active_semester = self.schedule.get_active_semester()
        semester_list = self.schedule.get_semesters()
        lead_list = self.schedule.get_registered_leads()
        tutor_list = self.schedule.get_registered_tutors()
        course_list = self.course.get_semester_courses(active_semester.id)
        return render_template('session/create_session.html', **locals())

    def deleted(self):
        sessions = self.session.get_deleted_sessions(session['SELECTED-SEMESTER'])
        semester = self.schedule.get_semester(session['SELECTED-SEMESTER'])
        semester_list = session['SEMESTER-LIST']
        current_alert = get_alert()
        session_tutors = self.session
        return render_template('session/restore_session.html', **locals())

    @route('/edit/<int:session_id>')
    def edit_session(self, session_id):
        current_alert = get_alert()
        session_info = self.session.get_session(session_id)
        session_tutors = self.session.get_session_tutors(session_id)
        tutor_names = self.session.get_session_tutor_names(session_id)  # used for a logic check in template
        lead_list = self.schedule.get_registered_leads()  # used for adding tutors to session
        tutor_list = self.schedule.get_registered_tutors()
        session_students = self.session.get_session_students(session_id)
        student_courses = self.session
        semester_list = session['SEMESTER-LIST']
        course_list = self.course.get_semester_courses(session['SELECTED-SEMESTER'])
        session_courses = self.session.get_session_courses(session_id)
        return render_template('session/edit_closed_session.html', **locals())

    # TODO FIX ROUTE
    @route('/attendance/edit/<int:student_id>/<int:session_id>')
    def edit_student(self, student_id, session_id):
        student = self.session.get_student_session_info(student_id, session_id)
        student_courses = self.course.get_student_courses(student_id, session['SELECTED-SEMESTER'])
        session_courses = self.session.get_student_session_courses(session_id, student_id)
        other_course = self.session.get_other_course(session_id, student_id)
        current_alert = get_alert()
        return render_template('session/edit_student.html', **locals())

    @route('/attendance/student/<int:session_id>')
    def add_student(self, session_id):
        current_alert = get_alert()
        student_list = self.schedule.get_registered_students()
        return render_template('session/add_student.html', **locals())

    @route('/addanon/<int:session_id>')
    def add_anonymous(self, session_id):
        current_alert = get_alert()
        session = self.session.get_session(session_id)
        return render_template('session/add_anonymous.html', **locals())

    # TODO FIX ROUTE
    @route('/attendance/tutor/edit/<int:tutor_id>/<int:session_id>')
    def edit_tutor(self, tutor_id, session_id):
        current_alert = get_alert()
        tutor = self.session.get_tutor_session_info(tutor_id, session_id)
        return render_template('session/edit_tutor.html', **locals())

    @route('/addattendance/tutor/<int:session_id>')
    def add_tutor(self, session_id):
        current_alert = get_alert()
        tutor_list = self.schedule.get_registered_tutors()
        return render_template('session/add_tutor.html', **locals())

    def delete_session(self, session_id):
        current_alert = get_alert()
        session = self.session.get_session(session_id)
        return render_template('session/delete_session.html', **locals())

    def delete_confirmed(self, session_id):
        try:
            self.session.delete_session(session_id)
            set_alert('success', 'Session deleted successfully!')
            return redirect(url_for('SessionView:closed'))
        except Exception as error:
            set_alert('danger', 'Failed to delete session: ' + str(error))
            return redirect(url_for('SessionView:delete_session', session_id=session_id))

    @route('/save_session_edits', methods=['post'])
    def save_session_edits(self):
        try:
            form = request.form
            session_id = form.get('session-id')
            name = form.get('name')
            room = form.get('room')
            semester_id = form.get('semester')
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
        try:
            self.session.delete_student_from_session(student_id, session_id)
            set_alert('success', 'Student deleted successfully!')
        except Exception as error:
            set_alert('danger', 'Failed to delete student: ' + str(error))
        return redirect(url_for('SessionView:edit_session', session_id=session_id))

    def delete_tutor_from_session(self, tutor_id, session_id):
        try:
            self.session.delete_tutor_from_session(tutor_id, session_id)
            set_alert('success', 'Tutor deleted successfully!')
        except Exception as error:
            set_alert('danger', 'Failed to delete tutor: ' + str(error))
        return redirect(url_for('SessionView:edit_session', session_id=session_id))

    @route('/add_student_submit', methods=['post'])
    def add_student_submit(self):
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
        try:
            form = request.form
            name = form.get('name')
            room = form.get('room')
            semester_id = form.get('semester')
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

    # TODO: hash and CAS authentications

    def open_session(self, session_id):
        opener_username = app_settings['TEST_USERNAME']  # TODO: update with roles and permissions
        opener_user = self.user.get_user_by_username(opener_username)
        self.session.add_tutor_to_session(session_id, opener_user.id, datetime.now().strftime('%H:%M:%S'), None, 1)
        self.session.start_open_session(session_id, opener_user.id)
        return redirect(url_for('SessionView:student_attendance', session_id=session_id))

    def student_attendance(self, session_id):
        session_info = self.session.get_session(session_id)
        students = self.session.get_session_students(session_id)
        return render_template('session/student_attendance.html', **locals())

    def tutor_attendance(self, session_id):
        session_info = self.session.get_session(session_id)
        course_info = self.course.get_active_course_info()
        tutors = self.session.get_session_tutors(session_id)
        return render_template('session/tutor_attendance.html', **locals())

    def close_open_session(self, session_id):
        current_alert = get_alert()
        session_info = self.session.get_session(session_id)
        course_info = self.course.get_active_course_info()
        return render_template('session/close_open_session.html', **locals())

    @route('/confirm_close', methods=['post'])
    def confirm_close(self):
        try:
            form = request.form
            session_id = form.get('session-id')
            comments = form.get('comments')
            self.session.close_open_session(session_id, comments)
            set_alert('success', 'Session closed successfully!')
            return redirect(url_for("SessionView:index"))
        except Exception as error:
            set_alert('danger', 'Failed to close session: ' + str(error))
            return redirect(url_for('SessionView:close_open_session', session_id=session_id))

    def restore_deleted_session(self, session_id):
        try:
            self.session.restore_deleted_session(session_id)
            set_alert('success', 'Session restored successfully!')
            return redirect(url_for('SessionView:index'))
        except Exception as error:
            set_alert('danger', 'Failed to restore session: ' + str(error))
            return redirect(url_for('SessionView:deleted'))

    def student_sign_in(self, session_id):
        self.session.student_sign_in(session_id, 40476)  # TODO: Update with actual sign in
        return redirect(url_for('SessionView:student_attendance', session_id=session_id))

    def student_sign_out(self, session_id, student_id):
        self.session.student_sign_out(session_id, student_id)
        return redirect(url_for('SessionView:student_attendance', session_id=session_id))

    def tutor_sign_in(self, session_id):
        self.session.add_tutor_to_session(session_id, 40476, datetime.now().strftime('%H:%M:%S'), None, 1)  # TODO: Update with actual sign in
        return redirect(url_for('SessionView:tutor_attendance', session_id=session_id))

    def tutor_sign_out(self, session_id, tutor_id):
        self.session.tutor_sign_out(session_id, tutor_id)
        return redirect(url_for('SessionView:tutor_attendance', session_id=session_id))
