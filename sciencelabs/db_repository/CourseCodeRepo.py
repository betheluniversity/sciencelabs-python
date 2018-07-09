from sqlalchemy import *

from sciencelabs.db_repository import Base
from sciencelabs.db_repository import session


class CourseCode(Base):
    __tablename__ = 'CourseCode'
    id = Column(Integer, primary_key=True)
    dept = Column(String)
    courseNum = Column(String)
    underived = Column(String)
    active = Column(Integer)
    courseName = Column(String)