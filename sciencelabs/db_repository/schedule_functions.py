from datetime import datetime, timedelta, date
from sqlalchemy import func, or_

from sciencelabs.db_repository import db_session
from sciencelabs.db_repository.db_tables import Schedule_Table, Session_Table, Semester_Table, StudentSession_Table, \
    ScheduleCourseCodes_Table, CourseCode_Table, User_Table, TutorSchedule_Table, user_role_Table, Role_Table, \
    TutorSession_Table, SessionCourseCodes_Table
from sciencelabs.sciencelabs_controller import ScienceLabsController


class Schedule:

    def __init__(self):
        self.base = ScienceLabsController()

    def check_schedule_room_groupings(self, schedule_id):
        sessions = self.get_sessions_by_schedule(schedule_id)
        num_sessions = len(sessions)
        num_room_groups = 0
        for session in sessions:
            if session.room_group_id:
                num_room_groups += 1

        if num_sessions == num_room_groups:
            return True
        return False



    def get_schedule_tab_info(self):
        return db_session.query(Schedule_Table) \
            .filter(Schedule_Table.id == Session_Table.schedule_id) \
            .filter(Session_Table.semester_id == Semester_Table.id) \
            .filter(Semester_Table.active == 1)\
            .filter(Schedule_Table.deletedAt == None) \
            .all()

    def get_schedule_sessions(self):
        return db_session.query(Session_Table).filter(Schedule_Table.id == Session_Table.schedule_id) \
            .filter(Session_Table.semester_id == Semester_Table.id) \
            .filter(Semester_Table.active == 1)\
            .filter(Schedule_Table.deletedAt == None) \

    def get_yearly_schedule_tab_info(self, year, term):
        return db_session.query(Schedule_Table) \
            .filter(Schedule_Table.id == Session_Table.schedule_id) \
            .filter(Session_Table.deletedAt == None)\
            .filter(Session_Table.semester_id == Semester_Table.id) \
            .filter(Semester_Table.year == year)\
            .filter(Semester_Table.term == term)\
            .all()

    def get_term_report(self, semester_id):
        return db_session.query(Schedule_Table, func.count(Schedule_Table.id)) \
            .filter(Session_Table.startTime != None) \
            .filter(Session_Table.endTime != None) \
            .filter(Schedule_Table.id != None) \
            .filter(Schedule_Table.term == Semester_Table.term) \
            .filter(Schedule_Table.startTime != None) \
            .filter(Schedule_Table.endTime != None) \
            .filter(Session_Table.schedule_id == Schedule_Table.id) \
            .filter(Schedule_Table.deletedAt == None) \
            .filter(Session_Table.deletedAt == None) \
            .filter(Session_Table.semester_id == Semester_Table.id) \
            .filter(Semester_Table.id == semester_id) \
            .group_by(Schedule_Table.id)\
            .all()

    def get_anon_student_attendance_info(self, semester_id):
        return db_session.query(Session_Table, Schedule_Table)\
            .filter(Session_Table.schedule_id == Schedule_Table.id)\
            .filter(Session_Table.startTime)\
            .filter(Session_Table.deletedAt == None)\
            .filter(Session_Table.semester_id == semester_id)\
            .all()

    def get_active_semester(self):
        return db_session.query(Semester_Table)\
            .filter(Semester_Table.active == 1)\
            .one()

    def get_semesters(self):
        return db_session.query(Semester_Table)\
            .order_by(Semester_Table.id.desc())\
            .all()

    def get_semester(self, semester_id):
        return db_session.query(Semester_Table)\
            .filter(Semester_Table.id == semester_id)\
            .one()

    def get_semester_by_year(self, year, term):
        return db_session.query(Semester_Table)\
            .filter(Semester_Table.term == term)\
            .filter(Semester_Table.year == year)\
            .first()

    def get_registered_leads(self):
        return db_session.query(User_Table.id, User_Table.firstName, User_Table.lastName)\
            .filter(User_Table.id == user_role_Table.user_id)\
            .filter(user_role_Table.role_id == Role_Table.id)\
            .filter(Role_Table.name == "Lead Tutor")\
            .filter(User_Table.deletedAt == None)\
            .order_by(User_Table.lastName)\
            .all()

    def get_registered_tutors(self):
        return db_session.query(User_Table.id, User_Table.firstName, User_Table.lastName)\
            .filter(User_Table.id == user_role_Table.user_id)\
            .filter(user_role_Table.role_id == Role_Table.id)\
            .filter(or_(Role_Table.name == "Tutor", Role_Table.name == "Lead Tutor")) \
            .filter(User_Table.deletedAt == None)\
            .order_by(User_Table.lastName)\
            .distinct()

    def get_registered_students(self):
        return db_session.query(User_Table.id, User_Table.firstName, User_Table.lastName) \
            .filter(User_Table.id == user_role_Table.user_id) \
            .filter(user_role_Table.role_id == Role_Table.id) \
            .filter(Role_Table.name == 'Student') \
            .filter(User_Table.deletedAt == None)\
            .order_by(User_Table.lastName)\
            .distinct()

    def get_schedule_courses(self, schedule_id):
        courses = db_session.query(ScheduleCourseCodes_Table, CourseCode_Table)\
            .filter(ScheduleCourseCodes_Table.schedule_id == schedule_id)\
            .filter(ScheduleCourseCodes_Table.coursecode_id == CourseCode_Table.id)\
            .all()
        schedule_courses = []
        for schedulecoursecode, coursecode in courses:
            schedule_courses.append('{0} {1}'.format(coursecode.dept, coursecode.courseNum))
        return schedule_courses

    def get_schedule(self, schedule_id):
        return db_session.query(Schedule_Table)\
            .filter(Schedule_Table.id == schedule_id)\
            .one()

    def get_schedule_from_session(self, session_id):
        return db_session.query(Schedule_Table)\
            .filter(Session_Table.id == session_id)\
            .filter(Session_Table.schedule_id == Schedule_Table.id)\
            .first()

    def get_schedule_tutors(self, schedule_id):
        return db_session.query(User_Table.id, User_Table.firstName, User_Table.lastName, TutorSchedule_Table.isLead,
                                TutorSchedule_Table.schedTimeIn, TutorSchedule_Table.schedTimeOut)\
            .filter(TutorSchedule_Table.scheduleId == schedule_id)\
            .filter(User_Table.id == TutorSchedule_Table.tutorId)\
            .order_by(TutorSchedule_Table.isLead.desc())

    def get_scheduled_lead_ids(self, schedule_id):
        lead_ids = []
        leads = db_session.query(User_Table).filter(TutorSchedule_Table.scheduleId == schedule_id)\
            .filter(TutorSchedule_Table.isLead == 1).filter(TutorSchedule_Table.tutorId == User_Table.id).all()
        for lead in leads:
            lead_ids.append(lead.id)
        return lead_ids

    def get_scheduled_tutor_ids(self, schedule_id):
        tutor_ids = []
        tutors = db_session.query(User_Table).filter(TutorSchedule_Table.scheduleId == schedule_id) \
            .filter(TutorSchedule_Table.isLead == 0).filter(TutorSchedule_Table.tutorId == User_Table.id).all()
        for tutor in tutors:
            tutor_ids.append(tutor.id)
        return tutor_ids

    def delete_schedule(self, schedule_id):
        schedule_to_delete = self.get_schedule(schedule_id)
        schedule_to_delete.deletedAt = datetime.now()
        scheduled_sessions = self.get_sessions_by_schedule(schedule_id)
        self.delete_old_scheduled_sessions(scheduled_sessions)
        db_session.commit()

    def set_current_term(self, term, year, start_date, end_date):
        current_term = db_session.query(Semester_Table)\
            .filter(Semester_Table.active == 1)\
            .one()
        current_term.active = 0
        db_start_date = datetime.strptime(start_date, "%m/%d/%Y").strftime("%Y-%m-%d")
        db_end_date = datetime.strptime(end_date, "%m/%d/%Y").strftime("%Y-%m-%d")
        new_term = Semester_Table(term=term, year=year, startDate=db_start_date, endDate=db_end_date, active=1)
        db_session.add(new_term)
        db_session.commit()

    ######################## CREATE SCHEDULE METHODS #########################

    def create_schedule(self, term, term_start_date, term_end_date, term_id, name, room, start_time, end_time,
                        day_of_week, capacity, leads, tutors, courses):
        # Creates the schedule and returns it
        new_schedule = self.create_new_schedule(name, room, start_time, end_time, day_of_week, term)
        # Creates the recurring sessions for the schedule and returns them in an array
        scheduled_sessions = self.create_scheduled_sessions(term_start_date, term_end_date, day_of_week, term_id,
                                                            new_schedule.id, start_time, end_time, capacity, room, name)
        # Creates leads tutor schedules
        self.create_new_lead_schedules(new_schedule.id, start_time, end_time, leads)
        # Creates leads recurring tutor sessions
        self.create_lead_scheduled_sessions(leads, start_time, end_time, scheduled_sessions)
        # Creates tutors tutor schedules
        self.create_new_tutor_schedules(new_schedule.id, start_time, end_time, tutors)
        # Creates tutors recurring tutor sessions
        self.create_tutor_scheduled_sessions(tutors, start_time, end_time, scheduled_sessions)
        # Creates schedule courses
        self.create_new_schedule_courses(new_schedule.id, courses)
        # Creates recurring session courses
        self.create_scheduled_session_courses(scheduled_sessions, courses)

        return scheduled_sessions

    def create_new_schedule(self, name, room, start_time, end_time, day_of_week, term):
        new_schedule = Schedule_Table(name=name, room=room, startTime=start_time, endTime=end_time,
                                      dayofWeek=day_of_week, term=term)
        db_session.add(new_schedule)
        db_session.commit()
        return new_schedule

    def create_new_lead_schedules(self, schedule_id, time_in, time_out, leads):
        for lead in leads:
            new_lead_schedule = TutorSchedule_Table(schedTimeIn=time_in, schedTimeOut=time_out, isLead=1,
                                                    tutorId=lead, scheduleId=schedule_id)
            db_session.add(new_lead_schedule)
        db_session.commit()

    def create_new_tutor_schedules(self, schedule_id, time_in, time_out, tutors):
        for tutor in tutors:
            new_tutor_schedule = TutorSchedule_Table(schedTimeIn=time_in, schedTimeOut=time_out, isLead=0,
                                                     tutorId=tutor, scheduleId=schedule_id)
            db_session.add(new_tutor_schedule)
        db_session.commit()

    def create_new_schedule_courses(self, schedule_id, courses):
        for course in courses:
            new_schedule_course = ScheduleCourseCodes_Table(schedule_id=schedule_id, coursecode_id=course)
            db_session.add(new_schedule_course)
        db_session.commit()

    def create_scheduled_sessions(self, term_start_date, term_end_date, day_of_week, term_id, schedule_id, start_time,
                                  end_time, capacity, room, name):
        sessions = []
        session_date = self.get_first_session_date(day_of_week, term_start_date)
        while session_date <= term_end_date:  # Loop through until our session date is after the end date of the term
            schedule_session = Session_Table(semester_id=term_id, schedule_id=schedule_id,
                                             date=session_date, schedStartTime=start_time,
                                             schedEndTime=end_time, room=room, open=0, hash=self.base.get_hash(),
                                             anonStudents=0, name=name, capacity=capacity)
            db_session.add(schedule_session)
            db_session.commit()
            sessions.append(schedule_session)
            session_date += timedelta(weeks=1)  # Add a week for next session

        return sessions

    def create_lead_scheduled_sessions(self, leads, start_time, end_time, scheduled_sessions):
        for new_session in scheduled_sessions:
            for lead in leads:
                new_tutor_session = TutorSession_Table(schedTimeIn=start_time, schedTimeOut=end_time, isLead=1,
                                                       tutorId=lead, sessionId=new_session.id, substitutable=0)
                db_session.add(new_tutor_session)
        db_session.commit()

    def create_tutor_scheduled_sessions(self, tutors, start_time, end_time, scheduled_sessions):
        for new_session in scheduled_sessions:
            for tutor in tutors:
                new_tutor_session = TutorSession_Table(schedTimeIn=start_time, schedTimeOut=end_time, isLead=0,
                                                       tutorId=tutor, sessionId=new_session.id, substitutable=0)
                db_session.add(new_tutor_session)
        db_session.commit()

    def create_scheduled_session_courses(self, scheduled_sessions, courses):
        for new_session in scheduled_sessions:
            for course in courses:
                new_course = SessionCourseCodes_Table(session_id=new_session.id, coursecode_id=course)
                db_session.add(new_course)
        db_session.commit()

    def get_first_session_date(self, week_day, semester_start):
        first_date = semester_start
        today = date.today()
        if today > first_date:
            first_date = today
        while True:
            # return the first day of the schedule after the semester starts
            if first_date.weekday() == (week_day + 6) % 7:  # Our DB Sunday = 0, Python datetime Monday = 0
                return first_date
            else:
                first_date += timedelta(days=1)  # if it hasn't matched, add a day and check again

    ######################## EDIT SCHEDULE METHODS #########################

    def edit_schedule(self, term_start_date, term_end_date, term_id, schedule_id, name, room, start_time,
                      end_time, day_of_week, capacity, leads, tutors, courses):
        # Gets an array of sessions based on the schedule id
        scheduled_sessions = self.get_sessions_by_schedule(schedule_id)
        # Deletes the old sessions so we can create new sessions
        self.delete_old_scheduled_sessions(scheduled_sessions)
        # Deletes the old TutorSchedule and ScheduleCourseCodes entries
        self.delete_old_schedule_tutors_and_courses(schedule_id)
        # Edits the schedule
        self.edit_schedule_info(schedule_id, name, room, start_time, end_time, day_of_week)
        # Creates the new recurring sessions for the schedule
        new_sessions = self.create_scheduled_sessions(term_start_date, term_end_date, day_of_week, term_id,
                                                      schedule_id, start_time, end_time, capacity, room, name)
        # Edits the lead's schedule
        self.create_new_lead_schedules(schedule_id, start_time, end_time, leads)
        # Creates the new recurring sessions for the lead
        self.create_lead_scheduled_sessions(leads, start_time, end_time, new_sessions)
        # Edits the tutor's schedule
        self.create_new_tutor_schedules(schedule_id, start_time, end_time, tutors)
        # Creates the new recurring sessions for the tutor
        self.create_tutor_scheduled_sessions(tutors, start_time, end_time, new_sessions)
        # Edits the schedules courses
        self.create_new_schedule_courses(schedule_id, courses)
        # Creates the new recurring session's courses
        self.create_scheduled_session_courses(new_sessions, courses)

        return new_sessions

    def delete_old_scheduled_sessions(self, scheduled_sessions):
        # In here we want to check that we're not deleting sessions that have already happened, so check for a startTime
        for scheduled_session in scheduled_sessions:
            if scheduled_session.startTime:
                continue
            else:
                db_session.query(TutorSession_Table).filter(TutorSession_Table.sessionId == scheduled_session.id).delete()
                db_session.query(SessionCourseCodes_Table)\
                    .filter(SessionCourseCodes_Table.session_id == scheduled_session.id).delete()
                db_session.query(Session_Table).filter(Session_Table.id == scheduled_session.id).delete()
        db_session.commit()

    def delete_old_schedule_tutors_and_courses(self, schedule_id):
        db_session.query(TutorSchedule_Table).filter(TutorSchedule_Table.scheduleId == schedule_id).delete()
        db_session.query(ScheduleCourseCodes_Table).filter(ScheduleCourseCodes_Table.schedule_id == schedule_id).delete()
        db_session.commit()

    def get_sessions_by_schedule(self, schedule_id):
        return db_session.query(Session_Table).filter(Session_Table.schedule_id == schedule_id).all()

    def get_first_session_by_schedule(self, schedule_id):
        return db_session.query(Session_Table).filter(Session_Table.schedule_id == schedule_id).first()

    def edit_schedule_info(self, schedule_id, name, room, start_time, end_time, day_of_week):
        schedule_to_edit = db_session.query(Schedule_Table).filter(Schedule_Table.id == schedule_id).one()
        schedule_to_edit.name = name
        schedule_to_edit.room = room
        schedule_to_edit.startTime = start_time
        schedule_to_edit.endTime = end_time
        schedule_to_edit.dayofWeek = day_of_week
        db_session.commit()

    def edit_lead_schedules(self, schedule_id, time_in, time_out, leads):
        db_session.query(TutorSchedule_Table).filter(TutorSchedule_Table.scheduleId == schedule_id)\
            .filter(TutorSchedule_Table.isLead == 1).delete()
        for lead in leads:
            new_lead_schedule = TutorSchedule_Table(schedTimeIn=time_in, schedTimeOut=time_out, isLead=1,
                                                    tutorId=lead, scheduleId=schedule_id)
            db_session.add(new_lead_schedule)
        db_session.commit()

    def edit_tutor_schedules(self, schedule_id, time_in, time_out, tutors):
        db_session.query(TutorSchedule_Table).filter(TutorSchedule_Table.scheduleId == schedule_id) \
            .filter(TutorSchedule_Table.isLead == 0).delete()
        for tutor in tutors:
            new_tutor_schedule = TutorSchedule_Table(schedTimeIn=time_in, schedTimeOut=time_out, isLead=0,
                                                     tutorId=tutor, scheduleId=schedule_id)
            db_session.add(new_tutor_schedule)
        db_session.commit()

    def edit_schedule_courses(self, schedule_id, courses):
        db_session.query(ScheduleCourseCodes_Table).filter(ScheduleCourseCodes_Table.schedule_id == schedule_id).delete()
        for course in courses:
            new_schedule_course = ScheduleCourseCodes_Table(schedule_id=schedule_id, coursecode_id=course)
            db_session.add(new_schedule_course)
        db_session.commit()

    def get_total_semester_attendance(self, semester_id):
        semester_student_sessions = db_session.query(StudentSession_Table)\
            .filter(StudentSession_Table.sessionId == Session_Table.id)\
            .filter(Session_Table.semester_id == semester_id).all()
        return len(semester_student_sessions)

    def create_semester_check(self, term, year):
        semester_exists = db_session.query(Semester_Table)\
            .filter(Semester_Table.term == term)\
            .filter(Semester_Table.year == year)\
            .one_or_none()
        if semester_exists:
            return True
        return False
