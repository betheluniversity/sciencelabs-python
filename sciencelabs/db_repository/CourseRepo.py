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
        return (session.query(Course.title, Course.section, Course.dept, Course.course_num, User.firstName, User.lastName, Course.num_attendees).filter(Course.num_attendees).filter(User.id == CourseProfessors.professor_id).filter(CourseProfessors.course_id == Course.id).all())

    def get_student_course_info(self):
        # Session = sessionmaker(bind=db)
        # session = Session()
        # # q = (session.query(Course.dept, Course.course_num, Course.title, Course.section, Course.professor_id).all())
        # return session.query(Course.dept)
        return (session.query(Course.dept, Course.course_num, Course.title, Course.section, User.firstName, User.lastName).filter(User.id == CourseProfessors.professor_id).filter(CourseProfessors.course_id == Course.id).all())


class CourseFunctions:

    def get_report_course_info(self):
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