# Packages
from flask import render_template
from flask_classy import FlaskView

# Local
from sciencelabs.reports.reports_controller import ReportController


class ReportView(FlaskView):
    def __init__(self):
        self.base = ReportController()

    def index(self):
        return render_template('reports/base.html')

    def student(self):
        student_info = self.base.get_student_info()
        return render_template('reports/student.html', **locals())

    def semester(self):
        term_info = self.base.get_term_info()
        return render_template('reports/term.html', **locals())

    def month(self):
        return render_template('reports/monthly.html')

    def annual(self):
        cumulative_info = self.base.get_cumulative_info()
        return render_template('reports/cumulative.html', **locals())

    def session(self):
        return render_template('reports/session.html')

    def course(self):
        course_info = self.base.get_course_info()
        return render_template('reports/course.html', **locals())
