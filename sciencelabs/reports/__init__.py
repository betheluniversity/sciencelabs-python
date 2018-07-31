# Packages
from flask import render_template
from flask_classy import FlaskView, route
import calendar

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

    # TODO GET RID OF THIS SESS, MONTH, YEAR CODE-BAD CODE

    def index(self):
        sess = self.session_.get_closed_sessions()
        month = int(str(sess[0].date)[5:7])
        year = int(str(sess[0].date)[:4])

        return render_template('reports/base.html', **locals())

    def student(self):
        sess = self.session_.get_closed_sessions()
        month = int(str(sess[0].date)[5:7])
        year = int(str(sess[0].date)[:4])

        semester_list = self.schedule.get_semesters()
        student_info = self.user.get_student_info()
        return render_template('reports/student.html', **locals())

    def semester(self):
        sess = self.session_.get_closed_sessions()
        month = int(str(sess[0].date)[5:7])
        year = int(str(sess[0].date)[:4])

        semester = self.schedule.get_active_semester()
        semester_list = self.schedule.get_semesters()
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

        avg_total = self.session_.get_avg_total_time_per_student()
        avg_total_time = 0
        for ss in avg_total:
            if ss.timeIn and ss.timeOut:
                avg_total_time += ((ss.timeOut - ss.timeIn).total_seconds()/3600)

        unique_attendance = 0
        for attendance_data in unique_attendance_info:
            unique_attendance += attendance_data[1]

        return render_template('reports/term.html', **locals())

    @route('/month/<int:year>/<int:month>')
    def month(self, year, month):
        sess = self.session_.get_closed_sessions()
        first_month = int(str(sess[0].date)[5:7])
        first_year = int(str(sess[0].date)[:4])

        cal = calendar
        selected_year = first_year
        selected_month = first_month
        print(month)
        print(year)
        semester_list = self.schedule.get_semesters()
        schedule_info = self.schedule.get_schedule_tab_info()
        sessions = self.session_.get_closed_sessions()
        schedule_ = self.schedule
        session_ = self.session_
        # TODO CHANGE THIS TO MAKE IT DYNAMIC NOT HARD-CODED IN
        monthly_sessions = self.session_.get_monthly_sessions((str(year) + '-' + str(month) + '-01'), (str(year) + '-' + str(month) + '-31'))
        return render_template('reports/monthly.html', **locals())

    def annual(self):
        sess = self.session_.get_closed_sessions()
        month = int(str(sess[0].date)[5:7])
        year = int(str(sess[0].date)[:4])
        session_ = self.session_
        semesters = self.session_.get_years()

        return render_template('reports/cumulative.html', **locals())

    def session(self):
        sess = self.session_.get_closed_sessions()
        month = int(str(sess[0].date)[5:7])
        year = int(str(sess[0].date)[:4])

        semester_list = self.schedule.get_semesters()
        sessions = self.session_.get_closed_sessions()
        session_ = self.session_
        return render_template('reports/session.html', **locals())

    def course(self):
        sess = self.session_.get_closed_sessions()
        month = int(str(sess[0].date)[5:7])
        year = int(str(sess[0].date)[:4])

        semester = self.schedule.get_active_semester()
        semester_list = self.schedule.get_semesters()
        user_ = self.user
        course_info = self.courses.get_active_course_info()
        return render_template('reports/course.html', **locals())

    @route('/student/<int:student_id>')
    def view_student(self, student_id):
        sess = self.session_.get_closed_sessions()
        month = int(str(sess[0].date)[5:7])
        year = int(str(sess[0].date)[:4])

        student = self.user.get_user(student_id)
        student_info, attendance = self.user.get_student_attendance(student_id)
        total_sessions = self.session_.get_closed_sessions()
        courses = self.user.get_student_courses(student_id)
        sessions = self.user.get_studentsession(student_id)
        user = self.user
        session_ = self.session_
        return render_template('reports/view_student.html', **locals())

    @route('/course/<int:course_id>')
    def view_course(self, course_id):
        sess = self.session_.get_closed_sessions()
        month = int(str(sess[0].date)[5:7])
        year = int(str(sess[0].date)[:4])

        course = self.courses.get_course(course_id)
        students = self.user.get_students_in_course(course_id)
        sessions = self.session_.get_sessions(course_id)
        user = self.user
        session_ = self.session_
        return render_template('reports/view_course.html', **locals())

    @route('/session/<int:session_id>')
    def view_session(self, session_id):
        sess = self.session_.get_closed_sessions()
        month = int(str(sess[0].date)[5:7])
        year = int(str(sess[0].date)[:4])

        session = self.session_.get_session(session_id)
        tutors = self.session_.get_session_tutors(session_id)
        student_s_list = self.session_.get_studentsession_from_session(session_id)
        session_students = self.session_.get_session_students(session_id)
        session_courses = self.session_.get_session_courses(session_id)
        course_list = self.courses.get_semester_courses(40013)
        user = self.user
        session_ = self.session_
        return render_template('reports/view_session.html', **locals())
