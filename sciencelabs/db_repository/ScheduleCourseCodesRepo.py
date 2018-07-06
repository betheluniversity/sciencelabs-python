from sqlalchemy import *

from sciencelabs.db_repository import Base
from sciencelabs.db_repository import session


class ScheduleCourseCodes(Base):
    __tablename__ = 'ScheduleCourseCodes'
    schedule_id = Column(Integer, primary_key=True)
    coursecode_id = Column(Integer)