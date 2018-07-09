from sqlalchemy import *

from sciencelabs.db_repository import Base
from sciencelabs.db_repository import session


class CourseViewer(Base):
    __tablename__ = 'CourseViewer'
    course_id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
