from sqlalchemy import func, or_

from sciencelabs.db_repository import session
from sciencelabs.db_repository.db_tables import Schedule_Table, Session_Table, Semester_Table, StudentSession_Table, \
    ScheduleCourseCodes_Table, CourseCode_Table, User_Table, TutorSchedule_Table, user_role_Table, Role_Table


class Schedule:

    def get_schedule_tab_info(self):
        return session.query(Schedule_Table) \
            .filter(Schedule_Table.id == Session_Table.schedule_id) \
            .filter(Session_Table.semester_id == Semester_Table.id) \
            .filter(Semester_Table.active == 1) \
            .all()

    def get_term_report(self):
        return session.query(Schedule_Table, func.count(Schedule_Table.id)) \
            .filter(Session_Table.startTime != None) \
            .filter(Session_Table.schedule_id == Schedule_Table.id) \
            .filter(Session_Table.semester_id == Semester_Table.id) \
            .filter(Semester_Table.active == 1) \
            .group_by(Schedule_Table.id).all()

    def get_session_attendance(self):
        return session.query(Schedule_Table, func.count(Schedule_Table.id)) \
            .filter(StudentSession_Table.sessionId == Session_Table.id) \
            .filter(Session_Table.semester_id == Semester_Table.id) \
            .filter(Semester_Table.active == 1) \
            .filter(Schedule_Table.id == Session_Table.schedule_id) \
            .group_by(Schedule_Table.id).all()

    def get_active_semester(self):
        return session.query(Semester_Table).filter(Semester_Table.active == 1).one()

    def get_semesters(self):
        return session.query(Semester_Table).order_by(Semester_Table.year.desc()).all()

    def get_registered_leads(self):
        return session.query(User_Table.id, User_Table.firstName, User_Table.lastName)\
            .filter(User_Table.id == user_role_Table.user_id)\
            .filter(user_role_Table.role_id == Role_Table.id)\
            .filter(Role_Table.name == "Lead Tutor")\
            .filter(User_Table.deletedAt == None).order_by(User_Table.lastName).all()

    def get_registered_tutors(self):
        return session.query(User_Table.id, User_Table.firstName, User_Table.lastName)\
            .filter(User_Table.id == user_role_Table.user_id)\
            .filter(user_role_Table.role_id == Role_Table.id)\
            .filter(or_(Role_Table.name == "Tutor", Role_Table.name == "Lead Tutor")) \
            .filter(User_Table.deletedAt == None).order_by(User_Table.lastName).distinct()

    def get_registered_students(self):
        return session.query(User_Table.id, User_Table.firstName, User_Table.lastName) \
            .filter(User_Table.id == user_role_Table.user_id) \
            .filter(user_role_Table.role_id == Role_Table.id) \
            .filter(Role_Table.name == "Student") \
            .filter(User_Table.deletedAt == None).order_by(User_Table.lastName).distinct()

    def get_schedule_courses(self, schedule_id):
        courses = session.query(ScheduleCourseCodes_Table, CourseCode_Table)\
            .filter(ScheduleCourseCodes_Table.schedule_id == schedule_id)\
            .filter(ScheduleCourseCodes_Table.coursecode_id == CourseCode_Table.id)\
            .all()
        schedule_courses = []
        for schedulecoursecode, coursecode in courses:
            schedule_courses.append(coursecode.dept + ' ' + coursecode.courseNum)
        return schedule_courses

    def get_schedule(self, schedule_id):
        return session.query(Schedule_Table).filter(Schedule_Table.id == schedule_id).one()

    def get_schedule_tutors(self, schedule_id):
        return session.query(User_Table.id, User_Table.firstName, User_Table.lastName, TutorSchedule_Table.lead,
                             TutorSchedule_Table.schedTimeIn, TutorSchedule_Table.schedTimeOut)\
            .filter(TutorSchedule_Table.scheduleId == schedule_id)\
            .filter(User_Table.id == TutorSchedule_Table.tutorId)\
            .order_by(TutorSchedule_Table.lead.desc())

    def get_schedule_tutor_names(self, schedule_id):
        return session.query(User_Table.id, User_Table.firstName, User_Table.lastName) \
            .filter(TutorSchedule_Table.scheduleId == schedule_id)\
            .filter(User_Table.id == TutorSchedule_Table.tutorId)\
            .order_by(TutorSchedule_Table.lead.desc())\
            .all()

