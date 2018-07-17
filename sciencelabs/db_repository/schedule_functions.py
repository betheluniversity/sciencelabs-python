from sqlalchemy import func

from sciencelabs.db_repository import session
from sciencelabs.db_repository.db_tables import Schedule_Table, Session_Table, Semester_Table, StudentSession_Table


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
        return session.query(Semester_Table.id, Semester_Table.term, Semester_Table.year)\
            .filter(Semester_Table.active == 1).one()

    def get_semesters(self):
        return session.query(Semester_Table.id, Semester_Table.term, Semester_Table.year, Semester_Table.active)\
            .order_by(Semester_Table.year.desc()).all()

    def get_semester_info(self, semester_id):
        return session.query(Semester_Table.id, Semester_Table.term, Semester_Table.year) \
            .filter(Semester_Table.id == semester_id).one()
