# Packages
from sqlalchemy import select

# Local
from sciencelabs import conn
from sciencelabs.db_repository import user
from sciencelabs.db_repository import course


class ReportController:
    def __init__(self):
        super(ReportController, self).__init__

    def get_student_info(self):
        # TODO STILL NEED ATTENDANCE AND REPORT
        student_list = conn.execute(select([user]))
        students = []
        for row in student_list:
            students.append([
                row[4],
                row[3],
                row[5],
                'attendance',
                'report'
            ])
        return students

    def get_course_info(self):
        # TODO STILL NEED SOME DATA
        course_list = conn.execute(select([course]).where(course.c.semester_id == 40013)) # TODO This will need to be updated so you can pass in a semester id
        courses = []
        for row in course_list:
            courses.append([
                row[8] + row[5],
                row[12],
                row[6],
                'Prof',
                'Tot',
                'Unq',
                'Pct',
                'Report'
            ])
        return courses

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
