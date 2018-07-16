from sqlalchemy import func

from sciencelabs.db_repository import session
from sciencelabs.db_repository.db_tables import Schedule_Table, Session_Table, Semester_Table, StudentSession_Table, ScheduleCourseCodes_Table, CourseCode_Table


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