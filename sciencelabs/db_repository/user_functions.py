from sqlalchemy import func, distinct

from sciencelabs.db_repository import session
from sciencelabs.db_repository.db_tables import User_Table, StudentSession_Table, Session_Table, Semester_Table, \
    Role_Table, user_role_Table, Schedule_Table


class User:

    def get_report_student_info(self):
        return session.query(User_Table.lastName, User_Table.firstName, User_Table.email).filter(User_Table.id == StudentSession_Table.studentId) \
            .filter(StudentSession_Table.sessionId == Session_Table.id).filter(Session_Table.semester_id == Semester_Table.id) \
            .filter(Semester_Table.active == 1).all()

    def get_user_info(self):
        return session.query(User_Table.lastName, User_Table.firstName, User_Table.email, Role_Table.name).filter(User_Table.id == user_role_Table.user_id) \
            .filter(user_role_Table.role_id == Role_Table.id).all()

    def get_session_students(self, session_id):
        return session.query(User_Table.id, User_Table.firstName, User_Table.lastName, StudentSession_Table.timeIn, StudentSession_Table.timeOut) \
            .filter(StudentSession_Table.sessionId == session_id).filter(StudentSession_Table.studentId == User_Table.id).all()

    def get_student_info(self):
        return session.query(User_Table, func.count(User_Table.id)) \
            .filter(User_Table.id == StudentSession_Table.studentId) \
            .filter(StudentSession_Table.sessionId == Session_Table.id) \
            .filter(Session_Table.semester_id == Semester_Table.id) \
            .filter(Semester_Table.active == 1) \
            .group_by(User_Table.id) \
            .all()

    def get_user_info(self):
        return session.query(User_Table, Role_Table).filter(User_Table.id == user_role_Table.user_id) \
            .filter(User_Table.id == user_role_Table.user_id) \
            .filter(user_role_Table.role_id == Role_Table.id) \
            .all()

    def get_unique_session_attendance(self):
        return session.query(User_Table, func.count(distinct(User_Table.id))) \
            .filter(StudentSession_Table.sessionId == Session_Table.id) \
            .filter(Session_Table.semester_id == Semester_Table.id) \
            .filter(Semester_Table.active == 1) \
            .filter(Schedule_Table.id == Session_Table.schedule_id) \
            .filter(StudentSession_Table.studentId == User_Table.id) \
            .group_by(User_Table.id) \
            .all()
