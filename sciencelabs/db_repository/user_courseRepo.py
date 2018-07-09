from sqlalchemy import *

from sciencelabs.db_repository import Base
from sciencelabs.db_repository import session


class user_course(Base):
    __tablename__ = 'user_course'
    user_id = Column(Integer, primary_key=True)
    course_id = Column(Integer)