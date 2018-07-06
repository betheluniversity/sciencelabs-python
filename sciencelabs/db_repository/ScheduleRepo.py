from sqlalchemy import *

from sciencelabs.db_repository import Base
from sciencelabs.db_repository import session
from sciencelabs.db_repository.SemesterRepo import Semester
from sciencelabs.db_repository.SessionRepo import Session


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

    def get_report_term_info(self):
        return session.query(Schedule.name, Schedule.dayofWeek, Schedule.startTime, Schedule.endTime, Schedule.room).filter(Schedule.id == Session.schedule_id).filter(Session.semester_id == Semester.id).filter(Semester.active == 1).all()