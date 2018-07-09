from sqlalchemy import *

from sciencelabs.db_repository import Base


class TutorSession(Base):
    __tablename__ = 'TutorSession'
    id = Column(Integer, primary_key=True)
    schedTimeIn = Column(String)
    schedTimeOut = Column(String)
    timeIn = Column(String)
    timeOut = Column(String)
    lead = Column(Integer)
    tutorId = Column(Integer)
    sessionId = Column(Integer)
    substitutable = Column(Integer)
