# Packages
from flask import render_template
from flask_classy import FlaskView

# Local
from sciencelabs.reports.reports_controller import ReportController
from sciencelabs.db_repository.UserRepo import UserFunctions
from sciencelabs.db_repository.CourseRepo import CourseFunctions


class ReportView(FlaskView):
    def __init__(self):
        self.base = ReportController()

    def index(self):
        return render_template('reports/base.html')

    def student(self):
        student_info = UserFunctions.get_report_student_info(self)
        return render_template('reports/student.html', **locals())

    def semester(self):
        term_info = self.base.get_term_info()
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
        course_info = CourseFunctions.get_report_course_info(self)
        return render_template('reports/course.html', **locals())
