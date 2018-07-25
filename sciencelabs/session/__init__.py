# Packages
from flask import render_template
from flask_classy import FlaskView, route

# Local
from sciencelabs.session.session_controller import SessionController
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

    def closed(self):
        sessions = self.session.get_closed_sessions()
        session_tutors = self.session
        semester = self.schedule.get_active_semester()
        semester_list = self.schedule.get_semesters()
        return render_template('session/closed_sessions.html', **locals())

    def create(self):
        active_semester = self.schedule.get_active_semester()
        semester_list = self.schedule.get_semesters()
        lead_list = self.schedule.get_registered_leads()
        tutor_list = self.schedule.get_registered_tutors()
        course_list = self.course.get_semester_courses(active_semester.id)
        return render_template('session/create_session.html', **locals())

    @route('/deleted')
    def restore(self):
        semester = self.schedule.get_active_semester()
        semester_list = self.schedule.get_semesters()
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
        semester_list = self.schedule.get_semesters()
        course_list = self.course.get_semester_courses(40013)  # TODO: needs to update with semester selector
        session_courses = self.session.get_session_courses(session_id)
        return render_template('session/edit_closed_session.html', **locals())

    def edit_student(self, student_id, session_id):
        student = self.session.get_student_session_info(student_id, session_id)
        student_courses = self.course.get_student_courses(student_id, 40013) #TODO: needs to update with semester selector
        session_courses = self.session.get_student_session_courses(session_id, student_id)
        other_course = self.session.get_other_course(session_id, student_id)
        return render_template('session/edit_student.html', **locals())

    def add_student(self):
        student_list = self.schedule.get_registered_students()
        return render_template('session/add_student.html', **locals())

    def add_anonymous(self, session_id):
        session = self.session.get_session(session_id)
        return render_template('session/add_anonymous.html', **locals())

    def edit_tutor(self, tutor_id, session_id):
        tutor = self.session.get_tutor_session_info(tutor_id, session_id)
        return render_template('session/edit_tutor.html', **locals())

    def add_tutor(self):
        tutor_list = self.schedule.get_registered_tutors()
        return render_template('session/add_tutor.html', **locals())

    def delete_session(self, session_id):
        session = self.session.get_session(session_id)
        return render_template('session/delete_session.html', **locals())
