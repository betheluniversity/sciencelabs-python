from sqlalchemy import *

from sciencelabs.db_repository import Base
from sciencelabs.db_repository import session
from sciencelabs.db_repository.UserRepo import User
from sciencelabs.db_repository.CourseProfessorsRepo import CourseProfessors
from sciencelabs.db_repository.SemesterRepo import Semester


class Course(Base):
    __tablename__ = 'Course'
    id = Column(Integer, primary_key=True)
    professor_id = Column(Integer)
    semester_id = Column(Integer)
    begin_date = Column(String)
    begin_time = Column(String)
    course_num = Column(String)
    section = Column(Integer)
    crn = Column(Integer)
    dept = Column(String)
    end_date = Column(String)
    end_time = Column(String)
    meeting_day = Column(String)
    title = Column(String)
    course_code_id = Column(Integer)
    num_attendees = Column(Integer)
    room = Column(String)

    def get_course_info(self):
        return (session.query(Course.title, Course.section, Course.dept, Course.course_num, User.firstName,
                              User.lastName, Course.num_attendees).filter(Course.num_attendees)
                .filter(User.id == CourseProfessors.professor_id).filter(CourseProfessors.course_id == Course.id)
                .filter(Course.semester_id == Semester.id).filter(Semester.active == 1).all())

    def get_report_course_info(self):
        return (session.query(Course.dept, Course.course_num, Course.title, Course.section, User.firstName,
                              User.lastName)
                .filter(User.id == CourseProfessors.professor_id).filter(CourseProfessors.course_id == Course.id).filter(Course.semester_id == Semester.id).filter(Semester.active == 1).all())
