from datetime import datetime
from sqlalchemy import func, distinct

from sciencelabs.db_repository import session
from sciencelabs.db_repository.db_tables import Session_Table, Semester_Table, User_Table, TutorSession_Table,\
    Course_Table, SessionCourses_Table, StudentSession_Table, Schedule_Table, CourseCode_Table


class Session:

    def get_closed_sessions(self):
        return (session.query(Session_Table)
                .filter(Session_Table.semester_id == Semester_Table.id).filter(Semester_Table.active == 1)
                .filter(Session_Table.startTime != None).filter(Session_Table.deletedAt == None).all())

    def get_session(self, session_id):
        return session.query(Session_Table).filter(Session_Table.id == session_id).one()

    def get_session_tutors(self, session_id):
        return session.query(User_Table.id, User_Table.firstName, User_Table.lastName, TutorSession_Table.lead,
                             TutorSession_Table.timeIn, TutorSession_Table.timeOut, TutorSession_Table.schedTimeIn,
                             TutorSession_Table.schedTimeOut)\
            .filter(TutorSession_Table.sessionId == session_id).filter(User_Table.id == TutorSession_Table.tutorId)\
            .order_by(TutorSession_Table.lead.desc())

    def get_session_tutor_names(self, session_id):
        return session.query(User_Table.id, User_Table.firstName, User_Table.lastName)\
            .filter(TutorSession_Table.sessionId == session_id).filter(User_Table.id == TutorSession_Table.tutorId)\
            .order_by(TutorSession_Table.lead.desc())

    def get_tutor_session_info(self, tutor_id, session_id):
        return session.query(User_Table.firstName, User_Table.lastName, TutorSession_Table.lead,
                             TutorSession_Table.timeIn, TutorSession_Table.timeOut)\
            .filter(TutorSession_Table.sessionId == session_id)\
            .filter(TutorSession_Table.tutorId == tutor_id)\
            .filter(User_Table.id == tutor_id).one()

    def get_student_session_info(self, student_id, session_id):
        return session.query(User_Table.id, User_Table.firstName, User_Table.lastName, StudentSession_Table.timeIn,
                             StudentSession_Table.timeOut) \
            .filter(StudentSession_Table.sessionId == session_id).filter(StudentSession_Table.studentId == student_id) \
            .filter(User_Table.id == student_id).one()

    def get_session_students(self, session_id):
        return session.query(User_Table.id, User_Table.firstName, User_Table.lastName, StudentSession_Table.timeIn, StudentSession_Table.timeOut,
                             StudentSession_Table.otherCourse, StudentSession_Table.otherCourseName) \
            .filter(StudentSession_Table.sessionId == session_id)\
            .filter(StudentSession_Table.studentId == User_Table.id).all()

    # The following two methods must return the same data for a logic check in one of the templates
    def get_student_session_courses(self, session_id, student_id):
        return session.query(Course_Table.dept, Course_Table.course_num, CourseCode_Table.courseName)\
            .filter(StudentSession_Table.sessionId == session_id)\
            .filter(StudentSession_Table.studentId == student_id)\
            .filter(StudentSession_Table.id == SessionCourses_Table.studentsession_id)\
            .filter(SessionCourses_Table.course_id == Course_Table.id)\
            .filter(CourseCode_Table.id == Course_Table.course_code_id).all()

    # This method must return the same data as above
    def get_session_courses(self, session_id):
        return session.query(Course_Table.dept, Course_Table.course_num, CourseCode_Table.courseName)\
            .filter(session_id == StudentSession_Table.sessionId)\
            .filter(StudentSession_Table.id == SessionCourses_Table.studentsession_id)\
            .filter(Course_Table.id == SessionCourses_Table.course_id)\
            .filter(CourseCode_Table.id == Course_Table.course_code_id).distinct()

    def get_other_course(self, session_id, student_id):
        return session.query(StudentSession_Table.otherCourse, StudentSession_Table.otherCourseName)\
            .filter(StudentSession_Table.sessionId == session_id)\
            .filter(StudentSession_Table.studentId == student_id).one()

    def get_sessions(self, course_id):
        return session.query(Session_Table, Schedule_Table).filter(Session_Table.schedule_id == Schedule_Table.id)\
            .filter(Session_Table.id == StudentSession_Table.sessionId)\
            .filter(StudentSession_Table.id == SessionCourses_Table.studentsession_id)\
            .filter(SessionCourses_Table.course_id == course_id)\
            .filter(Course_Table.id == course_id)\
            .all()

    def get_session_attendees(self, course_id, session_id):
        return session.query(StudentSession_Table, func.count(distinct(StudentSession_Table.id)))\
            .filter(StudentSession_Table.sessionId == session_id)\
            .filter(Session_Table.id == StudentSession_Table.sessionId)\
            .filter(SessionCourses_Table.studentsession_id == StudentSession_Table.id)\
            .filter(SessionCourses_Table.course_id == course_id).group_by(StudentSession_Table.id)\
            .all()

    def get_studentsession_from_session(self, session_id):
        return session.query(User_Table, StudentSession_Table).filter(User_Table.id == StudentSession_Table.studentId)\
            .filter(StudentSession_Table.sessionId == session_id)\
            .all()

    def get_report_student_session_courses(self, session_id, student_id):
        return session.query(Course_Table.id, Course_Table.dept, Course_Table.course_num, CourseCode_Table.courseName,
                             Course_Table.title, Course_Table.section)\
            .filter(StudentSession_Table.sessionId == session_id)\
            .filter(StudentSession_Table.studentId == student_id)\
            .filter(StudentSession_Table.id == SessionCourses_Table.studentsession_id)\
            .filter(SessionCourses_Table.course_id == Course_Table.id)\
            .filter(CourseCode_Table.id == Course_Table.course_code_id).all()

    def get_dayofWeek_from_session(self, session_id):
        return session.query(Schedule_Table).filter(Session_Table.id == session_id)\
            .filter(Session_Table.schedule_id == Schedule_Table.id).one()

    def delete_session(self, session_id):
        session_to_delete = self.get_session(session_id)
        session_to_delete.deletedAt = datetime.now()
        session.commit()

    def add_anonymous_to_session(self, session_id, anon_students):
        session_to_edit = session.query(Session_Table).filter(Session_Table.id == session_id).one()
        session_to_edit.anonStudents = anon_students
        session.commit()

    def add_tutor_to_session(self, session_id, tutor_id, time_in, time_out, lead):
        # TODO: HELP
        db_time_in = datetime.strptime(time_in, '%H:%M')
        db_time_out = datetime.strptime(time_out, '%H:%M')
        new_tutor_session = TutorSession_Table(timeIn=db_time_in, timeOut=db_time_out, lead=lead, tutorId=tutor_id,
                                               sessionId=session_id)
        session.add(new_tutor_session)
        session.commit()

    def add_student_to_session(self, session_id, student_id):
        new_student_session = StudentSession_Table(studentId=student_id, sessionId=session_id)
        session.add(new_student_session)
        session.commit()

    def delete_student_from_session(self, student_id, session_id):
        student_session_to_delete = session.query(StudentSession_Table)\
            .filter(StudentSession_Table.studentId == student_id)\
            .filter(StudentSession_Table.sessionId == session_id).one()
        session.delete(student_session_to_delete)
        session.commit()

    def delete_tutor_from_session(self, tutor_id, session_id):
        tutor_session_to_delete = session.query(TutorSession_Table)\
            .filter(TutorSession_Table.tutorId == tutor_id)\
            .filter(TutorSession_Table.sessionId == session_id).one()
        session.delete(tutor_session_to_delete)
        session.commit()

    def edit_student_session(self, session_id, student_id, time_in, time_out, other_course):
        student_session_to_edit = session.query(StudentSession_Table)\
            .filter(StudentSession_Table.sessionId == session_id)\
            .filter(StudentSession_Table.studentId == student_id).one()
        student_session_to_edit.timeIn = time_in
        student_session_to_edit.timeOut = time_out
        if other_course:
            student_session_to_edit.otherCourse = 1
            student_session_to_edit.otherCourseName = other_course
        else:
            student_session_to_edit.otherCourse = 0
            student_session_to_edit.otherCourseName = None
        session.commit()

    def edit_student_courses(self, session_id, student_id, student_courses):
        student_session = session.query(StudentSession_Table).filter(StudentSession_Table.studentId == student_id)\
            .filter(StudentSession_Table.sessionId == session_id).one()
        session.query(SessionCourses_Table).filter(SessionCourses_Table.studentsession_id == student_session.studentsession_id).delete()
        for course in student_courses:
            new_student_course = SessionCourses_Table(studentsession_id=student_session.studentsession_id, course_id=course)
            session.add(new_student_course)
        session.commit()

