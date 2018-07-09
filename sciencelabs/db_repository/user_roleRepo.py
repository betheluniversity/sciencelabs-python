from sqlalchemy import *

from sciencelabs.db_repository import Base
from sciencelabs.db_repository import session


class user_role(Base):
    __tablename__ = 'user_role'
    user_id = Column(Integer, primary_key=True)
    role_id = Column(Integer)