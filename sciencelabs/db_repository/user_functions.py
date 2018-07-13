from sqlalchemy import func, distinct

from sciencelabs.db_repository import session
from sciencelabs.db_repository.db_tables import User, StudentSession, Session, Semester, Role, user_role, Schedule


class UserFunctions:

    def get_report_student_info(self):
        return session.query(User.lastName, User.firstName, User.email).filter(User.id == StudentSession.studentId) \
            .filter(StudentSession.sessionId == Session.id).filter(Session.semester_id == Semester.id) \
            .filter(Semester.active == 1).all()

    def get_user_info(self):
        return session.query(User.lastName, User.firstName, User.email, Role.name).filter(User.id == user_role.user_id) \
            .filter(user_role.role_id == Role.id).all()

    def get_session_students(self, session_id):
        return session.query(User.firstName, User.lastName, StudentSession.timeIn, StudentSession.timeOut) \
            .filter(StudentSession.sessionId == session_id).filter(StudentSession.studentId == User.id).all()

    def get_student_info(self):
        return session.query(User, func.count(User.id)) \
            .filter(User.id == StudentSession.studentId) \
            .filter(StudentSession.sessionId == Session.id) \
            .filter(Session.semester_id == Semester.id) \
            .filter(Semester.active == 1) \
            .group_by(User.id) \
            .all()

    def get_user_info(self):
        return session.query(User, Role).filter(User.id == user_role.user_id) \
            .filter(User.id == user_role.user_id) \
            .filter(user_role.role_id == Role.id) \
            .all()

    def get_unique_session_attendance(self):
        return session.query(User, func.count(distinct(User.id))) \
            .filter(StudentSession.sessionId == Session.id) \
            .filter(Session.semester_id == Semester.id) \
            .filter(Semester.active == 1) \
            .filter(Schedule.id == Session.schedule_id) \
            .filter(StudentSession.studentId == User.id) \
            .group_by(User.id) \
            .all()
