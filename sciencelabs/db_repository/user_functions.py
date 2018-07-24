from sqlalchemy import func, distinct

from sciencelabs.db_repository import session
from sciencelabs.db_repository.db_tables import User_Table, StudentSession_Table, Session_Table, Semester_Table, \
    Role_Table, user_role_Table, Schedule_Table, user_course_Table, Course_Table, CourseCode_Table, SessionCourseCodes_Table, CourseViewer_Table, SessionCourses_Table


class User:

    def get_user_info(self):
        return session.query(User_Table, Role_Table).filter(User_Table.id == user_role_Table.user_id) \
            .filter(user_role_Table.role_id == Role_Table.id).all()

    def get_session_students(self, session_id):
        return session.query(User_Table, StudentSession_Table) \
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

    def get_studentsession(self, student_id):
        return session.query(StudentSession_Table, Session_Table)\
            .filter(StudentSession_Table.studentId == student_id)\
            .filter(StudentSession_Table.sessionId == Session_Table.id)\
            .filter(Session_Table.semester_id == Semester_Table.id)\
            .filter(Semester_Table.active == 1)\
            .all()

    def get_user(self, user_id):
        return session.query(User_Table).filter(User_Table.id == user_id).one()

    # TODO FIGURE OUT HOW TO USE THIS TO GET ATTENDANCE FOR SPECIFIC COURSE
    def get_student_attendance(self, student_id, course_id):
        if not course_id:
            return session.query(User_Table, func.count(User_Table.id)) \
                .filter(student_id == User_Table.id)\
                .filter(User_Table.id == StudentSession_Table.studentId) \
                .filter(StudentSession_Table.sessionId == Session_Table.id) \
                .filter(Session_Table.semester_id == Semester_Table.id) \
                .filter(Semester_Table.active == 1) \
                .group_by(User_Table.id) \
                .one()
        else:
            print(course_id)
            return session.query(StudentSession_Table)\
                .filter(StudentSession_Table.sessionId == Session_Table.id)\
                .filter(Session_Table.semester_id == Semester_Table.id)\
                .filter(Semester_Table.active == 1)\
                .filter(SessionCourses_Table.studentsession_id == StudentSession_Table.id)\
                .filter(SessionCourses_Table.course_id == CourseViewer_Table.course_id)\
                .all()

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