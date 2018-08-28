import json

# Packages
from flask import render_template, redirect, url_for, request, session
from flask_classy import FlaskView, route

# Local
from sciencelabs.sess.session_controller import SessionController
from sciencelabs.db_repository.session_functions import Session
from sciencelabs.db_repository.user_functions import User
from sciencelabs.db_repository.schedule_functions import Schedule
from sciencelabs.db_repository.course_functions import Course


class SessionView(FlaskView):
    def __init__(self):
        self.base = SessionController()
        self.user = User()
        self.session = Session()
        self.schedule = Schedule()
        self.course = Course()

    def index(self):
        semester = self.schedule.get_active_semester()
        return render_template('session/base.html', **locals())

    @route('/closed')
    def closed(self):
        sessions = self.session.get_closed_sessions(session['SELECTED-SEMESTER'])
        session_tutors = self.session
        semester = self.schedule.get_active_semester()
        semester_list = session['SEMESTER-LIST']
        return render_template('session/closed_sessions.html', **locals())

    def create(self):
        active_semester = self.schedule.get_active_semester()
        semester_list = session['SEMESTER-LIST']
        lead_list = self.schedule.get_registered_leads()
        tutor_list = self.schedule.get_registered_tutors()
        course_list = self.course.get_semester_courses(active_semester.id)
        return render_template('session/create_session.html', **locals())

    def deleted(self):
        semester = self.schedule.get_active_semester()
        semester_list = session['SEMESTER-LIST']
        return render_template('session/restore_session.html', **locals())

    @route('/edit/<int:session_id>')
    def edit_session(self, session_id):
        session_info = self.session.get_session(session_id)
        session_tutors = self.session.get_session_tutors(session_id)
        tutor_names = self.session.get_session_tutor_names(session_id)  # used for a logic check in template
        lead_list = self.schedule.get_registered_leads()  # used for adding tutors to session
        tutor_list = self.schedule.get_registered_tutors()
        session_students = self.session.get_session_students(session_id)
        student_courses = self.session
        semester_list = session['SEMESTER-LIST']
        course_list = self.course.get_semester_courses(40013)  # TODO: needs to update with semester selector
        session_courses = self.session.get_session_courses(session_id)
        return render_template('session/edit_closed_session.html', **locals())

    # TODO FIX ROUTE
    @route('/attendance/edit/<int:student_id>/<int:session_id>')
    def edit_student(self, student_id, session_id):
        student = self.session.get_student_session_info(student_id, session_id)
        student_courses = self.course.get_student_courses(student_id, 40013) #TODO: needs to update with semester selector
        session_courses = self.session.get_student_session_courses(session_id, student_id)
        other_course = self.session.get_other_course(session_id, student_id)
        return render_template('session/edit_student.html', **locals())

    @route('/attendance/student/<int:session_id>')
    def add_student(self, session_id):
        student_list = self.schedule.get_registered_students()
        return render_template('session/add_student.html', **locals())

    @route('/addanon/<int:session_id>')
    def add_anonymous(self, session_id):
        session = self.session.get_session(session_id)
        return render_template('session/add_anonymous.html', **locals())

    # TODO FIX ROUTE
    @route('/attendance/tutor/edit/<int:tutor_id>/<int:session_id>')
    def edit_tutor(self, tutor_id, session_id):
        tutor = self.session.get_tutor_session_info(tutor_id, session_id)
        return render_template('session/edit_tutor.html', **locals())

    @route('/addattendance/tutor/<int:session_id>')
    def add_tutor(self, session_id):
        tutor_list = self.schedule.get_registered_tutors()
        return render_template('session/add_tutor.html', **locals())

    def delete_session(self, session_id):
        session = self.session.get_session(session_id)
        return render_template('session/delete_session.html', **locals())

    def delete_confirmed(self, session_id):
        self.session.delete_session(session_id)
        return redirect(url_for('SessionView:closed'))

    @route('/save_session_edits', methods=['post'])
    def save_session_edits(self):
        form = request.form
        session_id = form.get('sessionID')
        # TODO: Save edits
        return 'success'

    @route('/save_student_edits', methods=['post'])
    def save_student_edits(self):
        try:
            form = request.form
            session_id = form.get('sessionId')
            student_id = form.get('studentId')
            time_in = form.get('timeIn')
            time_out = form.get('timeOut')
            json_courses = form.get('courses')
            student_courses = json.loads(json_courses)
            other_course = form.get('otherCourse')
            self.session.edit_student_session(session_id, student_id, time_in, time_out, other_course)
            self.session.edit_student_courses(session_id, student_id, student_courses)
            return 'Student edited successfully'
        except:
            return 'Failed to edit students'

    @route('/save_tutor_edits', methods=['post'])
    def save_tutor_edits(self):
        try:
            form = request.form
            session_id = form.get('sessionId')
            tutor_id = form.get('tutorId')
            time_in = form.get('timeIn')
            time_out = form.get('timeOut')
            lead = form.get('lead')
            self.session.edit_tutor_session(session_id, tutor_id, time_in, time_out, lead)
            return 'Tutor edited successfully'
        except:
            return 'Failed to edit tutor'

    def delete_student_from_session(self, student_id, session_id):
        self.session.delete_student_from_session(student_id, session_id)
        return redirect(url_for('SessionView:closed'))

    def delete_tutor_from_session(self, tutor_id, session_id):
        self.session.delete_tutor_from_session(tutor_id, session_id)
        return redirect(url_for('SessionView:closed'))

    @route('/add_student_submit', methods=['post'])
    def add_student_submit(self):
        try:
            form = request.form
            session_id = form.get('sessionId')
            student_id = form.get('studentId')
            self.session.add_student_to_session(session_id, student_id)
            return 'Student Added Successfully'
        except:
            return 'Failed to add student'

    @route('/add_anon_submit', methods=['post'])
    def add_anon_submit(self):
        try:
            form = request.form
            session_id = form.get('sessionId')
            anon_students = form.get('anonStudents')
            self.session.add_anonymous_to_session(session_id, anon_students)
            return 'Anonymous students edited successfully'
        except:
            return 'Failed to edit anonymous students'

    @route('/add_tutor_submit', methods=['post'])
    def add_tutor_submit(self):
        try:
            form = request.form
            session_id = form.get('sessionId')
            tutor_id = form.get('tutorId')
            time_in = form.get('timeIn')
            time_out = form.get('timeOut')
            lead = form.get('lead')
            self.session.add_tutor_to_session(session_id, tutor_id, time_in, time_out, lead)
            return 'Tutor added successfully'
        except:
            return 'Failed to add tutor'

    @route('/create_session_submit', methods=['post'])
    def create_session_submit(self):
        form = request.form
        session_id = form.get('sessionID')
        # TODO: Save edits
        return 'success'
