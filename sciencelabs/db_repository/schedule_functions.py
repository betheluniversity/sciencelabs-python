from sqlalchemy import func

from sciencelabs.db_repository import session
from sciencelabs.db_repository.db_tables import Schedule, Session, Semester, StudentSession


class ScheduleFunctions:

    def get_schedule_tab_info(self):
        return session.query(Schedule) \
            .filter(Schedule.id == Session.schedule_id) \
            .filter(Session.semester_id == Semester.id) \
            .filter(Semester.active == 1) \
            .all()

    def get_term_report(self):
        return session.query(Schedule, func.count(Schedule.id)) \
            .filter(Session.startTime != None) \
            .filter(Session.schedule_id == Schedule.id) \
            .filter(Session.semester_id == Semester.id) \
            .filter(Semester.active == 1) \
            .group_by(Schedule.id).all()

    def get_session_attendance(self):
        return session.query(Schedule, func.count(Schedule.id)) \
            .filter(StudentSession.sessionId == Session.id) \
            .filter(Session.semester_id == Semester.id) \
            .filter(Semester.active == 1) \
            .filter(Schedule.id == Session.schedule_id) \
            .group_by(Schedule.id).all()
