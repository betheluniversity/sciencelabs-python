from sqlalchemy import *

from sciencelabs.db_repository import Base
from sciencelabs.db_repository import session
from sciencelabs.db_repository.SemesterRepo import Semester


class Session(Base):
    __tablename__ = 'Session'
    id = Column(Integer, primary_key=True)
    semester_id = Column(Integer)
    schedule_id = Column(Integer)
    date = Column(String)
    schedStartTime = Column(String)
    schedEndTime = Column(String)
    startTime = Column(String)
    endTime = Column(String)
    room = Column(String)
    open = Column(Integer)
    hash = Column(String)
    comments = Column(String)
    deletedAt = Column(String)
    openerId = Column(Integer)
    anonStudents = Column(Integer)
    name = Column(String)

    def get_closed_sessions(self):
        return (session.query(Session.id, Session.name, Session.date, Session.startTime, Session.endTime, Session.room).filter(Session.semester_id == Semester.id).filter(Semester.active == 1).filter(Session.startTime != None).all())