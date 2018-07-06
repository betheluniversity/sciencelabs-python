from sqlalchemy import *

from sciencelabs.db_repository import Base
from sciencelabs.db_repository import session


class SessionCourses(Base):
    __tablename__ = 'SessionCourses'
    studentsession_id = Column(Integer, primary_key=True)
    course_id = Column(Integer)