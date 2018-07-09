from sqlalchemy import *

from sciencelabs.db_repository import Base
from sciencelabs.db_repository import session


class StudentSession(Base):
    __tablename__ = 'StudentSession'
    id = Column(Integer, primary_key=True)
    timeIn = Column(String)
    timeOut = Column(String)
    studentId = Column(Integer)
    sessionId = Column(Integer)
    otherCourse = Column(Integer)
    otherCourseName = Column(String)