from datetime import datetime, timedelta
from sqlalchemy import func, distinct

from sciencelabs.db_repository import db_session
from sciencelabs.db_repository.db_tables import Session_Table, Semester_Table, User_Table, TutorSession_Table,\
    Course_Table, SessionCourses_Table, StudentSession_Table, Schedule_Table, CourseCode_Table, \
    SessionCourseCodes_Table
from sciencelabs.sciencelabs_controller import ScienceLabsController
from sciencelabs import app


class Session:
    def __init__(self):
        self.base = ScienceLabsController()

    def get_closed_sessions(self, semester_id):
        return db_session.query(Session_Table)\
                .filter(Session_Table.semester_id == Semester_Table.id)\
                .filter(Semester_Table.id == semester_id)\
                .filter(Session_Table.startTime)\
                .filter(Session_Table.deletedAt == None)\
                .filter(Session_Table.date)\
                .order_by(Session_Table.date.asc())\
                .all()

    def get_available_sessions(self, semester_id):
        return db_session.query(Session_Table).filter(Session_Table.semester_id == semester_id)\
            .filter(Session_Table.deletedAt == None).filter(Session_Table.startTime == None).all()

    # This gets all session that have been 'soft deleted'
    def get_deleted_sessions(self, semester_id):
        return db_session.query(Session_Table) \
            .filter(Session_Table.semester_id == semester_id) \
            .filter(Session_Table.startTime).filter(Session_Table.endTime) \
            .filter(Session_Table.deletedAt != None) \
            .order_by(Session_Table.date) \
            .all()

    def get_session(self, session_id):
        return db_session.query(Session_Table)\
            .filter(Session_Table.id == session_id)\
            .first()

    def get_open_sessions(self):
        return db_session.query(Session_Table).filter(Session_Table.open == 1).all()

    def get_session_tutors(self, session_id):
        return db_session.query(User_Table.id, User_Table.firstName, User_Table.lastName, TutorSession_Table.isLead,
                                TutorSession_Table.timeIn, TutorSession_Table.timeOut, TutorSession_Table.schedTimeIn,
                                TutorSession_Table.schedTimeOut)\
            .filter(TutorSession_Table.sessionId == session_id)\
            .filter(User_Table.id == TutorSession_Table.tutorId)\
            .order_by(TutorSession_Table.isLead.desc())

    def get_tutor_sessions(self, session_id):
        return db_session.query(TutorSession_Table).filter(TutorSession_Table.sessionId == session_id).all()

    def get_session_lead_ids(self, session_id):
        lead_ids = []
        leads = db_session.query(User_Table).filter(TutorSession_Table.sessionId == session_id)\
            .filter(TutorSession_Table.isLead == 1).filter(TutorSession_Table.tutorId == User_Table.id).all()
        for lead in leads:
            lead_ids.append(lead.id)
        return lead_ids

    def get_session_tutor_ids(self, session_id):
        tutor_ids = []
        tutors = db_session.query(User_Table).filter(TutorSession_Table.sessionId == session_id)\
            .filter(TutorSession_Table.isLead == 0).filter(TutorSession_Table.tutorId == User_Table.id).all()
        for tutor in tutors:
            tutor_ids.append(tutor.id)
        return tutor_ids

    def get_tutor_session_info(self, tutor_session_id):
        return db_session.query(User_Table.firstName, User_Table.lastName, TutorSession_Table.isLead,
                                TutorSession_Table.timeIn, TutorSession_Table.timeOut, TutorSession_Table.sessionId)\
            .filter(TutorSession_Table.id == tutor_session_id)\
            .filter(TutorSession_Table.tutorId == User_Table.id)\
            .one()

    def get_student_session_info(self, student_session_id):
        return db_session.query(User_Table.id, User_Table.firstName, User_Table.lastName, StudentSession_Table.timeIn,
                             StudentSession_Table.timeOut, StudentSession_Table.sessionId) \
            .filter(StudentSession_Table.id == student_session_id)\
            .filter(StudentSession_Table.studentId == User_Table.id) \
            .one()

    def get_session_students(self, session_id):
        return db_session.query(User_Table.id, User_Table.firstName, User_Table.lastName, StudentSession_Table.timeIn,
                             StudentSession_Table.timeOut, StudentSession_Table.otherCourse,
                             StudentSession_Table.otherCourseName) \
            .filter(StudentSession_Table.sessionId == session_id)\
            .filter(StudentSession_Table.studentId == User_Table.id)\
            .all()

    def get_student_sessions(self, session_id):
        return db_session.query(StudentSession_Table).filter(StudentSession_Table.sessionId == session_id).all()

    def get_number_of_student_sessions(self, session_id):
        return db_session.query(func.count(StudentSession_Table.sessionId))\
            .filter(StudentSession_Table.sessionId == Session_Table.id)\
            .filter(Session_Table.id == session_id)\
            .group_by(StudentSession_Table.studentId)\
            .all()

    def get_studentsession_courses(self, student_session_id):
        return db_session.query(Course_Table.id, Course_Table.dept, Course_Table.course_num,
                                Course_Table.course_code_id, CourseCode_Table.courseName)\
            .filter(StudentSession_Table.id == student_session_id)\
            .filter(StudentSession_Table.id == SessionCourses_Table.studentsession_id)\
            .filter(SessionCourses_Table.course_id == Course_Table.id)\
            .filter(CourseCode_Table.id == Course_Table.course_code_id)\
            .all()

    # The following two methods must return the same data for a logic check in one of the templates
    def get_student_session_courses(self, session_id, student_id):
        return db_session.query(Course_Table.id, Course_Table.dept, Course_Table.course_num,
                                Course_Table.course_code_id, CourseCode_Table.courseName)\
            .filter(StudentSession_Table.sessionId == session_id)\
            .filter(StudentSession_Table.studentId == student_id)\
            .filter(StudentSession_Table.id == SessionCourses_Table.studentsession_id)\
            .filter(SessionCourses_Table.course_id == Course_Table.id)\
            .filter(CourseCode_Table.id == Course_Table.course_code_id)\
            .all()

    # This method must return the same data as above
    def get_session_courses(self, session_id):
        return db_session.query(Course_Table.id, Course_Table.dept, Course_Table.course_num,
                                Course_Table.course_code_id, CourseCode_Table.courseName)\
            .filter(session_id == StudentSession_Table.sessionId)\
            .filter(StudentSession_Table.id == SessionCourses_Table.studentsession_id)\
            .filter(Course_Table.id == SessionCourses_Table.course_id)\
            .filter(CourseCode_Table.id == Course_Table.course_code_id)\
            .distinct()

    def get_session_course_codes(self, session_id):
        return db_session.query(CourseCode_Table).filter(SessionCourseCodes_Table.session_id == session_id)\
            .filter(SessionCourseCodes_Table.coursecode_id == CourseCode_Table.id).all()

    def get_sess_courses(self, session_id, semester_id):
        course_codes = self.get_session_course_codes(session_id)
        courses = []
        for course_code in course_codes:
            courses.append(db_session.query(Course_Table)
                           .filter(Course_Table.course_code_id == course_code.id)
                           .filter(Course_Table.semester_id == semester_id)
                           .first())

        return courses

    def get_student_session_course_ids(self, session_id, student_id):
        course_ids = []
        courses = self.get_student_session_courses(session_id, student_id)
        for course in courses:
            course_code = db_session.query(CourseCode_Table).filter(CourseCode_Table.courseName == course.courseName)\
                .filter(CourseCode_Table.id == course.course_code_id).one()
            course_ids.append(course_code.id)
        return course_ids

    def get_course_code_attendance(self, session_id, course_id):
        return db_session.query(User_Table).filter(StudentSession_Table.sessionId == session_id)\
            .filter(SessionCourses_Table.studentsession_id == StudentSession_Table.id)\
            .filter(SessionCourses_Table.course_id == Course_Table.id)\
            .filter(Course_Table.course_code_id == course_id).all()

    def get_course_email_info(self, course_id):
        return db_session.query(Course_Table.title, Course_Table.section)\
            .filter(Course_Table.id == course_id)\
            .all()

    def get_other_course(self, student_session_id):
        return db_session.query(StudentSession_Table.otherCourse, StudentSession_Table.otherCourseName)\
            .filter(StudentSession_Table.id == student_session_id)\
            .one()

    def get_sessions(self, course_id):
        return db_session.query(Session_Table)\
            .filter(Session_Table.id == StudentSession_Table.sessionId)\
            .filter(StudentSession_Table.id == SessionCourses_Table.studentsession_id)\
            .filter(SessionCourses_Table.course_id == course_id)\
            .filter(Course_Table.id == course_id)\
            .all()

    def get_course_session(self, course_id, session_id):
        return db_session.query(Session_Table, Schedule_Table)\
            .filter(Session_Table.schedule_id == Schedule_Table.id)\
            .filter(Session_Table.id == StudentSession_Table.sessionId)\
            .filter(StudentSession_Table.id == SessionCourses_Table.studentsession_id)\
            .filter(SessionCourses_Table.course_id == course_id)\
            .filter(Course_Table.id == course_id)\
            .filter(Session_Table.id == session_id) \
            .all()

    def get_session_attendees(self, session_id):
        return db_session.query(User_Table.id) \
            .filter(StudentSession_Table.sessionId == session_id)\
            .filter(StudentSession_Table.studentId == User_Table.id)\
            .distinct()

    def get_session_attendees_with_dup(self, course_id, session_id):
        return db_session.query(StudentSession_Table, func.count(distinct(StudentSession_Table.id)))\
            .filter(StudentSession_Table.sessionId == session_id)\
            .filter(Session_Table.id == StudentSession_Table.sessionId)\
            .filter(SessionCourses_Table.studentsession_id == StudentSession_Table.id)\
            .filter(SessionCourses_Table.course_id == course_id)\
            .group_by(StudentSession_Table.id)\
            .all()

    def get_student_sessions_for_course(self, course_id, session_id):
        return db_session.query(StudentSession_Table)\
            .filter(StudentSession_Table.sessionId == session_id)\
            .filter(Session_Table.id == StudentSession_Table.sessionId)\
            .filter(SessionCourses_Table.studentsession_id == StudentSession_Table.id)\
            .filter(SessionCourses_Table.course_id == course_id)\
            .all()

    def get_session_course_students(self, session_id, course_id):
        return db_session.query(User_Table).filter(User_Table.id == StudentSession_Table.studentId)\
            .filter(StudentSession_Table.id == SessionCourses_Table.studentsession_id)\
            .filter(SessionCourses_Table.course_id == course_id)\
            .filter(StudentSession_Table.sessionId == session_id)\
            .all()

    def get_prof_session_students(self, session_id, prof_course_ids):
        prof_students = []
        for course_id in prof_course_ids:
            course_students = db_session.query(User_Table.id, User_Table.firstName, User_Table.lastName,
                                               StudentSession_Table.timeIn, StudentSession_Table.timeOut,
                                               StudentSession_Table.otherCourse, StudentSession_Table.otherCourseName)\
                .filter(User_Table.id == StudentSession_Table.studentId)\
                .filter(StudentSession_Table.sessionId == session_id)\
                .filter(StudentSession_Table.id == SessionCourses_Table.studentsession_id)\
                .filter(SessionCourses_Table.course_id == course_id)\
                .all()
            for student in course_students:
                prof_students.append(student)
        return prof_students

    def get_studentsession_from_session(self, session_id):
        return db_session.query(User_Table, StudentSession_Table)\
            .filter(User_Table.id == StudentSession_Table.studentId)\
            .filter(StudentSession_Table.sessionId == session_id)\
            .all()

    def get_report_student_session_courses(self, session_id, student_id):
        return db_session.query(Course_Table.id, Course_Table.dept, Course_Table.course_num, CourseCode_Table.courseName,
                             Course_Table.title, Course_Table.section)\
            .filter(StudentSession_Table.sessionId == session_id)\
            .filter(StudentSession_Table.studentId == student_id)\
            .filter(StudentSession_Table.id == SessionCourses_Table.studentsession_id)\
            .filter(SessionCourses_Table.course_id == Course_Table.id)\
            .filter(CourseCode_Table.id == Course_Table.course_code_id)\
            .all()

    def get_dayofWeek_from_session(self, session_id):
        return db_session.query(Schedule_Table)\
            .filter(Session_Table.id == session_id)\
            .filter(Session_Table.schedule_id == Schedule_Table.id)\
            .first()

    def delete_session(self, session_id):
        session_to_delete = self.get_session(session_id)
        session_to_delete.deletedAt = datetime.now()
        db_session.commit()

    def add_anonymous_to_session(self, session_id, anon_students):
        session_to_edit = db_session.query(Session_Table)\
            .filter(Session_Table.id == session_id)\
            .one()
        session_to_edit.anonStudents = anon_students
        db_session.commit()

    def add_tutor_to_session(self, session_id, tutor_id, time_in, time_out, lead):
        new_tutor_session = TutorSession_Table(timeIn=time_in, timeOut=time_out, isLead=lead, tutorId=tutor_id,
                                               sessionId=session_id, substitutable=0)
        db_session.add(new_tutor_session)
        db_session.commit()

    def add_student_to_session(self, session_id, student_id):
        new_student_session = StudentSession_Table(studentId=student_id, sessionId=session_id)
        db_session.add(new_student_session)
        db_session.commit()

    def delete_student_from_session(self, student_session_id):
        student_session_to_delete = db_session.query(StudentSession_Table)\
            .filter(StudentSession_Table.id == student_session_id)\
            .one()
        db_session.delete(student_session_to_delete)
        db_session.commit()

    def delete_tutor_from_session(self, tutor_session_id):
        tutor_session_to_delete = db_session.query(TutorSession_Table)\
            .filter(TutorSession_Table.id == tutor_session_id)\
            .one()
        db_session.delete(tutor_session_to_delete)
        db_session.commit()

    def edit_tutor_session(self, tutor_session_id, time_in, time_out, lead):
        tutor_session_to_edit = db_session.query(TutorSession_Table)\
            .filter(TutorSession_Table.id == tutor_session_id)\
            .one()
        tutor_session_to_edit.timeIn = time_in
        tutor_session_to_edit.timeOut = time_out
        tutor_session_to_edit.isLead = lead
        db_session.commit()

    def get_monthly_sessions(self, start_date, end_date):
        return (db_session.query(Session_Table)
                .filter(Session_Table.date.between(start_date, end_date))
                .filter(Session_Table.semester_id == Semester_Table.id)
                .filter(Session_Table.deletedAt == None)
                .filter(Session_Table.startTime != None)
                .all())

    def get_avg_total_time_per_student(self, semester_id):
        return db_session.query(StudentSession_Table) \
            .filter(StudentSession_Table.sessionId == Session_Table.id) \
            .filter(Session_Table.semester_id == Semester_Table.id) \
            .filter(Semester_Table.id == semester_id) \
            .filter(Schedule_Table.id == Session_Table.schedule_id)\
            .all()

    def get_schedule_monthly_attendance(self, schedule_id, start_date, end_date):
        return db_session.query(StudentSession_Table)\
            .filter(StudentSession_Table.sessionId == Session_Table.id)\
            .filter(Session_Table.schedule_id == Schedule_Table.id)\
            .filter(Schedule_Table.id == schedule_id)\
            .filter(Session_Table.date.between(start_date, end_date))

    def get_years(self):
        years = db_session.query(Semester_Table.year)\
            .order_by(Semester_Table.year.desc())\
            .distinct()
        years_to_return = []
        for year in years:
            if app.config['LAB_TITLE'] != 'Computer Science Lab':
                years_to_return.append(year)
            elif year.year not in [2004, 2005, 2006]:  # Must be computer science, check for semesters we don't want to pull
                years_to_return.append(year)
        return years_to_return

    def get_monthly_sessions_attendance(self, start_date, end_date):
        return (db_session.query(StudentSession_Table)
                .filter(StudentSession_Table.sessionId == Session_Table.id)\
                .filter(Session_Table.date.between(start_date, end_date))
                .filter(Session_Table.semester_id == Semester_Table.id)
                .filter(Session_Table.startTime != None)
                .all())

    def get_semester_closed_sessions(self, year, term):
        return (db_session.query(Session_Table)
                .filter(Session_Table.semester_id == Semester_Table.id)
                .filter(Semester_Table.year == year)
                .filter(Semester_Table.term == term)
                .filter(Session_Table.startTime != None)
                .all())

    def get_unscheduled_sessions(self, year, term):
        return (db_session.query(Session_Table)
                .filter(Session_Table.deletedAt == None)
                .filter(Session_Table.schedule_id == None)
                .filter(Session_Table.semester_id == Semester_Table.id)
                .filter(Semester_Table.term == term)
                .filter(Semester_Table.year == year)
                .filter(Session_Table.startTime != None)
                .all())

    def get_unscheduled_unique_attendance(self, session_id):
        return db_session.query(User_Table, func.count(distinct(User_Table.id)))\
            .filter(User_Table.id == StudentSession_Table.studentId)\
            .filter(StudentSession_Table.sessionId == session_id)\
            .group_by(User_Table.id)\
            .all()

    def tutor_currently_signed_in(self, session_id, tutor_id):
        return db_session.query(TutorSession_Table).filter(TutorSession_Table.sessionId == session_id)\
            .filter(TutorSession_Table.tutorId == tutor_id).filter(TutorSession_Table.timeIn != None)\
            .filter(TutorSession_Table.timeOut == None).one_or_none()

    def student_currently_signed_in(self, session_id, student_id):
        return db_session.query(StudentSession_Table).filter(StudentSession_Table.sessionId == session_id)\
            .filter(StudentSession_Table.studentId == student_id).filter(StudentSession_Table.timeIn != None)\
            .filter(StudentSession_Table.timeOut == None).one_or_none()

    def get_reservation_sessions(self):
        future_sessions = db_session.query(Session_Table).filter(Session_Table.date >= datetime.now().date())
        valid_sessions = []
        for session in future_sessions:
            time = session.schedStartTime
            reservations_end_time = datetime.combine(session.date, datetime.strptime(str(time + timedelta(minutes=15)), '%H:%M:%S').time())
            reservations_start_time = datetime.combine(session.date, datetime.strptime(str(time), '%H:%M:%S').time())
            if (reservations_start_time - timedelta(days=1)) <= datetime.now() <= reservations_end_time:
                valid_sessions.append(session)

        return valid_sessions

    ######################### EDIT STUDENT METHODS #########################

    def edit_student_session(self, student_session_id, time_in, time_out, other_course, student_courses):
        self.edit_student_session_info(student_session_id, time_in, time_out, other_course)
        self.edit_student_courses(student_session_id, student_courses)

    def edit_student_session_info(self, student_session_id, time_in, time_out, other_course):
        student_session_to_edit = db_session.query(StudentSession_Table) \
            .filter(StudentSession_Table.id == student_session_id) \
            .one()
        student_session_to_edit.timeIn = time_in
        student_session_to_edit.timeOut = time_out
        if other_course:
            student_session_to_edit.otherCourse = 1
            student_session_to_edit.otherCourseName = other_course
        else:
            student_session_to_edit.otherCourse = 0
            student_session_to_edit.otherCourseName = None
        db_session.commit()

    def edit_student_courses(self, student_session_id, student_courses):
        student_session = db_session.query(StudentSession_Table)\
            .filter(StudentSession_Table.id == student_session_id) \
            .one()
        db_session.query(SessionCourses_Table).filter(
            SessionCourses_Table.studentsession_id == student_session.id).delete()
        for course in student_courses:
            new_student_course = SessionCourses_Table(studentsession_id=student_session.id, course_id=course)
            db_session.add(new_student_course)
        db_session.commit()

    ######################### CREATE SESSION METHODS #########################

    def create_new_session(self, semester_id, date, scheduled_start, scheduled_end, actual_start, actual_end, room,
                           comments, anon_students, name, leads, tutors, courses):
        new_session = self.create_session(semester_id, date, scheduled_start, scheduled_end, actual_start,
                                          actual_end, room, comments, anon_students, name)
        self.create_lead_sessions(scheduled_start, scheduled_end, leads, new_session.id)
        self.create_tutor_sessions(scheduled_start, scheduled_end, tutors, new_session.id)
        self.create_session_courses(new_session.id, courses)

    def create_session(self, semester_id, date, scheduled_start, scheduled_end, actual_start, actual_end, room,
                           comments, anon_students, name):
        new_session = Session_Table(semester_id=semester_id, date=date, schedStartTime=scheduled_start,
                                    schedEndTime=scheduled_end, startTime=actual_start, endTime=actual_end, room=room,
                                    open=0, comments=comments, anonStudents=anon_students, name=name,
                                    hash=self.base.get_hash())
        db_session.add(new_session)
        db_session.commit()
        return new_session

    def create_lead_sessions(self, scheduled_start, scheduled_end, leads, session_id):
        for lead in leads:
            new_tutor_session = TutorSession_Table(schedTimeIn=scheduled_start, schedTimeOut=scheduled_end, isLead=1,
                                                   tutorId=lead, sessionId=session_id, substitutable=0)
            db_session.add(new_tutor_session)
        db_session.commit()

    def create_tutor_sessions(self, scheduled_start, scheduled_end, tutors, session_id):
        for tutor in tutors:
            new_tutor_session = TutorSession_Table(schedTimeIn=scheduled_start, schedTimeOut=scheduled_end, isLead=0,
                                                   tutorId=tutor, sessionId=session_id, substitutable=0)
            db_session.add(new_tutor_session)
        db_session.commit()

    def create_session_courses(self, session_id, courses):
        for course in courses:
            new_session_course = SessionCourseCodes_Table(session_id=session_id, coursecode_id=course)
            db_session.add(new_session_course)
        db_session.commit()

    ########################################################################

    ######################### EDIT SESSION METHODS #########################

    def edit_session(self, session_id, semester_id, date, scheduled_start, scheduled_end, actual_start, actual_end,
                     room, comments, anon_students, name, leads, tutors, courses):
        self.edit_session_info(session_id, semester_id, date, scheduled_start, scheduled_end, actual_start,
                               actual_end, room, comments, anon_students, name)
        self.edit_session_leads(scheduled_start, scheduled_end, leads, session_id)
        self.edit_session_tutors(scheduled_start, scheduled_end, tutors, session_id)
        self.edit_session_courses(session_id, courses)

    def edit_session_info(self, session_id, semester_id, date, scheduled_start, scheduled_end, actual_start, actual_end,
                     room, comments, anon_students, name):
        session_to_edit = db_session.query(Session_Table).filter(Session_Table.id == session_id).one()
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
        db_session.commit()

    def edit_session_leads(self, scheduled_start, scheduled_end, leads, session_id):
        current_lead_ids = db_session.query(TutorSession_Table.tutorId)\
            .filter(TutorSession_Table.sessionId == session_id)\
            .filter(TutorSession_Table.isLead == 1).all()
        # Check to see if any current leads are still leads, and if not delete them
        for current_lead in current_lead_ids:
            if current_lead in leads:
                leads.remove(current_lead)  # Remove lead from list to add
            else:
                db_session.query(TutorSession_Table).filter(TutorSession_Table.sessionId == session_id)\
                    .filter(TutorSession_Table.tutorId == current_lead).delete()  # delete if not still lead
        db_session.commit()
        if leads:  # If there are still leads left we need to add them now
            self.create_lead_sessions(scheduled_start, scheduled_end, leads, session_id)

    def edit_session_tutors(self, scheduled_start, scheduled_end, tutors, session_id):
        current_tutor_ids = db_session.query(TutorSession_Table.tutorId)\
            .filter(TutorSession_Table.sessionId == session_id) \
            .filter(TutorSession_Table.isLead == 0).all()
        # Check to see if any current tutors are still tutors
        for current_tutor in current_tutor_ids:
            if current_tutor in tutors:
                tutors.remove(current_tutor)  # Remove tutor from list to add
            else:
                db_session.query(TutorSession_Table).filter(TutorSession_Table.sessionId == session_id) \
                    .filter(TutorSession_Table.tutorId == current_tutor).delete()  # delete if not still tutor
        db_session.commit()
        if tutors:  # If there are still tutors we need to add them now
            self.create_tutor_sessions(scheduled_start, scheduled_end, tutors, session_id)

    def edit_session_courses(self, session_id, courses):
        db_session.query(SessionCourseCodes_Table).filter(SessionCourseCodes_Table.session_id == session_id).delete()
        db_session.commit()
        self.create_session_courses(session_id, courses)

    ########################################################################

    def restore_deleted_session(self, session_id):
        session_to_restore = db_session.query(Session_Table).filter(Session_Table.id == session_id).one()
        session_to_restore.deletedAt = None
        db_session.commit()

    def start_open_session(self, session_id, opener_id):
        session_to_open = db_session.query(Session_Table).filter(Session_Table.id == session_id).one()
        session_to_open.open = 1
        session_to_open.startTime = datetime.now().strftime('%H:%M:%S')
        session_to_open.openerId = opener_id
        db_session.commit()
        self.log_session('{0} ({1}) opened at {2}'.format(session_to_open.name,
                                                          session_to_open.date.strftime("%m/%d/%Y"),
                                                          datetime.now().strftime("%H:%M:%S")))

    def close_open_session(self, session_id, comments):
        session_to_close = db_session.query(Session_Table).filter(Session_Table.id == session_id).one()
        session_to_close.open = 0
        session_to_close.endTime = datetime.now().strftime('%H:%M:%S')
        session_to_close.comments = comments
        db_session.commit()
        self.log_session('{0} ({1}) closed at {2}'.format(session_to_close.name,
                                                          session_to_close.date.strftime("%m/%d/%Y"),
                                                          datetime.now().strftime("%H:%M:%S")))

    def tutor_sign_in(self, session_id, tutor_id):
        tutor_session = db_session.query(TutorSession_Table).filter(TutorSession_Table.sessionId == session_id)\
            .filter(TutorSession_Table.tutorId == tutor_id).filter(TutorSession_Table.timeIn == None).one_or_none()
        if tutor_session:
            tutor_session.timeIn = datetime.now().strftime("%H:%M:%S")
            db_session.commit()
        else:
            self.add_tutor_to_session(session_id, tutor_id, datetime.now().strftime("%H:%M:%S"), None, 0)
        tutor = db_session.query(User_Table).filter(User_Table.id == tutor_id).one()
        self.log_session('{0} {1} signed in as a tutor at {2}'.format(tutor.firstName, tutor.lastName,
                                                                      datetime.now().strftime("%m/%d/%Y %H:%M:%S")))

    def tutor_sign_out(self, session_id, tutor_id):
        tutor_session = db_session.query(TutorSession_Table).filter(TutorSession_Table.sessionId == session_id)\
            .filter(TutorSession_Table.tutorId == tutor_id).filter(TutorSession_Table.timeOut == None).one_or_none()
        if not tutor_session:
            return False
        tutor_session.timeOut = datetime.now().strftime('%H:%M:%S')
        db_session.commit()
        tutor = db_session.query(User_Table).filter(User_Table.id == tutor_id).one()
        self.log_session('{0} {1} signed out as a tutor at {2}'.format(tutor.firstName, tutor.lastName,
                                                                       datetime.now().strftime("%m/%d/%Y %H:%M:%S")))
        return True

    def student_sign_in(self, session_id, student_id, student_course_ids, other_course, other_name, time_in):
        db_time = datetime.strptime(time_in, "%I:%M%p").strftime("%H:%M:%S")
        # Create student session
        new_student_session = StudentSession_Table(timeIn=db_time, studentId=student_id,
                                                   sessionId=session_id, otherCourse=other_course,
                                                   otherCourseName=other_name)
        db_session.add(new_student_session)
        db_session.commit()
        # Create student session courses
        for course_id in student_course_ids:
            new_student_course = SessionCourses_Table(studentsession_id=new_student_session.id, course_id=course_id)
            db_session.add(new_student_course)
        db_session.commit()
        student = db_session.query(User_Table).filter(User_Table.id == student_id).one()
        self.log_session('{0} {1} signed in as a student at {2}'.format(student.firstName, student.lastName,
                                                                        datetime.now().strftime("%m/%d/%Y %H:%M:%S")))

    def student_sign_out(self, session_id, student_id):
        student_session = db_session.query(StudentSession_Table).filter(StudentSession_Table.sessionId == session_id)\
            .filter(StudentSession_Table.studentId == student_id).filter(StudentSession_Table.timeOut == None).all()
        for single_student_session in student_session:
            single_student_session.timeOut = datetime.now().strftime('%H:%M:%S')
        db_session.commit()
        student = db_session.query(User_Table).filter(User_Table.id == student_id).one()
        self.log_session('{0} {1} signed out as a student at {2}'.format(student.firstName, student.lastName,
                                                                         datetime.now().strftime("%m/%d/%Y %H:%M:%S")))

    def close_open_sessions_cron(self):
        open_sessions = self.get_open_sessions()
        for open_session in open_sessions:
            message = 'Closed by the system on {0}'.format(datetime.now().strftime('%m/%d/%Y'))
            if open_session.comments:
                message += ' with message {0}'.format(open_session.comments)
            self.close_open_session(open_session.id, message)
        db_session.commit()
        return open_sessions

    def log_session(self, message):
        session_log = open(app.config['INSTALL_LOCATION'] + '/session_info.log', 'a')
        session_log.write(message + '\n')
        session_log.close()
