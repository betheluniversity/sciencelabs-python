from sqlalchemy import *

from sciencelabs.db_repository import Base
from sciencelabs.db_repository import session
from sciencelabs.db_repository.user_roleRepo import user_role
from sciencelabs.db_repository.RoleRepo import Role


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
        return session.query(User.lastName, User.firstName, User.email).all()

    def get_user_info(self):
        return session.query(User.lastName, User.firstName, User.email, Role.name).filter(User.id == user_role.user_id).filter(user_role.role_id == Role.id).all()


class UserFunctions:

    def get_report_student_info(self):
        # # TODO STILL NEED ATTENDANCE AND REPORT
        # student_list = conn.execute(select([user]))
        # students = []
        # for row in student_list:
        #     students.append([
        #         row[4],  # lastName
        #         row[3],  # firstName
        #         row[5],  # Email
        #         'attendance',
        #         'report'
        #     ])
        # return students
        students = []
        for row in User.get_report_student_info(self):
            students.append([
                row[0],
                row[1],
                row[2],
                'attendance',
                'report'
            ])
        return students

    def get_user_info(self):
        users = []
        for row in User.get_user_info(self):
            users.append([
                row[0],
                row[1],
                row[2],
                row[3],
                'edit',
                'check'
            ])
        return users