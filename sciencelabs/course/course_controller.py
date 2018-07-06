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