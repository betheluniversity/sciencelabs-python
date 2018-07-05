# Packages
from sqlalchemy import MetaData, Table
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import create_engine

# Local
from app_settings import app_settings

# Local
from sciencelabs import db

metadata = MetaData()

db = create_engine(app_settings['DATABASE_KEY'])
conn = db.connect()

# Tables
course = Table('Course', metadata, autoload=True, autoload_with=db)
course_code = Table('CourseCode', metadata, autoload=True, autoload_with=db)
course_profs = Table('CourseProfessors', metadata, autoload=True, autoload_with=db)
course_viewer = Table('CourseViewer', metadata, autoload=True, autoload_with=db)
role = Table('Role', metadata, autoload=True, autoload_with=db)
schedule = Table('Schedule', metadata, autoload=True, autoload_with=db)
schedule_course_codes = Table('ScheduleCourseCodes', metadata, autoload=True, autoload_with=db)
semester = Table('Semester', metadata, autoload=True, autoload_with=db)
session = Table('Session', metadata, autoload=True, autoload_with=db)
session_course_codes = Table('SessionCourseCodes', metadata, autoload=True, autoload_with=db)
session_courses = Table('SessionCourses', metadata, autoload=True, autoload_with=db)
student_session = Table('StudentSession', metadata, autoload=True, autoload_with=db)
tutor_schedule = Table('TutorSchedule', metadata, autoload=True, autoload_with=db)
tutor_session = Table('TutorSession', metadata, autoload=True, autoload_with=db)
user = Table('User', metadata, autoload=True, autoload_with=db)
user_course = Table('user_course', metadata, autoload=True, autoload_with=db)
user_role = Table('user_role', metadata, autoload=True, autoload_with=db)

Base = declarative_base()
Session = sessionmaker(bind=db)
session = Session()

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
        # Session = sessionmaker(bind=db)
        # session = Session()
        # # q = (session.query(Course.dept, Course.course_num, Course.title, Course.section, Course.professor_id).all())
        # return session.query(Course.dept)
        return (session.query(Course.dept, Course.course_num, Course.title, Course.section, User.firstName, User.lastName).filter(User.id == CourseProfessors.professor_id).filter(CourseProfessors.course_id == Course.id).all())


class CourseCode(Base):
    __tablename__ = 'CourseCode'
    id = Column(Integer, primary_key=True)
    dept = Column(String)
    courseNum = Column(String)
    underived = Column(String)
    active = Column(Integer)
    courseName = Column(String)


class CourseProfessors(Base):
    __tablename__ = 'CourseProfessors'
    course_id = Column(Integer, primary_key=True)
    professor_id = Column(Integer)


class CourseViewer(Base):
    __tablename__ = 'CourseViewer'
    course_id = Column(Integer, primary_key=True)
    user_id = Column(Integer)


class Role(Base):
    __tablename__ = 'Role'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    role = Column(String)
    sort = Column(Integer)


class Schedule(Base):
    __tablename__ = 'Schedule'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    room = Column(String)
    startTime = Column(String)
    endTime = Column(String)
    dayofWeek = Column(Integer)
    term = Column(String)
    deletedAt = Column(String)


class ScheduleCourseCodes(Base):
    __tablename__ = 'ScheduleCourseCodes'
    schedule_id = Column(Integer, primary_key=True)
    coursecode_id = Column(Integer)


class Semester(Base):
    __tablename__ = 'Semester'
    id = Column(Integer, primary_key=True)
    term = Column(String)
    startDate = Column(String)
    endDate = Column(String)
    year = Column(Integer)
    active = Column(Integer)


class Session(Base):
    __tablename__ = 'Session'
    id = Column(Integer, primary_key=True)
    semester_id = Column(Integer)
    schedule_id = Column(Integer)
    date = Column(String)
    schedStartTime = Column(String)
    schedEndTime = Column(String)
    startTime = Column(String)
    endTime = Column(String)
    room = Column(String)
    open = Column(Integer)
    hash = Column(String)
    comments = Column(String)
    deletedAt = Column(String)
    openerId = Column(Integer)
    anonStudents = Column(Integer)
    name = Column(String)


class SessionCourseCodes(Base):
    __tablename__ = 'SessionCourseCodes'
    session_id = Column(Integer, primary_key=True)
    coursecode_id = Column(Integer)


class SessionCourses(Base):
    __tablename__ = 'SessionCourses'
    studentsession_id = Column(Integer, primary_key=True)
    course_id = Column(Integer)


class StudentSession(Base):
    __tablename__ = 'StudentSession'
    id = Column(Integer, primary_key=True)
    timeIn = Column(String)
    timeOut = Column(String)
    studentId = Column(Integer)
    sessionId = Column(Integer)
    otherCourse = Column(Integer)
    otherCourseName = Column(String)


class TutorSchedule(Base):
    __tablename__ = 'TutorSchedule'
    id = Column(Integer, primary_key=True)
    schedTimeIn = Column(String)
    schedTimeOut = Column(String)
    lead = Column(Integer)
    tutorId = Column(Integer)
    scheduleId = Column(Integer)


class User(Base):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    firstName = Column(String)
    lastName = Column(String)
    email = Column(String)
    send_email = Column(Integer)
    deletedAt = Column(String)


class user_course(Base):
    __tablename__ = 'user_course'
    user_id = Column(Integer, primary_key=True)
    course_id = Column(Integer)


class user_role(Base):
    __tablename__ = 'user_role'
    user_id = Column(Integer, primary_key=True)
    role_id = Column(Integer)

# print("WOW")
# q = (session.query(Role.name).filter(User.id == user_role.user_id).filter(user_role.role_id == Role.id).all())
# print(q)
# print("WOW")
#
# print("YES")
# q = (session.query(CourseProfessors.professor_id, User.id, User.firstName, User.lastName).filter(User.id == CourseProfessors.professor_id).filter(Semester.active == 1).all())
# print(q)
# print("NO")


# print('<--------------------------------------------------------------------------------->')
#
# role = Table('Role', metadata, autoload=True, autoload_with=db)
# print(repr(role))
#
# print('<--------------------------------------------------------------------------------->')
#
# s = select([user])
# result = conn.execute(s)
# for row in result:
#     print(row)
#
# print('<--------------------------------------------------------------------------------->')
#
# s = select([user.c.username])
# result = conn.execute(s)
# for row in result:
#     print(row)
#
# print('<--------------------------------------------------------------------------------->')
#
# s = select([role])
# result = conn.execute(s)
# for row in result:
#     print(row)
#
# print('<--------------------------------------------------------------------------------->')
#
# result = conn.execute(select([user, user.c.password]))
# for row in result:
#     print(row)
#
# print('<--------------------------------------------------------------------------------->')
#
# result = conn.execute(select([user, user.c.username]).where(user.c.username == 'bam95899'))  # or user.c.usernmae
# for row in result:
#     print(row)
#
# result.close()
