from sqlalchemy import *

from sciencelabs.db_repository import Base
from sciencelabs.db_repository import session
from sciencelabs.db_repository.CourseCodeRepo import CourseCode


class ScheduleCourseCodes(Base):
    __tablename__ = 'ScheduleCourseCodes'
    schedule_id = Column(Integer, primary_key=True)
    coursecode_id = Column(Integer)

    def get_schedule_courses(self, schedule_id):
        courses = session.query(ScheduleCourseCodes, CourseCode)\
            .filter(ScheduleCourseCodes.schedule_id == schedule_id)\
            .filter(ScheduleCourseCodes.coursecode_id == CourseCode.id)\
            .all()
        schedule_courses = []
        for schedulecoursecode, coursecode in courses:
            schedule_courses.append(coursecode.dept + ' ' + coursecode.courseNum)
        return schedule_courses
