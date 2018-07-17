from sciencelabs.db_repository import session
from sciencelabs.db_repository.db_tables import User_Table, Course_Table, CourseProfessors_Table, Semester_Table


class Course:

    def get_course_info(self):
        return (session.query(Course_Table, User_Table).filter(Course_Table.num_attendees)
                .filter(User_Table.id == CourseProfessors_Table.professor_id).filter(CourseProfessors_Table.course_id == Course_Table.id)
                .filter(Course_Table.semester_id == Semester_Table.id).filter(Semester_Table.active == 1).all())

    def get_active_course_info(self):
        return (session.query(Course_Table, User_Table)
                .filter(User_Table.id == CourseProfessors_Table.professor_id)
                .filter(CourseProfessors_Table.course_id == Course_Table.id)
                .filter(Course_Table.semester_id == Semester_Table.id)
                .filter(Semester_Table.active == 1)
                .all())

    def get_course(self, course_id):
        return session.query(Course_Table, User_Table).filter(Course_Table.id == course_id).filter(CourseProfessors_Table.course_id == course_id).filter(CourseProfessors_Table.professor_id == User_Table.id).one()
