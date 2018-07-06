from sqlalchemy import *

from sciencelabs.db_repository import Base
from sciencelabs.db_repository import session


class Semester(Base):
    __tablename__ = 'Semester'
    id = Column(Integer, primary_key=True)
    term = Column(String)
    startDate = Column(String)
    endDate = Column(String)
    year = Column(Integer)
    active = Column(Integer)