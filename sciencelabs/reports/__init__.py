# Packages
from flask import render_template
from flask_classy import FlaskView, route

# Local
from sciencelabs.reports.reports_controller import ReportController
from sciencelabs.db_repository.schedule_functions import Schedule
from sciencelabs.db_repository.course_functions import Course
from sciencelabs.db_repository.user_functions import User
from sciencelabs.db_repository.session_functions import Session


class ReportView(FlaskView):
    def __init__(self):
        self.base = ReportController()
        self.schedule = Schedule()
        self.courses = Course()
        self.user = User()
        self.session_ = Session()

    def index(self):
        return render_template('reports/base.html')

    def student(self):
        student_info = self.user.get_student_info()
        return render_template('reports/student.html', **locals())

    def semester(self):
        term_info = self.schedule.get_term_report()
        term_attendance = self.schedule.get_session_attendance()
        unique_attendance_info = self.user.get_unique_session_attendance()
        total_sessions = 0
        for sessions in term_info:
            total_sessions += sessions[1]

        total_attendance = 0
        unique_attendance = 0
        attendance_list = []
        for sessions in term_attendance:
            total_attendance += sessions[1]
            attendance_list += [sessions[1]]

        unique_attendance = 0
        for attendance_data in unique_attendance_info:
            unique_attendance += attendance_data[1]

        return render_template('reports/term.html', **locals())

    def month(self):
        monthly_closed_info = self.base.get_closed_monthly_info()
        monthly_info = self.base.get_monthly_info()
        return render_template('reports/monthly.html', **locals())

    def annual(self):
        cumulative_info = self.base.get_cumulative_info()
        return render_template('reports/cumulative.html', **locals())

    def session(self):
        return render_template('reports/session.html')

    def course(self):
        user_ = self.user
        course_info = self.courses.get_active_course_info()
        return render_template('reports/course.html', **locals())

    @route('/student/<int:student_id>')
    def view_student(self, student_id):
        student = self.user.get_user(student_id)
        attendance = self.user.get_student_attendance(student_id, '')[1]
        courses = self.user.get_student_courses(student_id)
        user = self.user
        # TODO FIGURE OUT HOW TO USE THIS TO GET ATTENDANCE FOR SPECIFIC COURSE
        # info = self.user.get_student_attendance(student_id, 40146)
        # TODO MAYBE USE get_average_time_in_course(student_id, course_id) to get session attendance + time
        return render_template('reports/view_student.html', **locals())

    @route('/course/<int:course_id>')
    def view_course(self, course_id):
        course = self.courses.get_course(course_id)
        students = self.user.get_students_in_course(course_id)
        sessions = self.session_.get_sessions(course_id)
        user = self.user
        session_ = self.session_
        return render_template('reports/view_course.html', **locals())

    @route('/session/<int:session_id>')
    def view_session(self, session_id):
        session = self.session_.get_session(session_id)
        leads, tutors = self.session_.get_session_tutors(session_id)
        user = self.user
        session_ = self.session_
        course_list = self.courses.get_courses_for_session(session_id)
        count = 0
        # for things in course_list:
        #     count += 1
        #     print(things)
        # print('\n' + str(count))

        # TODO USE THIS TO GET STUDENT ATTENDANCE BY COURSE ALSO USE TO GET ALL OTHER RELEVANT INFO IN TABLE
        # TODO THEN USE USER.GET_USER(USER_ID) IN JINJA TO GET USER NAME
        # 40158
        # test = self.session_.get_session_attendees(40151, session_id)
        # for things in test:
        #     print(things[0].studentId)
        return render_template('reports/view_session.html', **locals())

