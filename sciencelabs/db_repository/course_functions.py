from sqlalchemy import *

from sciencelabs.db_repository import session
from sciencelabs.db_repository.db_tables import User_Table, Course_Table, CourseProfessors_Table, Semester_Table, \
    Session_Table, ScheduleCourseCodes_Table, SessionCourseCodes_Table, CourseCode_Table, SessionCourses_Table, \
    StudentSession_Table, Schedule_Table


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

    def get_semester_courses(self, semester_id):
        return session.query(Course_Table.dept, Course_Table.course_num, CourseCode_Table.courseName)\
            .filter(Course_Table.semester_id == semester_id)\
            .filter(Course_Table.course_code_id == CourseCode_Table.id).distinct()

    def get_student_courses(self, student_id, semester_id):
        return session.query(Course_Table.dept, Course_Table.course_num, CourseCode_Table.courseName)\
            .filter(CourseCode_Table.id == Course_Table.course_code_id)\
            .filter(Course_Table.id == SessionCourses_Table.course_id)\
            .filter(SessionCourses_Table.studentsession_id == StudentSession_Table.id)\
            .filter(StudentSession_Table.sessionId == Session_Table.id).filter(Session_Table.semester_id == semester_id) \
            .filter(StudentSession_Table.studentId == User_Table.id).filter(User_Table.id == student_id).distinct()

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

    def get_professor_courses(self, prof_id):
        return session.query(Course_Table)\
            .filter(CourseProfessors_Table.course_id == Course_Table.id)\
            .filter(CourseProfessors_Table.professor_id == prof_id) \
            .filter(Course_Table.semester_id == Semester_Table.id)\
            .filter(Semester_Table.active == 1)\
            .all()

    def get_semester_courses_with_section(self, semester_id):
        return session.query(Course_Table).filter(Course_Table.semester_id == semester_id).all()
