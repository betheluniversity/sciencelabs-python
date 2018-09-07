from datetime import datetime
from sqlalchemy import func, distinct, orm

from sciencelabs.db_repository import session
from sciencelabs.db_repository.db_tables import User_Table, StudentSession_Table, Session_Table, Semester_Table, \
    Role_Table, user_role_Table, Schedule_Table, user_course_Table, Course_Table, CourseCode_Table, SessionCourseCodes_Table, CourseViewer_Table, SessionCourses_Table


class User:

    def get_session_students(self, session_id):
        return session.query(User_Table, StudentSession_Table) \
            .filter(StudentSession_Table.sessionId == session_id).filter(StudentSession_Table.studentId == User_Table.id).all()

    def get_student_info(self):
        return session.query(User_Table, func.count(User_Table.id)) \
            .filter(User_Table.id == StudentSession_Table.studentId) \
            .filter(StudentSession_Table.sessionId == Session_Table.id) \
            .filter(Session_Table.semester_id == Semester_Table.id) \
            .filter(Semester_Table.active == 1) \
            .group_by(User_Table.id).order_by(User_Table.lastName.asc()) \
            .all()

    def get_user_info(self):
        return session.query(User_Table, Role_Table).filter(User_Table.id == user_role_Table.user_id) \
            .filter(User_Table.id == user_role_Table.user_id) \
            .filter(user_role_Table.role_id == Role_Table.id) \
            .filter(User_Table.deletedAt == None) \
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

    def get_studentsession(self, student_id):
        return session.query(StudentSession_Table, Session_Table)\
            .filter(StudentSession_Table.studentId == student_id)\
            .filter(StudentSession_Table.sessionId == Session_Table.id)\
            .filter(Session_Table.semester_id == Semester_Table.id)\
            .filter(Semester_Table.active == 1)\
            .all()

    def get_user(self, user_id):
        return session.query(User_Table).filter(User_Table.id == user_id).one()

    def get_student_attendance(self, student_id):
            return session.query(User_Table, func.count(User_Table.id)) \
                .filter(student_id == User_Table.id)\
                .filter(User_Table.id == StudentSession_Table.studentId) \
                .filter(StudentSession_Table.sessionId == Session_Table.id) \
                .filter(Session_Table.semester_id == Semester_Table.id) \
                .filter(Semester_Table.active == 1) \
                .group_by(User_Table.id) \
                .one()

    def get_student_courses(self, student_id):
        return session.query(Course_Table)\
            .filter(student_id == user_course_Table.user_id)\
            .filter(user_course_Table.course_id == Course_Table.id)\
            .filter(Course_Table.semester_id == Semester_Table.id)\
            .filter(Semester_Table.active == 1)\
            .all()

    def get_students_in_course(self, course_id):
        return session.query(User_Table, func.count(User_Table.id))\
            .filter(Course_Table.id == course_id)\
            .filter(SessionCourses_Table.course_id == course_id)\
            .filter(SessionCourses_Table.studentsession_id == StudentSession_Table.id)\
            .filter(StudentSession_Table.studentId == User_Table.id)\
            .group_by(User_Table.id)\
            .all()

    def get_average_time_in_course(self, student_id, course_id):
        return session.query(StudentSession_Table, User_Table) \
            .filter(Course_Table.id == course_id) \
            .filter(SessionCourses_Table.course_id == course_id) \
            .filter(SessionCourses_Table.studentsession_id == StudentSession_Table.id) \
            .filter(StudentSession_Table.studentId == User_Table.id) \
            .filter(User_Table.id == student_id) \
            .all()

    def get_student_from_studentsession(self, student_id):
        return session.query(User_Table).fitler(User_Table.id == student_id)

    def get_all_roles(self):
        return session.query(Role_Table).all()

    def get_user_roles(self, user_id):
        return session.query(Role_Table)\
            .filter(Role_Table.id == user_role_Table.role_id)\
            .filter(user_role_Table.user_id == User_Table.id)\
            .filter(User_Table.id == user_id)\
            .all()

    def get_professor_role(self):
        return session.query(Role_Table).filter(Role_Table.name == "Professor").one()

    def get_all_current_users(self):
        return session.query(User_Table).filter(User_Table.deletedAt == None).all()

    def delete_user(self, user_id):
        user_to_delete = self.get_user(user_id)
        user_to_delete.deletedAt = datetime.now()
        session.commit()

    def check_for_existing_user(self, username):
        try:  # return true if there is an existing user
            user = session.query(User_Table).filter(User_Table.username == username).one()
            return True
        except orm.exc.NoResultFound:  # otherwise return false
            return False

    def activate_existing_user(self, username):
        user = session.query(User_Table).filter(User_Table.username == username).one()
        user.deletedAt = None
        session.commit()

    def create_user(self, first_name, last_name, username):
        new_user = User_Table(username=username, password=None, firstName=first_name, lastName=last_name,
                              email=username+'@bethel.edu', send_email=0, deletedAt=None)
        session.add(new_user)
        session.commit()

    def set_user_roles(self, username, roles):
        user = session.query(User_Table).filter(User_Table.username == username).one()
        user_id = user.id
        for role in roles:
            user_role = user_role_Table(user_id=user_id, role_id=role)
            session.add(user_role)
        session.commit()

    def update_user_info(self, user_id, first_name, last_name, email):
        user = session.query(User_Table).filter(User_Table.id == user_id).one()
        user.firstName = first_name
        user.lastName = last_name
        user.email = email
        session.commit()

    def clear_current_roles(self, user_id):
        roles = session.query(user_role_Table).filter(user_role_Table.user_id == user_id).all()
        for role in roles:
            session.delete(role)
        session.commit()

    def get_user_by_username(self, username):
        return session.query(User_Table).filter(User_Table.username == username).one()

    def edit_user(self, first_name,last_name, username, email_pref):
        user_to_edit = self.get_user_by_username(username)
        user_to_edit.firstName = first_name
        user_to_edit.lastName = last_name
        user_to_edit.send_email = email_pref
        session.commit()


