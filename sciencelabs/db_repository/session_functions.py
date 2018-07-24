from sqlalchemy import func, distinct

from sciencelabs.db_repository import session
from sciencelabs.db_repository.db_tables import Session_Table, Semester_Table, User_Table, TutorSession_Table,\
    Course_Table, SessionCourses_Table, StudentSession_Table, Schedule_Table


class Session:

    def get_closed_sessions(self):
        return (session.query(Session_Table)
                .filter(Session_Table.semester_id == Semester_Table.id).filter(Semester_Table.active == 1)
                .filter(Session_Table.startTime != None).all())

    def get_session(self, session_id):
        return session.query(Session_Table).filter(Session_Table.id == session_id).one()

    def get_session_tutors(self, session_id):
        tutors = session.query(User_Table.id, User_Table.firstName, User_Table.lastName, TutorSession_Table.lead,
                               TutorSession_Table.timeIn, TutorSession_Table.timeOut, TutorSession_Table.schedTimeIn, TutorSession_Table.schedTimeOut)\
            .filter(TutorSession_Table.sessionId == session_id)\
            .filter(User_Table.id == TutorSession_Table.tutorId)
        session_leads = []
        session_tutors = []
        for tutor in tutors:
            if tutor.lead == 1:
                session_leads.append(tutor)
            else:
                session_tutors.append(tutor)
        return session_leads, session_tutors

    def get_tutor_session_info(self, tutor_id, session_id):
        return session.query(User_Table.firstName, User_Table.lastName, TutorSession_Table.lead,
                             TutorSession_Table.timeIn, TutorSession_Table.timeOut)\
            .filter(TutorSession_Table.sessionId == session_id)\
            .filter(TutorSession_Table.tutorId == tutor_id)\
            .filter(User_Table.id == tutor_id).one()

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
        return session.query(User_Table, StudentSession_Table).filter(User_Table.id == StudentSession_Table.studentId).filter(StudentSession_Table.sessionId == session_id).all()

    def get_student_session_courses(self, student_id, session_id):
        return session.query(Course_Table).filter(Course_Table.id == SessionCourses_Table.course_id).filter(SessionCourses_Table.studentsession_id == StudentSession_Table.id).filter(StudentSession_Table.studentId == student_id).filter(StudentSession_Table.sessionId == session_id).all()