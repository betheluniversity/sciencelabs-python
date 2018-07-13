from sqlalchemy import *

from sciencelabs.db_repository import Base
from sciencelabs.db_repository import session
from sciencelabs.db_repository.SemesterRepo import Semester
from sciencelabs.db_repository.SessionRepo import Session
from sciencelabs.db_repository.StudentSessionRepo import StudentSession


class Schedule(Base):
    __tablename__ = 'Schedule'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    room = Column(String)
    startTime = Column(String)
    endTime = Column(String)
    dayofWeek = Column(Integer)
    term = Column(String)
    deletedAt = Column(String)

    def get_schedule_tab_info(self):
        return session.query(Schedule)\
            .filter(Schedule.id == Session.schedule_id)\
            .filter(Session.semester_id == Semester.id)\
            .filter(Semester.active == 1)\
            .all()

    def get_term_report(self):
        return session.query(Schedule, func.count(Schedule.id))\
            .filter(Session.startTime != None)\
            .filter(Session.schedule_id == Schedule.id)\
            .filter(Session.semester_id == Semester.id)\
            .filter(Semester.active == 1)\
            .group_by(Schedule.id).all()

    def get_session_attendance(self):
        return session.query(Schedule, func.count(Schedule.id))\
            .filter(StudentSession.sessionId == Session.id)\
            .filter(Session.semester_id == Semester.id)\
            .filter(Semester.active == 1)\
            .filter(Schedule.id == Session.schedule_id)\
            .group_by(Schedule.id).all()
