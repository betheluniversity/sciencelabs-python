from sqlalchemy import *

from sciencelabs.db_repository import Base
from sciencelabs.db_repository import session


class Role(Base):
    __tablename__ = 'Role'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    role = Column(String)
    sort = Column(Integer)