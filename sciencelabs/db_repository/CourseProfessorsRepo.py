from sqlalchemy import *

from sciencelabs.db_repository import Base
from sciencelabs.db_repository import session


class CourseProfessors(Base):
    __tablename__ = 'CourseProfessors'
    course_id = Column(Integer, primary_key=True)
    professor_id = Column(Integer)
