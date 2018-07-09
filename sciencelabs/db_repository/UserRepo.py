from sqlalchemy import *

from sciencelabs.db_repository import Base
from sciencelabs.db_repository import session
from sciencelabs.db_repository.user_roleRepo import user_role
from sciencelabs.db_repository.RoleRepo import Role
from sciencelabs.db_repository.StudentSessionRepo import StudentSession
from sciencelabs.db_repository.SessionRepo import Session
from sciencelabs.db_repository.SemesterRepo import Semester


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

    def get_report_student_info(self):
        return session.query(User.lastName, User.firstName, User.email).filter(User.id == StudentSession.studentId).filter(StudentSession.sessionId == Session.id).filter(Session.semester_id == Semester.id).filter(Semester.active == 1).all()

    def get_user_info(self):
        return session.query(User.lastName, User.firstName, User.email, Role.name).filter(User.id == user_role.user_id)\
            .filter(user_role.role_id == Role.id).all()
