# Packages
from flask import render_template
from flask_classy import FlaskView
from datetime import datetime

# Local
from sciencelabs.reports.reports_controller import ReportController
from sciencelabs.db_repository.schedule_functions import Schedule
from sciencelabs.db_repository.course_functions import Course
from sciencelabs.db_repository.user_functions import User


class ReportView(FlaskView):
    def __init__(self):
        self.base = ReportController()
        self.schedule = Schedule()
        self.courses = Course()
        self.user = User()

    def index(self):
        return render_template('reports/base.html')

    def student(self):
        student_info = self.user.get_student_info()
        return render_template('reports/student.html', **locals())

    def semester(self):
        timedelta_to_time = datetime.min
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
        course_info = self.courses.get_active_course_info()
        return render_template('reports/course.html', **locals())

    def view_student(self, student_id):
        today = datetime.today().strftime('%m/%d/%Y')
        student = self.user.get_student(student_id)
        attendance = self.user.get_one(student_id)[1]
        return render_template('reports/view_student.html', **locals())
