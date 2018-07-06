from sqlalchemy import *

from sciencelabs.db_repository import Base
from sciencelabs.db_repository import session


class SessionCourseCodes(Base):
    __tablename__ = 'SessionCourseCodes'
    session_id = Column(Integer, primary_key=True)
    coursecode_id = Column(Integer)