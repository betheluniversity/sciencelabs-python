from sqlalchemy import *

from sciencelabs.db_repository import Base
from sciencelabs.db_repository import session
from sciencelabs.db_repository.UserRepo import User
from sciencelabs.db_repository.CourseProfessorsRepo import CourseProfessors


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
                .filter(User.id == CourseProfessors.professor_id).filter(CourseProfessors.course_id == Course.id).all())

    def get_student_course_info(self):
        # Session = sessionmaker(bind=db)
        # session = Session()
        # # q = (session.query(Course.dept, Course.course_num, Course.title, Course.section, Course.professor_id).all())
        # return session.query(Course.dept)
        return (session.query(Course.dept, Course.course_num, Course.title, Course.section, User.firstName,
                              User.lastName)
                .filter(User.id == CourseProfessors.professor_id).filter(CourseProfessors.course_id == Course.id).all())


class CourseFunctions:

    def get_report_course_info(self):
        # # TODO STILL NEED SOME DATA
        courses = []
        for row in Course.get_course_info(self):
            courses.append([
                row[0] + row[1],
                row[2],
                row[3],
                str(row[4]) + ' ' + str(row[5]),
                'Tot',
                'Unq',
                'Pct'
            ])
            # print(all)
        # print(Course.get_course_info(self)[1][0])
        return courses

    def get_course_info(self):
        # # TODO STILL NEED SOME DATA
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
