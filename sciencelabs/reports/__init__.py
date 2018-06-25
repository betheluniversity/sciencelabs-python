# Packages
from flask import render_template
from flask_classy import FlaskView

# Local
from sciencelabs.reports.reports_controller import ReportController


class ReportView(FlaskView):
    def __init__(self):
        self.base = ReportController()

    def index(self):
        return render_template('reports/home.html')

    def student(self):
        return render_template('reports/student.html')

    def semester(self):
        return render_template('reports/term.html')

    def month(self):
        return render_template('reports/monthly.html')

    def annual(self):
        return render_template('reports/cumulative.html')

    def session(self):
        return render_template('reports/session.html')

    def course(self):
        return render_template('reports/course.html')