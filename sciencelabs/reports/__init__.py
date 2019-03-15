# Packages
from flask import render_template, Response
from flask import session as flask_session
from flask_classy import FlaskView, route
import calendar
import csv
from datetime import datetime

# Local
from sciencelabs import app
from sciencelabs.reports.reports_controller import ReportController
from sciencelabs.db_repository.schedule_functions import Schedule
from sciencelabs.db_repository.course_functions import Course
from sciencelabs.db_repository.user_functions import User
from sciencelabs.db_repository.session_functions import Session
from sciencelabs.sciencelabs_controller import ScienceLabsController


class ReportView(FlaskView):
    def __init__(self):
        self.base = ReportController()
        self.schedule = Schedule()
        self.courses = Course()
        self.user = User()
        self.session_ = Session()
        self.slc = ScienceLabsController()

    @route('/')
    def index(self):
        self.slc.check_roles_and_route(['Professor', 'Administrator', 'Academic Counselor'])

        sem = self.schedule.get_semester(flask_session['SELECTED-SEMESTER'])
        month = self._get_selected_month()
        year = sem.year

        return render_template('reports/base.html', **locals())

    @route('/student')
    def student(self):
        self.slc.check_roles_and_route(['Professor', 'Administrator', 'Academic Counselor'])

        sem = self.schedule.get_semester(flask_session['SELECTED-SEMESTER'])
        month = self._get_selected_month()
        year = sem.year
        student_info = self.user.get_student_info(flask_session['SELECTED-SEMESTER'])

        student_and_attendance = {}
        for student in student_info:
            student_and_attendance[student] = len(self.user.get_unique_sessions_attended(student.id, flask_session['SELECTED-SEMESTER']))

        return render_template('reports/student.html', **locals())

    @route('/student/<int:student_id>')
    def view_student(self, student_id):
        self.slc.check_roles_and_route(['Professor', 'Administrator', 'Academic Counselor'])

        sem = self.schedule.get_semester(flask_session['SELECTED-SEMESTER'])
        month = self._get_selected_month()
        year = sem.year
        student = self.user.get_user(student_id)
        viewer = self.user.get_user_by_username(flask_session['USERNAME'])

        # The last check in the following if is to see if we are viewing the prof role, but not a specific prof user
        if 'Administrator' in flask_session['USER-ROLES'] \
                or 'Academic Counselor' in flask_session['USER-ROLES'] \
                or ('Professor' in flask_session['USER-ROLES'] and flask_session['NAME'] and self.courses.student_is_in_prof_course(student_id, viewer.id)) \
                or ('ADMIN-VIEWER' in flask_session.keys() and flask_session['ADMIN-VIEWER'] and not flask_session['NAME']):

            role_can_view = True
            student_info, attendance = self.user.get_student_attendance(student_id, flask_session['SELECTED-SEMESTER'])
            total_sessions = self.session_.get_closed_sessions(flask_session['SELECTED-SEMESTER'])
            courses = self.user.get_student_courses(student_id, flask_session['SELECTED-SEMESTER'])
            sessions = self.user.get_studentsession(student_id, flask_session['SELECTED-SEMESTER'])
            sessions_attended = len(self.user.get_unique_sessions_attended(student_id, flask_session['SELECTED-SEMESTER']))

            course_and_avg_time = {}
            for course in courses:
                course_and_avg_time[course] = self.user.get_average_time_in_course(student.id, course.id)

            sessions_and_courses = {}
            for studentsession, lab_session in sessions:
                sessions_and_courses[studentsession] = {}
                sessions_and_courses[studentsession]['session'] = lab_session
                sessions_and_courses[studentsession]['courses'] = self.session_.get_report_student_session_courses(lab_session.id, student.id)

        else:
            role_can_view = False

        return render_template('reports/view_student.html', **locals())

    def export_student_csv(self):
        self.slc.check_roles_and_route(['Professor', 'Administrator', 'Academic Counselor'])

        sem = self.schedule.get_semester(flask_session['SELECTED-SEMESTER'])
        term = sem.term[:2]
        year = sem.year
        lab = ''
        for letter in app.config['LAB_TITLE'].split():
            lab += letter[0]

        csv_name = '{0}{1}_{2}_StudentReport'.format(term, year, lab)

        my_list = [['Last', 'First', 'Email', 'Attendance']]

        for student in self.user.get_student_info(flask_session['SELECTED-SEMESTER']):
            my_list.append([student.lastName, student.firstName, student.email, len(self.user.get_unique_sessions_attended(student.id, flask_session['SELECTED-SEMESTER']))])

        return self.export_csv(my_list, csv_name)

    @route('/semester')
    def semester(self):
        self.slc.check_roles_and_route(['Administrator', 'Academic Counselor'])

        sem = self.schedule.get_semester(flask_session['SELECTED-SEMESTER'])
        month = self._get_selected_month()
        year = sem.year

        semester = self.schedule.get_semester(flask_session['SELECTED-SEMESTER'])
        term_info = self.schedule.get_term_report(flask_session['SELECTED-SEMESTER'])
        term_attendance = self.schedule.get_session_attendance(flask_session['SELECTED-SEMESTER'])
        anon_attendance = self.schedule.get_anon_student_attendance_info(flask_session['SELECTED-SEMESTER'])
        unique_attendance_info = self.user.get_unique_session_attendance(flask_session['SELECTED-SEMESTER'])
        anon_attendance_info = {}
        for sess, sched in anon_attendance:
            anon_attendance_info[sess] = {}
            anon_attendance_info[sess]['schedule'] = sched
            anon_attendance_info[sess]['attendance'] = len(self.session_.get_number_of_student_sessions(sess.id))

        total_sessions = 0
        for sessions in term_info:
            total_sessions += sessions[1]

        total_attendance = 0
        for sessions in term_attendance:
            total_attendance += sessions[1]

        avg_total = self.session_.get_avg_total_time_per_student(flask_session['SELECTED-SEMESTER'])
        avg_total_time = 0
        for ss in avg_total:
            if ss.timeIn and ss.timeOut:
                avg_total_time += ((ss.timeOut - ss.timeIn).total_seconds() / 3600)

        for unscheduled_session in self.session_.get_unscheduled_sessions(sem.year, sem.term):
            for user, studentsession in self.session_.get_studentsession_from_session(unscheduled_session.id):
                if studentsession.timeIn and studentsession.timeOut:
                    avg_total_time += ((studentsession.timeOut - studentsession.timeIn).total_seconds() / 3600)

        unique_attendance = 0
        unique_attendance_list = []
        for attendance_data in unique_attendance_info:
            unique_attendance += attendance_data[1]
            unique_attendance_list += [attendance_data[0].id]

        sem = self.schedule.get_semester(flask_session['SELECTED-SEMESTER'])
        unscheduled_sessions = self.session_.get_unscheduled_sessions(sem.year, sem.term)
        unscheduled_sessions_and_attendance = {}
        for unscheduled_session in unscheduled_sessions:
            unscheduled_sessions_and_attendance[unscheduled_session] = {}
            unscheduled_sessions_and_attendance[unscheduled_session]['attendance'] = len(self.user.get_session_students(unscheduled_session.id))
            unscheduled_sessions_and_attendance[unscheduled_session]['unscheduled-attendance'] = self.session_.get_unscheduled_unique_attendance(unscheduled_session.id)

        return render_template('reports/term.html', **locals())

    def export_semester_csv(self):
        self.slc.check_roles_and_route(['Administrator', 'Academic Counselor'])

        sem = self.schedule.get_semester(flask_session['SELECTED-SEMESTER'])
        term = sem.term[:2]
        year = sem.year
        lab = ''
        for letter in app.config['LAB_TITLE'].split():
            lab += letter[0]

        csv_name = '{0}{1}_{2}_TermReport'.format(term, year, lab)

        my_list = [['Schedule Statistics for Closed Sessions']]
        my_list.append(['Schedule Name', 'DOW', 'Start Time', 'Stop Time', 'Number of Sessions', 'Attendance',
                        'Percentage'])

        term_attendance = self.schedule.get_session_attendance(flask_session['SELECTED-SEMESTER'])
        total_attendance = 0
        unique_attendance = 0
        for sessions in term_attendance:
            total_attendance += sessions[1]

        unique_attendance_info = self.user.get_unique_session_attendance(flask_session['SELECTED-SEMESTER'])
        unique_attendance_list = []
        for attendance_data in unique_attendance_info:
            unique_attendance += attendance_data[1]
            unique_attendance_list += [attendance_data[0].id]

        all_total_attendance = total_attendance
        unscheduled_sessions = self.session_.get_unscheduled_sessions(sem.year, sem.term)
        for sessions in unscheduled_sessions:
            for unscheduled_attendance in self.session_.get_unscheduled_unique_attendance(sessions.id):
                if unscheduled_attendance[0].id not in unique_attendance_list:
                    all_total_attendance += unscheduled_attendance[1]

        term_info = self.schedule.get_term_report(flask_session['SELECTED-SEMESTER'])
        anon_attendance = self.schedule.get_anon_student_attendance_info(flask_session['SELECTED-SEMESTER'])

        for schedule, sessions in term_info:
            for sess, sched in anon_attendance:
                if sched.id == schedule.id:
                    all_total_attendance += sess.anonStudents

        index = 0
        session_count = 0
        total_anon = 0
        for schedule, sessions in term_info:
            anonStudents = 0
            attendance = 0
            for sess, sched in anon_attendance:
                if schedule.id == sched.id:
                    anonStudents += sess.anonStudents
                    attendance += len(self.session_.get_number_of_student_sessions(sess.id))
            total_anon += anonStudents
            session_count += sessions
            my_list.append([schedule.name, self._get_dayofweek(schedule.dayofWeek),
                            self._datetimeformatter(schedule.startTime), self._datetimeformatter(schedule.endTime),
                            sessions,
                            attendance + anonStudents,
                            str(round((((attendance + anonStudents) / all_total_attendance) * 100))) + '%'])
            index += 1

        my_list.append(['', '', '', 'Total:', session_count, total_attendance + total_anon, '100%'])
        my_list.append([])
        my_list.append(['Unscheduled Sessions', 'Date', 'Start Time', 'Stop Time', 'Attendance'])

        total_unscheduled = 0
        for sessions in unscheduled_sessions:
            my_list.append(['', sessions.date.strftime('%m/%d/%Y'), self._datetimeformatter(sessions.startTime),
                            self._datetimeformatter(sessions.endTime),
                            len(self.user.get_session_students(sessions.id)) + sessions.anonStudents])
            total_unscheduled += len(self.user.get_session_students(sessions.id)) + sessions.anonStudents

        my_list.append(['', '', 'Total', total_unscheduled])

        return self.export_csv(my_list, csv_name)

    @route('/month/<int:year>/<int:month>')
    def month(self, year, month):
        self.slc.check_roles_and_route(['Administrator', 'Academic Counselor'])

        self._set_semester_selector(year, month)
        sem = self.schedule.get_semester(flask_session['SELECTED-SEMESTER'])
        month = month
        year = sem.year
        cal = calendar
        months = self.base.months
        selected_year = year
        selected_month = month
        selected_months = []
        interim_list = [1]
        spring_list = [2, 3, 4, 5]
        summer_list = [6, 7]
        fall_list = [8, 9, 10, 11, 12]
        if month in interim_list:
            term = 'Interim'
            selected_months = interim_list
        elif month in spring_list:
            term = 'Spring'
            selected_months = spring_list
        elif month in fall_list:
            term = 'Fall'
            selected_months = fall_list
        else:
            term = 'Summer'
            selected_months = summer_list
        schedule_info = self.schedule.get_yearly_schedule_tab_info(selected_year, term)
        sessions = self.session_.get_semester_closed_sessions(selected_year, term)
        unscheduled_sessions = self.session_.get_unscheduled_sessions(selected_year, term)
        unscheduled_sessions_and_attendance = {}
        for unscheduled_session in unscheduled_sessions:
            unscheduled_sessions_and_attendance[unscheduled_session] = len(self.user.get_session_students(unscheduled_session.id))
        monthly_sessions = self.session_.get_monthly_sessions((str(year) + '-' + str(month) + '-01'), (str(year) + '-' +
                                                                                                       str(month) +
                                                                                                       '-31'))
        monthly_sessions_schedule_and_attendance = {}
        for month_session in monthly_sessions:
            monthly_sessions_schedule_and_attendance[month_session] = {}
            monthly_sessions_schedule_and_attendance[month_session]['schedule'] = self.schedule.get_schedule_from_session(month_session.id)
            monthly_sessions_schedule_and_attendance[month_session]['attendance'] = self.session_.get_session_attendees(month_session.id)
        return render_template('reports/monthly.html', **locals())

    def export_monthly_summary_csv(self, year, month):
        self.slc.check_roles_and_route(['Administrator', 'Academic Counselor'])

        month = int(month)
        if month == 1:
            term = 'Interim'
        elif month in [2, 3, 4, 5]:
            term = 'Spring'
        elif month in [8, 9, 10, 11, 12]:
            term = 'Fall'
        else:
            term = 'Summer'
        term_abbr = term[:2].upper()
        lab = ''
        for letter in app.config['LAB_TITLE'].split():
            lab += letter[0]
        selected_month = self.base.months[month - 1]

        csv_name = '{0}{1}_{2}_{3}_SummaryReport'.format(term_abbr, year, lab, selected_month)

        my_list = [['Schedule Name', 'DOW', 'Scheduled Time', 'Total Attendance', '% Total']]

        schedule_info = self.schedule.get_yearly_schedule_tab_info(year, term)
        monthly_sessions = self.session_.get_monthly_sessions((str(year) + '-' + str(month) + '-01'), (str(year) + '-' +
                                                                                                       str(month) +
                                                                                                       '-31'))

        total_attendance = 0
        for schedule in schedule_info:
            for session_info in monthly_sessions:
                session_schedule = self.schedule.get_schedule_from_session(session_info.id)
                attendance = self.session_.get_session_attendees(session_info.id)
                if schedule and session_schedule:
                    if schedule.id == session_schedule.id:
                        total_attendance += attendance.count() + session_info.anonStudents

        for schedule in schedule_info:
            total_attendance_per_schedule = 0
            for session_info in monthly_sessions:
                session_schedule = self.schedule.get_schedule_from_session(session_info.id)
                attendance = self.session_.get_session_attendees(session_info.id)
                if schedule and session_schedule:
                    if schedule.id == session_schedule.id:
                        total_attendance_per_schedule += attendance.count() + session_info.anonStudents
            my_list.append([schedule.name, self._get_dayofweek(schedule.dayofWeek),
                            self._datetimeformatter(schedule.startTime) + ' - ' +
                            self._datetimeformatter(schedule.endTime),
                            total_attendance_per_schedule,
                            str(round((total_attendance_per_schedule/total_attendance)*100, 1)) + '%'])

        unscheduled_sessions = self.session_.get_unscheduled_sessions(year, term)
        total_unscheduled = 0
        if unscheduled_sessions:
            for session_info in unscheduled_sessions:
                total_unscheduled += (len(self.user.get_session_students(session_info.id))) + session_info.anonStudents
            total_attendance += total_unscheduled

        my_list.append(['Unscheduled Sessions', '', '', total_unscheduled,
                        str(round((total_unscheduled / total_attendance) * 100, 1)) + '%'])

        my_list.append(['', '', 'Total', total_attendance])

        return self.export_csv(my_list, csv_name)

    def export_monthly_detail_csv(self, year, month):
        self.slc.check_roles_and_route(['Administrator', 'Academic Counselor'])

        month = int(month)
        if month == 1:
            term = 'Interim'
        elif month in [2, 3, 4, 5]:
            term = 'Spring'
        elif month in [8, 9, 10, 11, 12]:
            term = 'Fall'
        else:
            term = 'Summer'
        term_abbr = term[:2].upper()
        lab = ''
        for letter in app.config['LAB_TITLE'].split():
            lab += letter[0]
        selected_month = self.base.months[month - 1]

        csv_name = '{0}{1}_{2}_{3}_DetailReport'.format(term_abbr, year, lab, selected_month)

        my_list = [['Name', 'Date', 'DOW', 'Scheduled Time', 'Total Attendance']]

        cal = calendar

        monthly_sessions = self.session_.get_monthly_sessions((str(year) + '-' + str(month) + '-01'), (str(year) + '-' +
                                                                                                       str(month) +
                                                                                                       '-31'))
        total_attendance = 0
        for session_info in monthly_sessions:
            attendance = self.session_.get_session_attendees(session_info.id)
            total_attendance += attendance.count() + session_info.anonStudents
            sel_year, sel_month, sel_day = str(session_info.date).split('-')
            my_list.append([session_info.name, session_info.date.strftime('%m/%d/%Y'),
                            (self._get_dayofweek((cal.weekday(int(sel_year), int(sel_month), int(sel_day)) + 1) % 7)),
                            self._datetimeformatter(session_info.schedStartTime) +
                            ' - ' + self._datetimeformatter(session_info.schedStartTime), attendance.count() +
                            session_info.anonStudents])

        my_list.append(['', '', 'Total:', total_attendance])

        return self.export_csv(my_list, csv_name)

    @route('/annual')
    def annual(self):
        self.slc.check_roles_and_route(['Administrator', 'Academic Counselor'])

        sem = self.schedule.get_semester(flask_session['SELECTED-SEMESTER'])
        month = self._get_selected_month()  # Needed for subnav
        year = sem.year  # Needed for subnav
        cumulative_list = self.build_cumulative_list()
        return render_template('reports/cumulative.html', **locals())

    def export_cumulative_csv(self):
        self.slc.check_roles_and_route(['Administrator', 'Academic Counselor'])

        lab = ''
        for letter in app.config['LAB_TITLE'].split():
            lab += letter[0]

        csv_name = '{0}_CumulativeAttendance'.format(lab)

        my_list = self.build_cumulative_list()

        return self.export_csv(my_list, csv_name)

    def build_cumulative_list(self):
        my_list = [['Year', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Fall', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Spring',
                    'Jun', 'Jul', 'Summer', 'Total']]

        total_dict = {'8': 0, '9': 0, '10': 0, '11': 0, '12': 0, 'fall': 0, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0,
                      'spring': 0, '6': 0, '7': 0, 'summer': 0, 'total': 0}

        semesters = self.session_.get_years()
        for semester in semesters:
            sub_list = [str(semester.year) + '-' + str(semester.year + 1)]
            fall_total = 0
            for month in range(8, 13):
                monthly_sessions = self.session_.get_monthly_sessions((str(semester.year) + '-' + str(month) + '-1'),
                                                                      (str(semester.year) + '-' + str(month) + '-31'))
                total_attendance = 0
                for sessions in monthly_sessions:
                    attendance = self.session_.get_session_attendees(sessions.id).count()
                    total_attendance += attendance + sessions.anonStudents
                    total_dict[str(month)] += attendance + sessions.anonStudents
                sub_list.append(total_attendance)
                fall_total += total_attendance
            total_dict['fall'] += fall_total
            sub_list.append(fall_total)
            monthly_sessions = self.session_.get_monthly_sessions((str((semester.year + 1)) + '-' + str(1) + '-1'),
                                                                  (str((semester.year + 1)) + '-' + str(1) + '-31'))
            total_attendance = 0
            for sessions in monthly_sessions:
                attendance = self.session_.get_session_attendees(sessions.id).count()
                total_attendance += attendance + sessions.anonStudents
                total_dict[str(1)] += attendance + sessions.anonStudents
            sub_list.append(total_attendance)
            interim_total = total_attendance
            spring_total = 0
            for month in range(2, 6):
                monthly_sessions = self.session_.get_monthly_sessions((str((semester.year + 1)) + '-' + str(month) +
                                                                       '-1'), (str((semester.year + 1)) + '-' +
                                                                               str(month) + '-31'))
                total_attendance = 0
                for sessions in monthly_sessions:
                    attendance = self.session_.get_session_attendees(sessions.id).count()
                    total_attendance += attendance + sessions.anonStudents
                    total_dict[str(month)] += attendance + sessions.anonStudents
                sub_list.append(total_attendance)
                spring_total += total_attendance
            total_dict['spring'] += spring_total
            sub_list.append(spring_total)
            summer_total = 0
            for month in range(6, 8):
                monthly_sessions = self.session_.get_monthly_sessions((str((semester.year + 1)) + '-' + str(month) +
                                                                       '-1'), (str((semester.year + 1)) + '-' +
                                                                               str(month) + '-31'))
                total_attendance = 0
                for sessions in monthly_sessions:
                    attendance = self.session_.get_session_attendees(sessions.id).count()
                    total_attendance += attendance + sessions.anonStudents
                    total_dict[str(month)] += attendance + sessions.anonStudents
                sub_list.append(total_attendance)
                summer_total += total_attendance
            total_dict['summer'] += summer_total
            sub_list.append(summer_total)
            total_dict['total'] += fall_total + spring_total + summer_total + interim_total
            sub_list.append(fall_total + spring_total + summer_total + interim_total)
            my_list.append(sub_list)

        if app.config['LAB_TITLE'] == 'Math Lab':
            cumulative = self.base.math_lab_cumulative
        elif app.config['LAB_TITLE'] == 'Computer Science Lab':
            cumulative = self.base.cs_lab_cumulative
        else:
            cumulative = []
        first = True
        for info in cumulative:
            if first:
                sub_list = [cumulative[info]['academicYear']]
                for month in range(8, 13):
                    sub_list.append(cumulative[info]['monthly'][month])
                    total_dict[str(month)] += cumulative[info]['monthly'][month]
                total_dict['fall'] += cumulative[info]['fallTotal']
                sub_list.extend([cumulative[info]['fallTotal'], cumulative[info]['monthly'][1]])
                total_dict[str(1)] += cumulative[info]['monthly'][1]
                for month in range(2, 6):
                    sub_list.append(cumulative[info]['monthly'][month])
                    total_dict[str(month)] += cumulative[info]['monthly'][month]
                total_dict['spring'] += cumulative[info]['springTotal']
                sub_list.append(cumulative[info]['springTotal'])
                for month in range(6, 8):
                    sub_list.append(cumulative[info]['monthly'][month])
                    total_dict[str(month)] += cumulative[info]['monthly'][month]
                total_dict['summer'] += cumulative[info]['summerTotal']
                sub_list.extend([cumulative[info]['summerTotal'], cumulative[info]['yearTotal']])
                total_dict['total'] += cumulative[info]['yearTotal']
                first = False
            else:
                sub_list = [cumulative[info]['academicYear']]
                for month in range(8, 13):
                    sub_list.append(cumulative[info]['monthly'][month])
                    total_dict[str(month)] += cumulative[info]['monthly'][month]
                total_dict['fall'] += cumulative[info]['fallTotal']
                sub_list.extend([cumulative[info]['fallTotal'], cumulative[info]['monthly'][1]])
                total_dict[str(1)] += cumulative[info]['monthly'][1]
                for month in range(2, 6):
                    sub_list.append(cumulative[info]['monthly'][month])
                    total_dict[str(month)] += cumulative[info]['monthly'][month]
                total_dict['spring'] += cumulative[info]['springTotal']
                sub_list.append(cumulative[info]['springTotal'])
                for month in range(6, 8):
                    sub_list.append(cumulative[info]['monthly'][month])
                    total_dict[str(month)] += cumulative[info]['monthly'][month]
                total_dict['summer'] += cumulative[info]['summerTotal']
                sub_list.extend([cumulative[info]['summerTotal'], cumulative[info]['yearTotal']])
                total_dict['total'] += cumulative[info]['yearTotal']
            my_list.append(sub_list)

        sub_list = ['Total:']

        for keys in total_dict:
            sub_list.append(total_dict[keys])

        my_list.append(sub_list)

        return my_list

    @route('/session')
    def session(self):
        self.slc.check_roles_and_route(['Administrator', 'Academic Counselor'])

        sem = self.schedule.get_semester(flask_session['SELECTED-SEMESTER'])
        month = self._get_selected_month()
        year = sem.year
        months = self.base.months
        sessions = self.session_.get_closed_sessions(flask_session['SELECTED-SEMESTER'])
        sessions_info = {}
        for lab_session in sessions:
            sessions_info[lab_session] = {}
            sessions_info[lab_session]['DOW'] = self.session_.get_dayofWeek_from_session(lab_session.id)
            sessions_info[lab_session]['attendance'] = self.session_.get_number_of_student_sessions(lab_session.id)
            sessions_info[lab_session]['tutors'] = self.session_.get_session_tutors(lab_session.id)
        return render_template('reports/session.html', **locals())

    @route('/session/<int:session_id>')
    def view_session(self, session_id):
        self.slc.check_roles_and_route(['Administrator', 'Academic Counselor'])

        sem = self.schedule.get_semester(flask_session['SELECTED-SEMESTER'])
        month = self._get_selected_month()
        year = sem.year

        total_attendance = self.session_.get_number_of_student_sessions(session_id)
        session_info = self.session_.get_session(session_id)
        tutors = self.session_.get_session_tutors(session_id)
        student_s_list = self.session_.get_studentsession_from_session(session_id)
        session_students = self.session_.get_session_students(session_id)
        session_courses = self.session_.get_session_course_codes(session_id)
        session_courses_and_attendance = {}
        for course in session_courses:
            session_courses_and_attendance[course] = self.session_.get_course_code_attendance(session_id, course.id)
        opener = None
        if session_info.openerId:
            opener = self.user.get_user(session_info.openerId)
        students_and_report_courses = {}
        students_and_courses = {}
        for student in session_students:
            students_and_report_courses[student] = self.session_.get_report_student_session_courses(session_info.id, student.id)
            students_and_courses[student] = self.session_.get_student_session_course_ids(session_info.id, student.id)
        return render_template('reports/view_session.html', **locals())

    def export_session_csv(self):
        self.slc.check_roles_and_route(['Professor', 'Administrator', 'Academic Counselor'])

        sem = self.schedule.get_semester(flask_session['SELECTED-SEMESTER'])
        term = sem.term[:2]
        year = sem.year
        lab = ''
        for letter in app.config['LAB_TITLE'].split():
            lab += letter[0]

        csv_name = '{0}{1}_{2}_SessionReport'.format(term, year, lab)

        my_list = [['Date', 'Name', 'DOW', 'Start Time', 'End Time', 'Room', 'Total Attendance', 'Comments']]

        sessions = self.session_.get_closed_sessions(flask_session['SELECTED-SEMESTER'])
        dates = []
        for session_info in sessions:
            if (str(session_info.date.strftime('%m'))) not in dates:
                dates.append(str(session_info.date.strftime('%m')))

        days = self.base.days

        total_attendance = 0
        for date in dates:
            for session_info in sessions:
                if (str(session_info.date.strftime('%m'))) == date:
                    attendance = len(self.session_.get_number_of_student_sessions(session_info.id))
                    my_list.append([session_info.date.strftime('%m/%d/%Y'), session_info.name,
                                    days[self.session_.get_dayofWeek_from_session(session_info.id).dayofWeek],
                                    session_info.startTime, session_info.endTime, session_info.room, attendance,
                                    session_info.comments])
                    total_attendance += attendance

        my_list.append(['', '', '', '', '', 'Total:', total_attendance])

        return self.export_csv(my_list, csv_name)

    @route('/course')
    def course(self):
        self.slc.check_roles_and_route(['Professor', 'Administrator', 'Academic Counselor'])

        sem = self.schedule.get_semester(flask_session['SELECTED-SEMESTER'])
        month = self._get_selected_month()
        year = sem.year
        semester = self.schedule.get_semester(flask_session['SELECTED-SEMESTER'])

        # The last check in the following if is to see if we are viewing the prof role, but not a specific prof user
        if 'Administrator' in flask_session['USER-ROLES'] or 'Academic Counselor' in flask_session['USER-ROLES']\
                or ('ADMIN-VIEWER' in flask_session.keys() and flask_session['ADMIN-VIEWER'] and not flask_session['NAME']):

            course_info = self.courses.get_selected_course_info(flask_session['SELECTED-SEMESTER'])
            course_viewer_info = None

        else:  # They must be a professor
            prof = self.user.get_user_by_username(flask_session['USERNAME'])
            course_info = self.courses.get_selected_prof_course_info(flask_session['SELECTED-SEMESTER'], prof.id)
            course_viewer_info = self.courses.get_selected_course_viewer_info(flask_session['SELECTED-SEMESTER'], prof.id)

        courses_and_attendance = {}
        for course, course_user in course_info:
            courses_and_attendance[course] = {}
            courses_and_attendance[course]['user'] = course_user
            courses_and_attendance[course]['attendance'] = self.user.get_students_in_course(course.id)

        if course_viewer_info:
            for course, course_user in course_viewer_info:
                courses_and_attendance[course] = {}
                courses_and_attendance[course]['user'] = course_user
                courses_and_attendance[course]['attendance'] = self.user.get_students_in_course(course.id)

        return render_template('reports/course.html', **locals())

    @route('/course/<int:course_id>')
    def view_course(self, course_id):
        self.slc.check_roles_and_route(['Professor', 'Administrator', 'Academic Counselor'])

        sem = self.schedule.get_semester(flask_session['SELECTED-SEMESTER'])
        month = self._get_selected_month()
        year = sem.year

        course = self.courses.get_course(course_id)
        students = self.user.get_students_in_course(course_id)

        students_and_time = {}
        for student, attendance in students:
            students_and_time[student] = {}
            students_and_time[student]['attendance'] = attendance
            students_and_time[student]['time'] = self.user.get_average_time_in_course(student.id, course[0].id)

        sessions = self.session_.get_sessions(course_id)
        sessions_and_attendance = {}
        for lab_session, schedule in sessions:
            sessions_and_attendance[lab_session] = {}
            sessions_and_attendance[lab_session]['schedule'] = schedule
            sessions_and_attendance[lab_session]['attendance'] = self.session_.get_session_attendees_with_dup(course[0].id, lab_session.id)

        return render_template('reports/view_course.html', **locals())

    def export_course_session_csv(self, course_id):
        self.slc.check_roles_and_route(['Professor', 'Administrator', 'Academic Counselor'])

        sem = self.schedule.get_semester(flask_session['SELECTED-SEMESTER'])
        term = sem.term[:2]
        year = sem.year
        lab = ''
        for letter in app.config['LAB_TITLE'].split():
            lab += letter[0]

        my_list = [['Date', 'DOW', 'Time', 'Attendees']]

        sessions = self.session_.get_sessions(course_id)
        course = self.courses.get_course(course_id)
        csv_course_info = '{0}{1} ({2})'.format(course[0].dept, course[0].course_num, course[0].title)

        total_attendance = 0
        for sess, schedule in sessions:
            sub_list = [sess.date.strftime('%m/%d/%Y'), self._get_dayofweek(schedule.dayofWeek),
                        self._datetimeformatter(sess.schedStartTime) + ' - ' +
                        self._datetimeformatter(sess.schedEndTime)]
            attendance_per_session = self.session_.get_session_attendees_with_dup(course_id, sess.id)
            sub_list.append(len(attendance_per_session))
            total_attendance += len(attendance_per_session)
            my_list.append(sub_list)

        my_list.append(['', '', 'Total', total_attendance])

        csv_name = '{0}{1}_{2}_SessionAttendance_{3}'.format(term, year, lab, csv_course_info)

        return self.export_csv(my_list, csv_name)

    def export_course_session_attendance_csv(self, course_id):
        self.slc.check_roles_and_route(['Professor', 'Administrator', 'Academic Counselor'])

        sem = self.schedule.get_semester(flask_session['SELECTED-SEMESTER'])
        term = sem.term[:2]
        year = sem.year
        lab = ''
        for letter in app.config['LAB_TITLE'].split():
            lab += letter[0]

        csv_name = '{0}{1}_{2}_SessionAttendance'.format(term, year, lab)

        my_list = [['First Name', 'Last Name', 'Sessions', 'Avg Time']]

        students = self.user.get_students_in_course(course_id)

        total_attendance = 0
        total_time = 0
        index = 0
        for student, attendance in students:
            index += 1
            sub_list = [student.firstName, student.lastName, attendance]
            total_attendance += attendance
            time = self.user.get_average_time_in_course(student.id, course_id)
            avg_time = 0
            for times, user in time:
                if times.timeOut and times.timeIn:
                    avg_time += (((times.timeOut - times.timeIn).total_seconds())/60)

            total_time += avg_time/len(time)
            sub_list.append(str(round(avg_time/len(time))) + ' min')
            my_list.append(sub_list)

        my_list.append(['', 'Total:', total_attendance, total_time/index])

        return self.export_csv(my_list, csv_name)

    def export_csv(self, data, csv_name):

        with open(csv_name + '.csv', 'w+') as csvfile:
            filewriter = csv.writer(csvfile)

            my_list = [csv_name, 'Exported on:', datetime.now().strftime('%m/%d/%Y')]
            filewriter.writerow(my_list)
            my_list = []
            filewriter.writerow(my_list)

            for row in data:
                filewriter.writerow(row)

        with open(csv_name + '.csv', 'rb') as f:
            return Response(
                f.read(),
                mimetype="text/csv",
                headers={"Content-disposition": "attachment; filename=" + csv_name + '.csv'})

    def _get_selected_month(self):
        sem = self.schedule.get_semester(flask_session['SELECTED-SEMESTER'])
        term = sem.term
        if term == 'Interim':
            return 1
        elif term == 'Spring':
            return 2
        elif term == 'Fall':
            return 9
        else:
            return 6

    def _get_dayofweek(self, day_value):
        day = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        return day[day_value]

    def _datetimeformatter(self, value, custom_format='%l:%M%p'):
        if value:
            return (datetime.min + value).strftime(custom_format)
        else:
            return '???'

    def _set_semester_selector(self, year, month):
        if month == 1:
            term = 'Interim'
        elif month in (2, 3, 4, 5):
            term = 'Spring'
        elif month in (8, 9, 10, 11, 12):
            term = 'Fall'
        else:
            term = 'Summer'
        sem = self.schedule.get_semester_by_year(year, term)

        # Sets the attribute 'active' of all the semesters to 0 so none are active
        for semester in flask_session['SEMESTER-LIST']:
            if semester['id'] == sem.id:
                semester['active'] = 1  # activates the semester chosen
            else:
                semester['active'] = 0  # deactivates all others
        # Sets the SELECTED-SEMESTER
        flask_session['SELECTED-SEMESTER'] = int(sem.id)
        # Lets the session know it was modified
        flask_session.modified = True

