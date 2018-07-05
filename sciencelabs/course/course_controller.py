# Packages
from sqlalchemy import select

# Local
from sciencelabs import conn
from sciencelabs.db_repository import course
from sciencelabs.db_repository import course_profs
from sciencelabs.db_repository import semester
from sciencelabs.db_repository import Course


class CourseController():
    def __init__(self):
        super(CourseController, self).__init__

    def get_course_info(self):
        # # TODO STILL NEED SOME DATA
        # mathchy_match = conn.execute(select([course_profs]))
        # semester_list = conn.execute(select([semester.c.id]).where(semester.c.active == 1))
        # for data in semester_list:
        #     active_semester = data[0]
        # course_list = conn.execute(select([course]).where(course.c.semester_id == active_semester)) # TODO This will need to be updated so you can pass in a semester id
        # courses = []
        # for row in course_list:
        #     courses.append([
        #         row[12],  # title
        #         row[6],  # section
        #         row[8] + row[5],  # dept + course_num
        #         'Professor',
        #         'Enr'
        #     ])
        # return courses
        courses = []
        for all in Course.get_course_info(self):
            courses.append([
                all[0],
                all[1],
                all[2] + all[3],
                str(all[4]) + ' ' + str(all[5]),
                all[6]
            ])
        return courses