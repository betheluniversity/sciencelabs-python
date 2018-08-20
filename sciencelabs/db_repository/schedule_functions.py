from datetime import datetime
from sqlalchemy import func, or_

from sciencelabs.db_repository import session
from sciencelabs.db_repository.db_tables import Schedule_Table, Session_Table, Semester_Table, StudentSession_Table, \
    ScheduleCourseCodes_Table, CourseCode_Table, User_Table, TutorSchedule_Table, user_role_Table, Role_Table


class Schedule:

    def get_schedule_tab_info(self):
        return session.query(Schedule_Table) \
            .filter(Schedule_Table.id == Session_Table.schedule_id) \
            .filter(Session_Table.semester_id == Semester_Table.id) \
            .filter(Semester_Table.active == 1)\
            .filter(Schedule_Table.deletedAt == None) \
            .all()

    def get_yearly_schedule_tab_info(self, year, term):
        return session.query(Schedule_Table) \
            .filter(Schedule_Table.id == Session_Table.schedule_id) \
            .filter(Session_Table.deletedAt == None)\
            .filter(Session_Table.semester_id == Semester_Table.id) \
            .filter(Semester_Table.year == year)\
            .filter(Semester_Table.term == term)\
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

    def get_schedule_from_session(self, session_id):
        return session.query(Schedule_Table).filter(Session_Table.id == session_id)\
            .filter(Session_Table.schedule_id == Schedule_Table.id).first()

    def get_schedule_tutors(self, schedule_id):
        return session.query(User_Table.id, User_Table.firstName, User_Table.lastName, TutorSchedule_Table.isLead,
                             TutorSchedule_Table.schedTimeIn, TutorSchedule_Table.schedTimeOut)\
            .filter(TutorSchedule_Table.scheduleId == schedule_id)\
            .filter(User_Table.id == TutorSchedule_Table.tutorId)\
            .order_by(TutorSchedule_Table.isLead.desc())

    def get_schedule_tutor_names(self, schedule_id):
        return session.query(User_Table.id, User_Table.firstName, User_Table.lastName) \
            .filter(TutorSchedule_Table.scheduleId == schedule_id)\
            .filter(User_Table.id == TutorSchedule_Table.tutorId)\
            .order_by(TutorSchedule_Table.isLead.desc())\
            .all()

    def delete_schedule(self, schedule_id):
        schedule_to_delete = self.get_schedule(schedule_id)
        schedule_to_delete.deletedAt = datetime.now()
        session.commit()

    def set_current_term(self, term, year, start_date, end_date):
        current_term = session.query(Semester_Table).filter(Semester_Table.active == 1).one()
        current_term.active = 0
        db_start_date = datetime.strptime(start_date, "%a %b %d %Y").strftime("%Y-%m-%d")
        db_end_date = datetime.strptime(end_date, "%a %b %d %Y").strftime("%Y-%m-%d")
        new_term = Semester_Table(term=term, year=year, startDate=db_start_date, endDate=db_end_date, active=1)
        session.add(new_term)
        session.commit()

    def create_new_schedule(self, name, room, start_time, end_time, day_of_week, term):
        new_schedule = Schedule_Table(name=name, room=room, startTime=start_time, endTime=end_time,
                                      dayofWeek=day_of_week, term=term)
        session.add(new_schedule)
        session.commit()

    def get_new_schedule_id(self, name, room, start_time, end_time, day_of_week, term):
        return session.query(Schedule_Table.id)\
            .filter(Schedule_Table.name == name)\
            .filter(Schedule_Table.room == room)\
            .filter(Schedule_Table.startTime == start_time)\
            .filter(Schedule_Table.endTime == end_time)\
            .filter(Schedule_Table.dayofWeek == day_of_week)\
            .filter(Schedule_Table.term == term)\
            .one()

    def create_new_lead_schedules(self, schedule_id, time_in, time_out, leads):
        for lead in leads:
            new_lead_schedule = TutorSchedule_Table(schedTimeIn=time_in, schedTimeOut=time_out, isLead=1,
                                                    tutorId=lead, scheduleId=schedule_id)
            session.add(new_lead_schedule)
        session.commit()

    def create_new_tutor_schedules(self, schedule_id, time_in, time_out, tutors):
        for tutor in tutors:
            new_tutor_schedule = TutorSchedule_Table(schedTimeIn=time_in, schedTimeOut=time_out, isLead=0,
                                                     tutorId=tutor, scheduleId=schedule_id)
            session.add(new_tutor_schedule)
        session.commit()

    def create_new_schedule_courses(self, schedule_id, courses):
        for course in courses:
            new_schedule_course = ScheduleCourseCodes_Table(schedule_id=schedule_id, coursecode_id=course)
            session.add(new_schedule_course)
        session.commit()

    def edit_schedule(self, schedule_id, name, room, start_time, end_time, day_of_week):
        schedule_to_edit = session.query(Schedule_Table).filter(Schedule_Table.id == schedule_id).one()
        schedule_to_edit.name = name
        schedule_to_edit.room = room
        schedule_to_edit.startTime = start_time
        schedule_to_edit.endTime = end_time
        schedule_to_edit.dayofWeek = day_of_week
        session.commit()

    def edit_lead_schedules(self, schedule_id, time_in, time_out, leads):
        session.query(TutorSchedule_Table).filter(TutorSchedule_Table.scheduleId == schedule_id)\
            .filter(TutorSchedule_Table.isLead == 1).delete()
        for lead in leads:
            new_lead_schedule = TutorSchedule_Table(schedTimeIn=time_in, schedTimeOut=time_out, isLead=1,
                                                    tutorId=lead, scheduleId=schedule_id)
            session.add(new_lead_schedule)
        session.commit()

    def edit_tutor_schedules(self, schedule_id, time_in, time_out, tutors):
        session.query(TutorSchedule_Table).filter(TutorSchedule_Table.scheduleId == schedule_id) \
            .filter(TutorSchedule_Table.isLead == 0).delete()
        for tutor in tutors:
            new_tutor_schedule = TutorSchedule_Table(schedTimeIn=time_in, schedTimeOut=time_out, isLead=0,
                                                     tutorId=tutor, scheduleId=schedule_id)
            session.add(new_tutor_schedule)
        session.commit()

    def edit_schedule_courses(self, schedule_id, courses):
        session.query(ScheduleCourseCodes_Table).filter(ScheduleCourseCodes_Table.schedule_id == schedule_id).delete()
        for course in courses:
            new_schedule_course = ScheduleCourseCodes_Table(schedule_id=schedule_id, coursecode_id=course)
            session.add(new_schedule_course)
        session.commit()
