# Packages
from flask import render_template
from flask_classy import FlaskView

# Local
from sciencelabs.lab_reports.lab_reports_controller import ReportController


class ReportView(FlaskView):
    def __init__(self):
        self.base = ReportController()

    def index(self):
        return render_template('lab_reports/home.html')

    def student(self):
        return render_template('lab_reports/student.html')

    def semester(self):
        return render_template('lab_reports/term.html')

    def month(self):
        return render_template('lab_reports/monthly.html')

    def annual(self):
        return render_template('lab_reports/annual.html')

    def session(self):
        return render_template('lab_reports/session.html')

    def course(self):
        return render_template('lab_reports/course.html')