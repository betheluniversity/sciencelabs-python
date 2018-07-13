from sciencelabs.db_repository import session
from sciencelabs.db_repository.db_tables import User, Course, CourseProfessors, Semester


class CourseFunctions:

    def get_course_info(self):
        return (session.query(Course, User).filter(Course.num_attendees)
                .filter(User.id == CourseProfessors.professor_id).filter(CourseProfessors.course_id == Course.id)
                .filter(Course.semester_id == Semester.id).filter(Semester.active == 1).all())

    def get_active_course_info(self):
        return (session.query(Course.dept, Course.course_num, Course.title, Course.section, User.firstName, User.lastName)
                .filter(User.id == CourseProfessors.professor_id)
                .filter(CourseProfessors.course_id == Course.id)
                .filter(Course.semester_id == Semester.id)
                .filter(Semester.active == 1)
                .all())
