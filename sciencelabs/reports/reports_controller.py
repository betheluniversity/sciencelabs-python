# Packages
from sqlalchemy import select
from sqlalchemy.util import KeyedTuple

# Local
from sciencelabs import conn
from sciencelabs.db_repository import user
from sciencelabs.db_repository import course
from sciencelabs.db_repository import semester
from sciencelabs.db_repository import Course


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
        # # TODO STILL NEED SOME DATA
        # semester_list = conn.execute(select([semester.c.id]).where(semester.c.active == 1))
        # for data in semester_list:
        #     active_semester = data[0]
        # course_list = conn.execute(select([course]).where(course.c.semester_id == active_semester)) # TODO This will need to be updated so you can pass in a semester id
        # key = KeyedTuple([])
        # courses = []
        # for row in course_list:
        #     key = KeyedTuple([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10],
        #                       row[11], row[12], row[13], row[14], row[15]], labels=['id', 'professor_id', 'semester_id',
        #                                                                             'begin_date', 'begin_time',
        #                                                                             'course_num', 'section', 'crn',
        #                                                                             'dept', 'end_date', 'end_time',
        #                                                                             'meeting_day', 'title',
        #                                                                             'course_code_id', 'num_attendees',
        #                                                                             'room'])
        #     courses.append([
        #         key.dept + key.course_num,  # dept + course_num
        #         key.title,  # title
        #         key.section,  # section
        #         'Prof',
        #         'Tot',
        #         'Unq',
        #         'Pct',
        #         'report'
        #     ])
        # return courses
        courses = []
        for all in Course.get_student_course_info(self):
            courses.append([
                all[0] + all[1],
                all[2],
                all[3],
                str(all[4]) + ' ' + str(all[5]),
                'Tot',
                'Unq',
                'Pct'
            ])
            # print(all)
        # print(Course.get_course_info(self)[1][0])

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
