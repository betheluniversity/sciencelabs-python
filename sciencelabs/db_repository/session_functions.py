from sqlalchemy import func, distinct

from sciencelabs.db_repository import session
from sciencelabs.db_repository.db_tables import Session_Table, Semester_Table, User_Table, TutorSession_Table,\
    Course_Table, SessionCourses_Table, StudentSession_Table, Schedule_Table, CourseCode_Table



class Session:

    def get_closed_sessions(self):
        return (session.query(Session_Table)
                .filter(Session_Table.semester_id == Semester_Table.id).filter(Semester_Table.active == 1)
                .filter(Session_Table.startTime != None).all())

    def get_session(self, session_id):
        return session.query(Session_Table).filter(Session_Table.id == session_id).one()

    def get_session_tutors(self, session_id):

        return session.query(User_Table.id, User_Table.firstName, User_Table.lastName, TutorSession_Table.lead,
                             TutorSession_Table.timeIn, TutorSession_Table.timeOut)\
            .filter(TutorSession_Table.sessionId == session_id).filter(User_Table.id == TutorSession_Table.tutorId)\
            .order_by(TutorSession_Table.lead.desc())

    def get_session_tutor_names(self, session_id):
        return session.query(User_Table.id, User_Table.firstName, User_Table.lastName)\
            .filter(TutorSession_Table.sessionId == session_id).filter(User_Table.id == TutorSession_Table.tutorId)\
            .order_by(TutorSession_Table.lead.desc())

    def get_tutor_session_info(self, tutor_id, session_id):
        return session.query(User_Table.firstName, User_Table.lastName, TutorSession_Table.lead,
                             TutorSession_Table.timeIn, TutorSession_Table.timeOut)\
            .filter(TutorSession_Table.sessionId == session_id)\
            .filter(TutorSession_Table.tutorId == tutor_id)\
            .filter(User_Table.id == tutor_id).one()

    def get_student_session_info(self, student_id, session_id):
        return session.query(User_Table.id, User_Table.firstName, User_Table.lastName, StudentSession_Table.timeIn,
                             StudentSession_Table.timeOut) \
            .filter(StudentSession_Table.sessionId == session_id).filter(StudentSession_Table.studentId == student_id) \
            .filter(User_Table.id == student_id).one()

    def get_session_students(self, session_id):
        return session.query(User_Table.id, User_Table.firstName, User_Table.lastName, StudentSession_Table.timeIn, StudentSession_Table.timeOut,
                             StudentSession_Table.otherCourse, StudentSession_Table.otherCourseName) \
            .filter(StudentSession_Table.sessionId == session_id)\
            .filter(StudentSession_Table.studentId == User_Table.id).all()

    # The following two methods must return the same data for a logic check in one of the templates
    def get_student_session_courses(self, session_id, student_id):
        return session.query(Course_Table.dept, Course_Table.course_num, CourseCode_Table.courseName)\
            .filter(StudentSession_Table.sessionId == session_id)\
            .filter(StudentSession_Table.studentId == student_id)\
            .filter(StudentSession_Table.id == SessionCourses_Table.studentsession_id)\
            .filter(SessionCourses_Table.course_id == Course_Table.id)\
            .filter(CourseCode_Table.id == Course_Table.course_code_id).all()

    def get_session_courses(self, session_id):
        return session.query(Course_Table.dept, Course_Table.course_num, CourseCode_Table.courseName)\
            .filter(session_id == StudentSession_Table.sessionId)\
            .filter(StudentSession_Table.id == SessionCourses_Table.studentsession_id)\
            .filter(Course_Table.id == SessionCourses_Table.course_id)\
            .filter(CourseCode_Table.id == Course_Table.course_code_id).distinct()

    def get_other_course(self, session_id, student_id):
        return session.query(StudentSession_Table.otherCourse, StudentSession_Table.otherCourseName)\
            .filter(StudentSession_Table.sessionId == session_id)\
            .filter(StudentSession_Table.studentId == student_id).one()

    def get_sessions(self, course_id):
        return session.query(Session_Table, Schedule_Table).filter(Session_Table.schedule_id == Schedule_Table.id)\
            .filter(Session_Table.id == StudentSession_Table.sessionId)\
            .filter(StudentSession_Table.id == SessionCourses_Table.studentsession_id)\
            .filter(SessionCourses_Table.course_id == course_id)\
            .filter(Course_Table.id == course_id)\
            .all()

    def get_session_attendees(self, course_id, session_id):
        return session.query(StudentSession_Table, func.count(distinct(StudentSession_Table.id)))\
            .filter(StudentSession_Table.sessionId == session_id)\
            .filter(Session_Table.id == StudentSession_Table.sessionId)\
            .filter(SessionCourses_Table.studentsession_id == StudentSession_Table.id)\
            .filter(SessionCourses_Table.course_id == course_id).group_by(StudentSession_Table.id)\
            .all()

    def get_studentsession_from_session(self, session_id):
        return session.query(User_Table, StudentSession_Table).filter(User_Table.id == StudentSession_Table.studentId)\
            .filter(StudentSession_Table.sessionId == session_id)\
            .all()
