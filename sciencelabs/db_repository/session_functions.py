from datetime import datetime
from sqlalchemy import func, distinct

from sciencelabs.db_repository import session
from sciencelabs.db_repository.db_tables import Session_Table, Semester_Table, User_Table, TutorSession_Table,\
    Course_Table, SessionCourses_Table, StudentSession_Table, Schedule_Table, CourseCode_Table, SessionCourseCodes_Table
from sciencelabs.sciencelabs_controller import ScienceLabsController


class Session:

    def __init__(self):
        self.base = ScienceLabsController()

    def get_closed_sessions(self):
        return (session.query(Session_Table)
                .filter(Session_Table.semester_id == Semester_Table.id).filter(Semester_Table.active == 1)
                .filter(Session_Table.startTime != None).filter(Session_Table.deletedAt == None)
                .order_by(Session_Table.date.asc()).all())

    def get_available_sessions(self, semester_id):
        return session.query(Session_Table).filter(Session_Table.semester_id == semester_id)\
            .filter(Session_Table.deletedAt == None).filter(Session_Table.startTime == None).all()

    def get_deleted_sessions(self, semester_id):
        return session.query(Session_Table).filter(Session_Table.semester_id == semester_id)\
            .filter(Session_Table.deletedAt != None).filter(Session_Table.startTime != None).all()

    def get_session(self, session_id):
        return session.query(Session_Table).filter(Session_Table.id == session_id).one()

    def get_session_tutors(self, session_id):
        return session.query(User_Table.id, User_Table.firstName, User_Table.lastName, TutorSession_Table.isLead,
                             TutorSession_Table.timeIn, TutorSession_Table.timeOut, TutorSession_Table.schedTimeIn,
                             TutorSession_Table.schedTimeOut)\
            .filter(TutorSession_Table.sessionId == session_id).filter(User_Table.id == TutorSession_Table.tutorId)\
            .order_by(TutorSession_Table.isLead.desc())

    def get_session_tutor_names(self, session_id):
        return session.query(User_Table.id, User_Table.firstName, User_Table.lastName)\
            .filter(TutorSession_Table.sessionId == session_id).filter(User_Table.id == TutorSession_Table.tutorId)\
            .order_by(TutorSession_Table.isLead.desc())

    def get_tutor_session_info(self, tutor_id, session_id):
        return session.query(User_Table.firstName, User_Table.lastName, TutorSession_Table.isLead,
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
        return session.query(User_Table.id, User_Table.firstName, User_Table.lastName, StudentSession_Table.timeIn,
                             StudentSession_Table.timeOut, StudentSession_Table.otherCourse,
                             StudentSession_Table.otherCourseName) \
            .filter(StudentSession_Table.sessionId == session_id)\
            .filter(StudentSession_Table.studentId == User_Table.id).all()

    # The following two methods must return the same data for a logic check in one of the templates
    def get_student_session_courses(self, session_id, student_id):
        return session.query(Course_Table.id, Course_Table.dept, Course_Table.course_num, CourseCode_Table.courseName)\
            .filter(StudentSession_Table.sessionId == session_id)\
            .filter(StudentSession_Table.studentId == student_id)\
            .filter(StudentSession_Table.id == SessionCourses_Table.studentsession_id)\
            .filter(SessionCourses_Table.course_id == Course_Table.id)\
            .filter(CourseCode_Table.id == Course_Table.course_code_id).all()

    # This method must return the same data as above
    def get_session_courses(self, session_id):
        return session.query(Course_Table.id, Course_Table.dept, Course_Table.course_num, CourseCode_Table.courseName)\
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

    def get_session_attendees(self, session_id):
        return session.query(User_Table.id) \
            .filter(StudentSession_Table.sessionId == session_id)\
            .filter(StudentSession_Table.studentId == User_Table.id).distinct()

    def get_session_attendees_with_dup(self, course_id, session_id):
        return session.query(StudentSession_Table, func.count(distinct(StudentSession_Table.id)))\
            .filter(StudentSession_Table.sessionId == session_id)\
            .filter(Session_Table.id == StudentSession_Table.sessionId)\
            .filter(SessionCourses_Table.studentsession_id == StudentSession_Table.id)\
            .filter(SessionCourses_Table.course_id == course_id).group_by(StudentSession_Table.id).all()

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
        new_tutor_session = TutorSession_Table(timeIn=time_in, timeOut=time_out, isLead=lead, tutorId=tutor_id,
                                               sessionId=session_id, substitutable=0)
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

    def edit_tutor_session(self, session_id, tutor_id, time_in, time_out, lead):
        tutor_session_to_edit = session.query(TutorSession_Table).filter(TutorSession_Table.sessionId == session_id)\
            .filter(TutorSession_Table.tutorId == tutor_id).one()
        tutor_session_to_edit.timeIn = time_in
        tutor_session_to_edit.timeOut = time_out
        tutor_session_to_edit.isLead = lead
        session.commit()

    def get_monthly_sessions(self, start_date, end_date):
        return (session.query(Session_Table)
                .filter(Session_Table.date.between(start_date, end_date))
                .filter(Session_Table.semester_id == Semester_Table.id)
                .filter(Session_Table.deletedAt == None)
                .filter(Session_Table.startTime != None).all())

    def get_avg_total_time_per_student(self):
        return session.query(StudentSession_Table) \
            .filter(StudentSession_Table.sessionId == Session_Table.id) \
            .filter(Session_Table.semester_id == Semester_Table.id) \
            .filter(Semester_Table.active == 1) \
            .filter(Schedule_Table.id == Session_Table.schedule_id)\
            .all()

    def get_schedule_monthly_attendance(self, schedule_id, start_date, end_date):
        return session.query(StudentSession_Table)\
            .filter(StudentSession_Table.sessionId == Session_Table.id)\
            .filter(Session_Table.schedule_id == Schedule_Table.id)\
            .filter(Schedule_Table.id == schedule_id)\
            .filter(Session_Table.date.between(start_date, end_date))

    def get_years(self):
        return session.query(Semester_Table.year).order_by(Semester_Table.year.desc()).distinct()

    def get_monthly_sessions_attendance(self, start_date, end_date):
        return (session.query(StudentSession_Table).filter(StudentSession_Table.sessionId == Session_Table.id)\
                .filter(Session_Table.date.between(start_date, end_date))
                .filter(Session_Table.semester_id == Semester_Table.id)
                .filter(Session_Table.startTime != None).all())

    def get_semester_closed_sessions(self, year, term):
        return (session.query(Session_Table)
                .filter(Session_Table.semester_id == Semester_Table.id)
                .filter(Semester_Table.year == year)
                .filter(Semester_Table.term == term)
                .filter(Session_Table.startTime != None).all())

    def get_unscheduled_sessions(self, year, term):
        return (session.query(Session_Table)
                .filter(Session_Table.deletedAt == None)
                .filter(Session_Table.schedule_id == None)
                .filter(Session_Table.semester_id == Semester_Table.id)
                .filter(Semester_Table.term == term)
                .filter(Semester_Table.year == year)
                .filter(Session_Table.startTime != None).all())

    ######################### EDIT STUDENT METHODS #########################

    def edit_student_session(self, session_id, student_id, time_in, time_out, other_course, student_courses):
        try:
            self.edit_student_session_info(session_id, student_id, time_in, time_out, other_course)
            self.edit_student_courses(session_id, student_id, student_courses)
            return True
        except:
            return False

    def edit_student_session_info(self, session_id, student_id, time_in, time_out, other_course):
        student_session_to_edit = session.query(StudentSession_Table) \
            .filter(StudentSession_Table.sessionId == session_id) \
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
        student_session = session.query(StudentSession_Table).filter(StudentSession_Table.studentId == student_id) \
            .filter(StudentSession_Table.sessionId == session_id).one()
        session.query(SessionCourses_Table).filter(
            SessionCourses_Table.studentsession_id == student_session.id).delete()
        for course in student_courses:
            new_student_course = SessionCourses_Table(studentsession_id=student_session.id, course_id=course)
            session.add(new_student_course)
        session.commit()

    ######################### CREATE SESSION METHODS #########################

    def create_new_session(self, semester_id, date, scheduled_start, scheduled_end, actual_start, actual_end, room,
                           comments, anon_students, name, leads, tutors, courses):
        try:
            new_session = self.create_session(semester_id, date, scheduled_start, scheduled_end, actual_start,
                                              actual_end, room, comments, anon_students, name)
            self.create_lead_sessions(scheduled_start, scheduled_end, leads, new_session.id)
            self.create_tutor_sessions(scheduled_start, scheduled_end, tutors, new_session.id)
            self.create_session_courses(new_session.id, courses)
            return True
        except:
            return False

    def create_session(self, semester_id, date, scheduled_start, scheduled_end, actual_start, actual_end, room,
                           comments, anon_students, name):
        new_session = Session_Table(semester_id=semester_id, date=date, schedStartTime=scheduled_start,
                                    schedEndTime=scheduled_end, startTime=actual_start, endTime=actual_end, room=room,
                                    open=0, comments=comments, anonStudents=anon_students, name=name,
                                    hash=self.base.get_hash())
        session.add(new_session)
        session.commit()
        return new_session

    def create_lead_sessions(self, scheduled_start, scheduled_end, leads, session_id):
        for lead in leads:
            new_tutor_session = TutorSession_Table(schedTimeIn=scheduled_start, schedTimeOut=scheduled_end, isLead=1,
                                                   tutorId=lead, sessionId=session_id, substitutable=0)
            session.add(new_tutor_session)
        session.commit()

    def create_tutor_sessions(self, scheduled_start, scheduled_end, tutors, session_id):
        for tutor in tutors:
            new_tutor_session = TutorSession_Table(schedTimeIn=scheduled_start, schedTimeOut=scheduled_end, isLead=0,
                                                   tutorId=tutor, sessionId=session_id, substitutable=0)
            session.add(new_tutor_session)
        session.commit()

    def create_session_courses(self, session_id, courses):
        for course in courses:
            new_session_course = SessionCourseCodes_Table(session_id=session_id, coursecode_id=course)
            session.add(new_session_course)
        session.commit()

    ########################################################################

    ######################### EDIT SESSION METHODS #########################

    def edit_session(self, session_id, semester_id, date, scheduled_start, scheduled_end, actual_start, actual_end,
                     room, comments, anon_students, name, leads, tutors, courses):
        try:
            self.edit_session_info(session_id, semester_id, date, scheduled_start, scheduled_end, actual_start,
                                   actual_end, room, comments, anon_students, name)
            self.edit_session_leads(scheduled_start, scheduled_end, leads, session_id)
            self.edit_session_tutors(scheduled_start, scheduled_end, tutors, session_id)
            self.edit_session_courses(session_id, courses)
            return True
        except:
            return False

    def edit_session_info(self, session_id, semester_id, date, scheduled_start, scheduled_end, actual_start, actual_end,
                     room, comments, anon_students, name):
        session_to_edit = session.query(Session_Table).filter(Session_Table.id == session_id).one()
        session_to_edit.semester_id = semester_id
        session_to_edit.date = date
        session_to_edit.schedStartTime = scheduled_start
        session_to_edit.schedEndTime = scheduled_end
        session_to_edit.startTime = actual_start
        session_to_edit.endTime = actual_end
        session_to_edit.room = room
        session_to_edit.comments = comments
        session_to_edit.anonStudents = anon_students
        session_to_edit.name = name
        session.commit()

    def edit_session_leads(self, scheduled_start, scheduled_end, leads, session_id):
        current_lead_ids = session.query(TutorSession_Table.tutorId).filter(TutorSession_Table.sessionId == session_id)\
            .filter(TutorSession_Table.isLead == 1).all()
        # Check to see if any current leads are still leads, and if not delete them
        for current_lead in current_lead_ids:
            if current_lead in leads:
                leads.remove(current_lead)  # Remove lead from list to add
            else:
                session.query(TutorSession_Table).filter(TutorSession_Table.sessionId == session_id)\
                    .filter(TutorSession_Table.tutorId == current_lead).delete()  # delete if not still lead
        session.commit()
        if leads:  # If there are still leads left we need to add them now
            self.create_lead_sessions(scheduled_start, scheduled_end, leads, session_id)

    def edit_session_tutors(self, scheduled_start, scheduled_end, tutors, session_id):
        current_tutor_ids = session.query(TutorSession_Table.tutorId).filter(TutorSession_Table.sessionId == session_id) \
            .filter(TutorSession_Table.isLead == 0).all()
        # Check to see if any current tutors are still tutors
        for current_tutor in current_tutor_ids:
            if current_tutor in tutors:
                tutors.remove(current_tutor)  # Remove tutor from list to add
            else:
                session.query(TutorSession_Table).filter(TutorSession_Table.sessionId == session_id) \
                    .filter(TutorSession_Table.tutorId == current_tutor).delete()  # delete if not still tutor
        session.commit()
        if tutors:  # If there are still tutors we need to add them now
            self.create_tutor_sessions(scheduled_start, scheduled_end, tutors, session_id)

    def edit_session_courses(self, session_id, courses):
        session.query(SessionCourseCodes_Table).filter(SessionCourseCodes_Table.session_id == session_id).delete()
        session.commit()
        self.create_session_courses(session_id, courses)

    ########################################################################

    def restore_deleted_session(self, session_id):
        session_to_restore = session.query(Session_Table).filter(Session_Table.id == session_id).one()
        session_to_restore.deletedAt = None
        session.commit()

    def start_open_session(self, session_id, opener_id):
        session_to_open = session.query(Session_Table).filter(Session_Table.id == session_id).one()
        session_to_open.open = 1
        session_to_open.startTime = datetime.now().strftime('%H:%M:%S')
        session_to_open.openerId = opener_id
        session.commit()

    def close_open_session(self, session_id, comments):
        session_to_close = session.query(Session_Table).filter(Session_Table.id == session_id).one()
        session_to_close.open = 0
        session_to_close.endTime = datetime.now().strftime('%H:%M:%S')
        session_to_close.comments = comments
        session.commit()

    def tutor_sign_out(self, session_id, tutor_id):
        tutor_session = session.query(TutorSession_Table).filter(TutorSession_Table.sessionId == session_id)\
            .filter(TutorSession_Table.tutorId == tutor_id).one()
        tutor_session.timeOut = datetime.now().strftime('%H:%M:%S')
        session.commit()

    def student_sign_in(self, session_id, student_id):
        new_student_session = StudentSession_Table(timeIn=datetime.now().strftime('%H:%M:%S'), studentId=student_id,
                                                   sessionId=session_id)  # TODO: course stuff
        session.add(new_student_session)
        session.commit()

    def student_sign_out(self, session_id, student_id):
        student_session = session.query(StudentSession_Table).filter(StudentSession_Table.sessionId == session_id)\
            .filter(StudentSession_Table.studentId == student_id).one()
        student_session.timeOut = datetime.now().strftime('%H:%M:%S')
        session.commit()