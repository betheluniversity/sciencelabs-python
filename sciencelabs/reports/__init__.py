# Packages
from flask import render_template, Response, session
from flask_classy import FlaskView, route
import calendar
import csv
from datetime import datetime

# Local
from sciencelabs import app_settings
from sciencelabs import app
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

        semester_list = session['SEMESTER-LIST']
        # student_info = self.user.get_student_info_test(session['SELECTED-SEMESTER'])
        student_info = self.user.get_student_info()
        return render_template('reports/student.html', **locals())

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

    def export_student_csv(self):

        term = 'SP'[:2]  # SEMESTER.TERM[:2]
        year = '2018'  # SEMESTER.YEAR
        lab = ''
        for letter in app_settings['LAB_TITLE'].split():
            lab += letter[0]

        csv_name = '%s%s_%s_StudentReport' % (term, year, lab)

        my_list = [['Last', 'First', 'Email', 'Attendance']]

        for student, attendance in self.user.get_student_info():
            my_list.append([student.lastName, student.firstName, student.email, attendance])

        return self.export_csv(my_list, csv_name)

    def semester(self):
        sess = self.session_.get_closed_sessions()
        month = int(str(sess[0].date)[5:7])
        year = int(str(sess[0].date)[:4])

        semester = self.schedule.get_active_semester()
        semester_list = session['SEMESTER-LIST']
        term_info = self.schedule.get_term_report()
        term_attendance = self.schedule.get_session_attendance()
        unique_attendance_info = self.user.get_unique_session_attendance()
        session_ = self.session_
        user_ = self.user

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

        # TODO MAKE SURE SO NOT HARD-CODED
        unscheduled_sessions = self.session_.get_unscheduled_sessions('2018', 'Spring')

        return render_template('reports/term.html', **locals())

    def export_semester_csv(self):
        term = 'SP'[:2]  # SEMESTER.TERM[:2]
        year = '2018'  # SEMESTER.YEAR
        lab = ''
        for letter in app_settings['LAB_TITLE'].split():
            lab += letter[0]

        csv_name = '%s%s_%s_TermReport' % (term, year, lab)

        my_list = [['Schedule Statistics for Closed Sessions']]
        my_list.append(['Schedule Name', 'DOW', 'Start Time', 'Stop Time', 'Number of Sessions', 'Attendance', 'Percentage'])

        term_attendance = self.schedule.get_session_attendance()
        total_attendance = 0
        attendance_list = []
        for sessions in term_attendance:
            total_attendance += sessions[1]
            attendance_list += [sessions[1]]

        index = 0
        session_count = 0
        for schedule, sessions in self.schedule.get_term_report():
            session_count += sessions
            # TODO FIX SCHEDULE.DAYOFWEEK AND SCHEDULE.STARTTIME/SCHEDULE/ENDTIME
            my_list.append([schedule.name, schedule.dayofWeek, schedule.startTime, schedule.endTime, sessions,
                       attendance_list[index],
                       str(round(((attendance_list[index] / total_attendance) * 100))) + '%'])
            index += 1

        my_list.append(['', '', '', 'Total:', session_count, total_attendance, '100%'])
        my_list.append([])
        my_list.append(['Unscheduled Sessions', 'Date', 'Start Time', 'Stop Time', 'Attendance'])

        # TODO MAKE SURE SO NOT HARD-CODED
        unscheduled_sessions = self.session_.get_unscheduled_sessions('2018', 'Spring')
        total_unscheduled = 0
        for sessions in unscheduled_sessions:
            # TODO FIX SESSIONS.STARTTIME AND SESSIONS.ENDTIME
            my_list.append(['', sessions.date.strftime('%m/%d/%Y'), sessions.startTime, sessions.endTime, len(self.user.get_session_students(sessions.id)) + sessions.anonStudents])
            total_unscheduled += len(self.user.get_session_students(sessions.id)) + sessions.anonStudents

        my_list.append(['', '', 'Total', total_unscheduled])

        return self.export_csv(my_list, csv_name)

    @route('/month/<int:year>/<int:month>')
    def month(self, year, month):
        sess = self.session_.get_closed_sessions()
        first_month = int(str(sess[0].date)[5:7])
        first_year = int(str(sess[0].date)[:4])
        cal = calendar
        months = self.base.months
        selected_year = year
        selected_month = month
        semester_list = session['SEMESTER-LIST']
        if month == 1:
            term = 'Interim'
        elif month in (2, 3, 4, 5):
            term = 'Spring'
        elif month in (8, 9, 10, 11, 12):
            term = 'Fall'
        else:
            term = 'Summer'
        schedule_info = self.schedule.get_yearly_schedule_tab_info(selected_year, term)
        sessions = self.session_.get_semester_closed_sessions(selected_year, term)
        unscheduled_sessions = self.session_.get_unscheduled_sessions(selected_year, term)
        schedule_ = self.schedule
        session_ = self.session_
        user_ = self.user
        monthly_sessions = self.session_.get_monthly_sessions((str(year) + '-' + str(month) + '-01'), (str(year) + '-' + str(month) + '-31'))
        return render_template('reports/monthly.html', **locals())

    def export_monthly_summary_csv(self, year, month):
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
        for letter in app_settings['LAB_TITLE'].split():
            lab += letter[0]
        selected_month = self.base.months[month - 1]

        csv_name = '%s%s_%s_%s_SummaryReport' % (term_abbr, year, lab, selected_month)

        my_list = [['Schedule Name', 'DOW', 'Scheduled Time', 'Total Attendance', '% Total']]

        schedule_info = self.schedule.get_yearly_schedule_tab_info(year, term)
        monthly_sessions = self.session_.get_monthly_sessions((str(year) + '-' + str(month) + '-01'), (str(year) + '-' + str(month) + '-31'))

        total_attendance = 0
        for schedule in schedule_info:
            for session in monthly_sessions:
                session_schedule = self.schedule.get_schedule_from_session(session.id)
                attendance = self.session_.get_session_attendees(session.id)
                if schedule and session_schedule:
                    if schedule.id == session_schedule.id:
                        total_attendance += attendance.count() + session.anonStudents

        for schedule in schedule_info:
            total_attendance_per_schedule = 0
            for session in monthly_sessions:
                session_schedule = self.schedule.get_schedule_from_session(session.id)
                attendance = self.session_.get_session_attendees(session.id)
                if schedule and session_schedule:
                    if schedule.id == session_schedule.id:
                        total_attendance_per_schedule += attendance.count() + session.anonStudents
            # TODO FIX SCHEDULE.DAYOFWEEK AND SCHEDULE.STARTTIME/SCHEDULE.ENDTIME
            my_list.append([schedule.name, schedule.dayofWeek, str(schedule.startTime) + ' - ' + str(schedule.endTime), total_attendance_per_schedule, str(round((total_attendance_per_schedule/total_attendance)*100, 1)) + '%'])

        unscheduled_sessions = self.session_.get_unscheduled_sessions(year, term)
        total_unscheduled = 0
        if unscheduled_sessions:
            for session in unscheduled_sessions:
                total_unscheduled += (len(self.user.get_session_students(session.id))) + session.anonStudents
            total_attendance += total_unscheduled

        my_list.append(['Unscheduled Sessions', '', '', total_unscheduled, str(round((total_unscheduled / total_attendance) * 100, 1)) + '%'])

        my_list.append(['', '', 'Total', total_attendance])

        return self.export_csv(my_list, csv_name)

    def export_monthly_detail_csv(self, year, month):
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
        for letter in app_settings['LAB_TITLE'].split():
            lab += letter[0]
        selected_month = self.base.months[month - 1]

        csv_name = '%s%s_%s_%s_DetailReport' % (term_abbr, year, lab, selected_month)

        my_list = [['Name', 'Date', 'DOW', 'Scheduled Time', 'Total Attendance']]

        cal = calendar

        monthly_sessions = self.session_.get_monthly_sessions((str(year) + '-' + str(month) + '-01'), (str(year) + '-' + str(month) + '-31'))
        total_attendance = 0
        for session in monthly_sessions:
            attendance = self.session_.get_session_attendees(session.id)
            total_attendance += attendance.count() + session.anonStudents
            # TODO FIX CAL.WEEKDAY AND SESSION.SCHEDSTARTTIME/SESSION.SCHEDENDTIME
            my_list.append([session.name, session.date.strftime('%m/%d/%Y'), (cal.weekday(((int(str(session.date)[:4]))), ((int(str(session.date)[5:7]))), (((int(str(session.date)[8:]))))) + 1) % 7, str(session.schedStartTime) + ' - ' + str(session.schedEndTime), attendance.count() + session.anonStudents])

        my_list.append(['', '', 'Total:', total_attendance])

        return self.export_csv(my_list, csv_name)

    def annual(self):
        sess = self.session_.get_closed_sessions()
        month = int(str(sess[0].date)[5:7])
        year = int(str(sess[0].date)[:4])
        cumulative = self.base.cumulative

        session_ = self.session_
        semesters = self.session_.get_years()
        return render_template('reports/cumulative.html', **locals())

    def export_cumulative_csv(self):
        lab = ''
        for letter in app_settings['LAB_TITLE'].split():
            lab += letter[0]

        csv_name = '%s_CumulativeAttendance' % lab

        my_list = [['Year', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Fall', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Spring', 'Jun', 'Jul', 'Summer', 'Total']]

        total_dict = {'8': 0, '9': 0, '10': 0, '11': 0, '12': 0, 'fall': 0, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0,
                      'spring': 0, '6': 0, '7': 0, 'summer': 0, 'total': 0}

        semesters = self.session_.get_years()
        for semester in semesters:
            sub_list = [str(semester.year) + '-' + str(semester.year + 1)]
            fall_total = 0
            for month in range(8, 13):
                monthly_sessions = self.session_.get_monthly_sessions((str(semester.year)+ '-' + str(month) + '-1'), (str(semester.year) + '-' + str(month) + '-31'))
                total_attendance = 0
                for sessions in monthly_sessions:
                    attendance = self.session_.get_session_attendees(sessions.id).count()
                    total_attendance += attendance + sessions.anonStudents
                    total_dict[str(month)] += attendance + sessions.anonStudents
                sub_list.append(total_attendance)
                fall_total += total_attendance
            total_dict['fall'] += fall_total
            sub_list.append(fall_total)
            monthly_sessions = self.session_.get_monthly_sessions((str((semester.year + 1)) + '-' + str(1) + '-1'), (str((semester.year + 1)) + '-' + str(1) + '-31'))
            total_attendance = 0
            for sessions in monthly_sessions:
                attendance = self.session_.get_session_attendees(sessions.id).count()
                total_attendance += attendance + sessions.anonStudents
                total_dict[str(1)] += attendance + sessions.anonStudents
            sub_list.append(total_attendance)
            interim_total = total_attendance
            spring_total = 0
            for month in range(2, 6):
                monthly_sessions = self.session_.get_monthly_sessions((str((semester.year + 1)) + '-' + str(month) + '-1'), (str((semester.year + 1)) + '-' + str(month) + '-31'))
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
                monthly_sessions = self.session_.get_monthly_sessions((str((semester.year + 1)) + '-' + str(month) + '-1'), (str((semester.year + 1)) + '-' + str(month) + '-31'))
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

        cumulative = self.base.cumulative
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

        return self.export_csv(my_list, csv_name)

    def session(self):
        sess = self.session_.get_closed_sessions()
        month = int(str(sess[0].date)[5:7])
        year = int(str(sess[0].date)[:4])

        months = self.base.months
        semester_list = session['SEMESTER-LIST']
        sessions = self.session_.get_closed_sessions()
        session_ = self.session_
        return render_template('reports/session.html', **locals())

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

    def export_session_csv(self):
        term = 'SP'[:2]  # SEMESTER.TERM[:2]
        year = '2018'  # SEMESTER.YEAR
        lab = ''
        for letter in app_settings['LAB_TITLE'].split():
            lab += letter[0]

        csv_name = '%s%s_%s_SessionReport' % (term, year, lab)

        my_list = [['Date', 'Name', 'DOW', 'Start Time', 'End Time', 'Room', 'Total Attendance', 'Comments']]

        sessions = self.session_.get_closed_sessions()
        dates = []
        for session in sessions:
            if (str(session.date)[5:7]) not in dates:
                dates.append(str(session.date)[5:7])

        total_attendance = 0
        for date in dates:
            for session in sessions:
                if (str(session.date)[5:7]) == date:
                    attendance = len(self.session_.get_session_students(session.id))
                    # TODO FIX SESSION.GET_DAYOFWEEK_FROM_SESSION
                    my_list.append([session.date.strftime('%m/%d/%Y'), session.name, self.session_.get_dayofWeek_from_session(session.id).dayofWeek, session.startTime, session.endTime, session.room, attendance, session.comments])
                    total_attendance += attendance

        my_list.append(['', '', '', '', '', 'Total:', total_attendance])

        return self.export_csv(my_list, csv_name)

    def course(self):
        sess = self.session_.get_closed_sessions()
        month = int(str(sess[0].date)[5:7])
        year = int(str(sess[0].date)[:4])

        semester = self.schedule.get_active_semester()
        semester_list = session['SEMESTER-LIST']
        user_ = self.user
        course_info = self.courses.get_active_course_info()
        return render_template('reports/course.html', **locals())

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

    def export_course_session_csv(self, course_id):
        term = 'SP'[:2]  # SEMESTER.TERM[:2]
        year = '2018'  # SEMESTER.YEAR
        lab = ''
        for letter in app_settings['LAB_TITLE'].split():
            lab += letter[0]

        my_list = [['Date', 'DOW', 'Time', 'Attendees']]

        sessions = self.session_.get_sessions(course_id)
        course = self.courses.get_course(course_id)
        csv_course_info = course[0].dept + course[0].course_num + ' (' + course[0].title + ')'

        total_attendance = 0
        for session, schedule in sessions:
            # TODO FIX SCHEDULE.DAYOFWEEK AND SESSION.SCHEDSTARTTIME/SESSION.SCHEDSTARTTIME
            sub_list = [session.date.strftime('%m/%d/%Y'), schedule.dayofWeek, str(session.schedStartTime) + ' - ' + str(session.schedEndTime)]
            attendance_per_session = self.session_.get_session_attendees_with_dup(course_id, session.id)
            sub_list.append(len(attendance_per_session))
            total_attendance += len(attendance_per_session)
            my_list.append(sub_list)

        my_list.append(['', '', 'Total', total_attendance])

        csv_name = '%s%s_%s_SessionAttendance_%s' % (term, year, lab, csv_course_info)

        return self.export_csv(my_list, csv_name)

    def export_course_session_attendance_csv(self, course_id):
        term = 'SP'[:2]  # SEMESTER.TERM[:2]
        year = '2018'  # SEMESTER.YEAR
        lab = ''
        for letter in app_settings['LAB_TITLE'].split():
            lab += letter[0]

        csv_name = '%s%s_%s_SessionAttendance' % (term, year, lab)

        my_list = [['First Name', 'Last Name', 'Sessions', 'Avg Time']]

        students = self.user.get_students_in_course(course_id)

        sub_list = []
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
