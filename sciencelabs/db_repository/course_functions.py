from sqlalchemy import *

from sciencelabs.db_repository import session
from sciencelabs.db_repository.db_tables import User_Table, Course_Table, CourseProfessors_Table, Semester_Table, Session_Table, ScheduleCourseCodes_Table, SessionCourseCodes_Table, CourseCode_Table, SessionCourses_Table, StudentSession_Table, Schedule_Table


class Course:

    def get_course_info(self):
        return (session.query(Course_Table, User_Table).filter(Course_Table.num_attendees)
                .filter(User_Table.id == CourseProfessors_Table.professor_id)
                .filter(CourseProfessors_Table.course_id == Course_Table.id)
                .filter(Course_Table.semester_id == Semester_Table.id)
                .filter(Semester_Table.active == 1)
                .all())

    def get_active_course_info(self):
        return (session.query(Course_Table, User_Table)
                .filter(User_Table.id == CourseProfessors_Table.professor_id)
                .filter(CourseProfessors_Table.course_id == Course_Table.id)
                .filter(Course_Table.semester_id == Semester_Table.id)
                .filter(Semester_Table.active == 1)
                .all())

    def get_course(self, course_id):
        return session.query(Course_Table, User_Table, Semester_Table)\
            .filter(Course_Table.id == course_id)\
            .filter(CourseProfessors_Table.course_id == course_id)\
            .filter(CourseProfessors_Table.professor_id == User_Table.id)\
            .filter(Course_Table.semester_id == Semester_Table.id)\
            .one()

    def get_courses_for_session(self, session_id):
        return session.query(Course_Table)\
            .filter(Course_Table.id == SessionCourses_Table.course_id)\
            .filter(SessionCourses_Table.studentsession_id == StudentSession_Table.id)\
            .filter(StudentSession_Table.sessionId == session_id)\
            .all()
