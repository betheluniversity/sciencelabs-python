from sqlalchemy import *

from sciencelabs.db_repository import Base
from sciencelabs.db_repository import session


class TutorSchedule(Base):
    __tablename__ = 'TutorSchedule'
    id = Column(Integer, primary_key=True)
    schedTimeIn = Column(String)
    schedTimeOut = Column(String)
    lead = Column(Integer)
    tutorId = Column(Integer)
    scheduleId = Column(Integer)