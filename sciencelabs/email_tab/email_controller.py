import socket
from flask import render_template
from flask_mail import Mail, Message
from sciencelabs.db_repository.session_functions import Session
from sciencelabs.db_repository.user_functions import User
from sciencelabs.db_repository.course_functions import Course
from sciencelabs import app


class EmailController:
    def __init__(self):
        self.session = Session()
        self.user = User()
        self.course = Course()

    # def close_session_email(self, session_id):
    #     # todo: check to make sure the session is open. If its not - send an alert?
    #     # todo: this should loop over each user who should receive an email and build their individual email
    #     # todo: make sure profs set as "course viewers" for other courses also see this
    #
    #     sess = self.session.get_session(session_id)
    #     subject = "{" + app.config['LAB_TITLE'] + "} " + sess.name + " (" + sess.date.strftime('%m/%d/%Y') + ")"
    #     opener = self.user.get_user(sess.openerId)
    #     lab_url = app.config['LAB_BASE_URL']
    #
    #     recipients = self.user.get_end_of_session_recipients()
    #     for recipient in recipients:
    #         recipient_roles = self.user.get_user_roles(recipient.id)
    #         recipient_role_names = []
    #         for role in recipient_roles:
    #             recipient_role_names.append(role.name)
    #         students_and_courses_report = {}
    #         students_and_courses = {}
    #
    #         # todo: add in this check
    #         is_recipient_admin = False
    #         self.create_close_session_email(is_recipient_admin)
    #
    #         # todo: put this into a method used above
    #         # def create_close_session_email(is_admin=False)
    #         tutors = self.session.get_session_tutors(session_id)
    #         session_students = self.session.get_session_students(session_id)
    #         for student in session_students:
    #             students_and_courses_report[student] = self.session.get_report_student_session_courses(session_id,
    #                                                                                                    student.id)
    #             students_and_courses[student] = self.session.get_student_session_courses(session_id, student.id)
    #         session_courses = self.session.get_session_courses(session_id)
    #         courses_and_info = {}
    #         courses_and_email_info = {}
    #         for course in session_courses:
    #             courses_and_info[course] = self.course.get_course(course.id)
    #             courses_and_email_info[course] = self.session.get_course_email_info(course.id)
    #
    #         # send an email
    #         self.send_message(subject, render_template('session/email.html', **locals()), recipient.email, None, True)

    def close_session_email(self, session_id):
        sess = self.session.get_session(session_id)
        subject = "{" + app.config['LAB_TITLE'] + "} " + sess.name + " (" + sess.date.strftime('%m/%d/%Y') + ")"
        opener = self.user.get_user(sess.openerId)
        tutors = self.session.get_session_tutors(session_id)
        recipients = self.user.get_end_of_session_recipients()
        count = 0
        failed = 0
        for recipient in recipients:
            try:
                recipient_roles = self.user.get_user_roles(recipient.id)
                recipient_role_names = []
                for role in recipient_roles:
                    recipient_role_names.append(role.name)
                students_and_courses = {}
                courses_and_attendance = {}
                if 'Administrator' in recipient_role_names:
                    session_students = self.session.get_session_students(session_id)
                    for student in session_students:
                        students_and_courses[student] = self.session.get_report_student_session_courses(session_id, student.id)  # Gets courses attended
                    session_courses = self.course.get_courses_for_session(session_id)
                    for course in session_courses:
                        courses_and_attendance[course] = self.session.get_session_course_students(session_id, course.id)  # Gets list of students attended for course
                else:  # They must be a prof since get_end_of_session_recipients only gets admins and profs
                    session_courses = self.course.get_courses_for_session(session_id)
                    professor_courses = self.course.get_professor_courses(recipient.id)
                    professor_viewer_courses = self.course.get_course_viewer_courses(recipient.id)
                    professor_course_ids = []
                    for course in professor_courses:
                        professor_course_ids.append(course.id)
                    for course in professor_viewer_courses:
                        professor_course_ids.append(course.id)
                    for course in session_courses:
                        if course.id in professor_course_ids:
                            courses_and_attendance[course] = self.session.get_session_course_students(session_id, course.id)  # Same as above
                    session_students = self.session.get_prof_session_students(session_id, professor_course_ids)  # Gets students specific to prof
                    for student in session_students:
                        students_and_courses[student] = self.session.get_report_student_session_courses(session_id, student.id)  # Same as above
                # send an email
                self.send_message(subject, render_template('sessions/email.html', **locals()), recipient.email, None, True)
                count = count + 1
            except:
                failed = failed + 1
        return "Sent {0} emails, failed to send {1} emails".format(count, failed)

    def send_message(self, subject, body, recipients, bcc, html=False):
        if app.config['ENVIRON'] != 'prod':
            print('Would have sent email to: ' + str(recipients))
            recipients = app.config['TEST_EMAILS']

        # TODO: remove this
        subject = subject + str(recipients)
        recipients = app.config['TEST_EMAILS']

        # if we are sending a message to a single user, go ahead and convert the string into a list
        if isinstance(recipients, str):
            recipients = [recipients]

        mail = Mail(app)
        msg = Message(subject=subject,
                      sender='noreply@bethel.edu',
                      recipients=recipients,
                      bcc=bcc)
        if html:
            msg.html = body
        else:
            msg.body = body
        try:
            mail.send(msg)
        except socket.error:
            print("Failed to send message: {}".format(body))
            return False
        return True
