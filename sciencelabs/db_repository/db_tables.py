from sqlalchemy import Column, Integer, String, DateTime

from sciencelabs.db_repository import base


class CourseCode_Table(base):
    __tablename__ = 'CourseCode'
    id = Column(Integer, primary_key=True)
    dept = Column(String)
    courseNum = Column(String)
    underived = Column(String)
    active = Column(Integer)
    courseName = Column(String)


class CourseProfessors_Table(base):
    __tablename__ = 'CourseProfessors'
    course_id = Column(Integer, primary_key=True)
    professor_id = Column(Integer)


class Course_Table(base):
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


class CourseViewer_Table(base):
    __tablename__ = 'CourseViewer'
    course_id = Column(Integer, primary_key=True)
    user_id = Column(Integer)


class ReservationCourses_Table(base):
    __tablename__ = 'ReservationCourses'
    id = Column(Integer, primary_key=True)
    reservation_id = Column(Integer)
    course_id = Column(Integer)


class Role_Table(base):
    __tablename__ = 'Role'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    role = Column(String)
    sort = Column(Integer)


class RoomGrouping_Table(base):
    __tablename__ = 'RoomGrouping'
    id = Column(Integer, primary_key=True)
    capacity = Column(Integer)


class ScheduleCourseCodes_Table(base):
    __tablename__ = 'ScheduleCourseCodes'
    schedule_id = Column(Integer, primary_key=True)
    coursecode_id = Column(Integer, primary_key=True)


class Schedule_Table(base):
    __tablename__ = 'Schedule'
    id = Column(Integer, primary_key=True)
    usingReserveSys = Column(Integer)
    name = Column(String)
    room = Column(String)
    startTime = Column(String)
    endTime = Column(String)
    dayofWeek = Column(Integer)
    term = Column(String)
    deletedAt = Column(String)


class Semester_Table(base):
    __tablename__ = 'Semester'
    id = Column(Integer, primary_key=True)
    term = Column(String)
    startDate = Column(String)
    endDate = Column(String)
    year = Column(Integer)
    active = Column(Integer)


class SessionCourseCodes_Table(base):
    __tablename__ = 'SessionCourseCodes'
    session_id = Column(Integer, primary_key=True)
    coursecode_id = Column(Integer, primary_key=True)


class SessionCourses_Table(base):
    __tablename__ = 'SessionCourses'
    studentsession_id = Column(Integer, primary_key=True)
    course_id = Column(Integer, primary_key=True)


class Session_Table(base):
    __tablename__ = 'Session'
    id = Column(Integer, primary_key=True)
    semester_id = Column(Integer)
    schedule_id = Column(Integer)
    usingReserveSys = Column(Integer)
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
    zoom_url = Column(String)
    capacity = Column(Integer)
    room_group_id = Column(Integer)


class SessionReservations_Table(base):
    __tablename__ = 'SessionReservations'
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer)
    user_id = Column(Integer)
    seat_number = Column(Integer)


class StudentSession_Table(base):
    __tablename__ = 'StudentSession'
    id = Column(Integer, primary_key=True)
    timeIn = Column(String)
    timeOut = Column(String)
    studentId = Column(Integer)
    sessionId = Column(Integer)
    otherCourse = Column(Integer)
    otherCourseName = Column(String)
    online = Column(Integer)


class TutorSchedule_Table(base):
    __tablename__ = 'TutorSchedule'
    id = Column(Integer, primary_key=True)
    schedTimeIn = Column(String)
    schedTimeOut = Column(String)
    isLead = Column(Integer)
    tutorId = Column(Integer)
    scheduleId = Column(Integer)


class TutorSession_Table(base):
    __tablename__ = 'TutorSession'
    id = Column(Integer, primary_key=True)
    schedTimeIn = Column(DateTime)
    schedTimeOut = Column(DateTime)
    timeIn = Column(DateTime)
    timeOut = Column(DateTime)
    isLead = Column(Integer)
    tutorId = Column(Integer)
    sessionId = Column(Integer)
    substitutable = Column(Integer)


class user_course_Table(base):
    __tablename__ = 'user_course'
    user_id = Column(Integer, primary_key=True)
    course_id = Column(Integer)


class user_role_Table(base):
    __tablename__ = 'user_role'
    user_id = Column(Integer, primary_key=True)
    role_id = Column(Integer)


class User_Table(base):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    firstName = Column(String)
    lastName = Column(String)
    email = Column(String)
    send_email = Column(Integer)
    deletedAt = Column(String)
