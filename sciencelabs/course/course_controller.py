# Packages
from sqlalchemy import select

# Local
from sciencelabs import conn
from sciencelabs.db_repository import course


class CourseController():
    def __init__(self):
        super(CourseController, self).__init__

    def get_course_info(self):
        # TODO STILL NEED SOME DATA
        course_list = conn.execute(select([course]).where(course.c.semester_id == 40013)) # TODO This will need to be updated so you can pass in a semester id
        courses = []
        for row in course_list:
            courses.append([
                row[12],
                row[6],
                row[8] + row[5],
                'Professor',
                'Enr'
            ])
        return courses