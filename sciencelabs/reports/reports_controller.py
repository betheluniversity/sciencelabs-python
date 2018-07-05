# Packages
from sqlalchemy import select

# Local
from sciencelabs import conn
from sciencelabs.db_repository import user
from sciencelabs.db_repository import course
from sciencelabs.db_repository import semester


class ReportController:
    def __init__(self):
        super(ReportController, self).__init__

    def get_student_info(self):
        # TODO STILL NEED ATTENDANCE AND REPORT
        student_list = conn.execute(select([user]))
        students = []
        for row in student_list:
            students.append([
                row[4],  # lastName
                row[3],  # firstName
                row[5],  # Email
                'attendance',
                'report'
            ])
        return students

    def get_course_info(self):
        # TODO STILL NEED SOME DATA\
        semester_list = conn.execute(select([semester.c.id]).where(semester.c.active == 1))
        for data in semester_list:
            active_semester = data[0]
        course_list = conn.execute(select([course]).where(course.c.semester_id == active_semester)) # TODO This will need to be updated so you can pass in a semester id
        courses = []
        for row in course_list:
            courses.append([
                row[8] + row[5],  # dept + course_num
                row[12],  # title
                row[6],  # section
                'Prof',
                'Tot',
                'Unq',
                'Pct',
                'report'
            ])
        return courses

    # TODO FINISH METHOD
    def get_closed_monthly_info(self):
        monthly = []
        for i in range(1, 8):
            monthly.append([
                'Schedule Name',
                'DOW',
                'Schedule Time',
                'Total Attendance',
                '% Total'
            ])
        return monthly

    # TODO FINISH METHOD
    def get_monthly_info(self):
        monthly = []
        for i in range(1, 27):
            monthly.append([
                'Name',
                'Date',
                'DOW',
                'Schedule Time',
                'Total Attendance',
                'report'
            ])
        return monthly

    # TODO FINISH METHOD
    def get_cumulative_info(self):
        return []

    # TODO FINISH METHOD
    def get_term_info(self):
        term = []
        for i in range(1, 8):
            term.append([
                "Schedule Name",
                "DOW",
                "Start Time",
                "Stop Time",
                "Number of Sessions",
                "Attendance",
                "Percentage"
            ])
        return term
