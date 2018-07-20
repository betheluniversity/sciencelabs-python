from sciencelabs.db_repository import session
from sciencelabs.db_repository.db_tables import User_Table, Course_Table, CourseProfessors_Table, Semester_Table, CourseCode_Table


class Course:

    def get_course_info(self):
        return (session.query(Course_Table, User_Table).filter(Course_Table.num_attendees)
                .filter(User_Table.id == CourseProfessors_Table.professor_id).filter(CourseProfessors_Table.course_id == Course_Table.id)
                .filter(Course_Table.semester_id == Semester_Table.id).filter(Semester_Table.active == 1).all())

    def get_active_course_info(self):
        return (session.query(Course_Table.dept, Course_Table.course_num, Course_Table.title, Course_Table.section, User_Table.firstName, User_Table.lastName)
                .filter(User_Table.id == CourseProfessors_Table.professor_id)
                .filter(CourseProfessors_Table.course_id == Course_Table.id)
                .filter(Course_Table.semester_id == Semester_Table.id)
                .filter(Semester_Table.active == 1)
                .all())

    def get_semester_courses(self, semester_id):
        return session.query(Course_Table.dept, Course_Table.course_num, CourseCode_Table.courseName)\
            .filter(Course_Table.semester_id == semester_id)\
            .filter(Course_Table.course_code_id == CourseCode_Table.id).distinct()
