from sciencelabs.db_repository import session
from sciencelabs.db_repository.db_tables import Session_Table, Semester_Table, User_Table, TutorSession_Table, \
    StudentSession_Table, Course_Table, SessionCourses_Table


class Session:

    def get_closed_sessions(self):
        return (session.query(Session_Table.id, Session_Table.name, Session_Table.date, Session_Table.startTime, Session_Table.endTime, Session_Table.room)
                .filter(Session_Table.semester_id == Semester_Table.id).filter(Semester_Table.active == 1)
                .filter(Session_Table.startTime != None).all())

    def get_session(self, session_id):
        return session.query(Session_Table).filter(Session_Table.id == session_id).one()

    def get_session_tutors(self, session_id):
        return session.query(User_Table.id, User_Table.firstName, User_Table.lastName, TutorSession_Table.lead,
                             TutorSession_Table.timeIn, TutorSession_Table.timeOut)\
            .filter(TutorSession_Table.sessionId == session_id).filter(User_Table.id == TutorSession_Table.tutorId)\
            .order_by(TutorSession_Table.lead.desc())

    def get_tutor_session_info(self, tutor_id, session_id):
        return session.query(User_Table.firstName, User_Table.lastName, TutorSession_Table.lead, TutorSession_Table.timeIn, TutorSession_Table.timeOut)\
            .filter(TutorSession_Table.sessionId == session_id).filter(TutorSession_Table.tutorId == tutor_id)\
            .filter(User_Table.id == tutor_id).one()

    def get_student_session_info(self, student_id, session_id):
        return session.query(User_Table.firstName, User_Table.lastName, StudentSession_Table.timeIn,
                             StudentSession_Table.timeOut, Course_Table.title) \
            .filter(StudentSession_Table.sessionId == session_id).filter(StudentSession_Table.studentId == student_id) \
            .filter(User_Table.id == student_id).filter(StudentSession_Table.id == SessionCourses_Table.studentsession_id)\
            .filter(SessionCourses_Table.course_id == Course_Table.id).one()
