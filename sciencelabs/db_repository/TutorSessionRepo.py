from sqlalchemy import *

from sciencelabs.db_repository import Base
from sciencelabs.db_repository import session
from sciencelabs.db_repository.UserRepo import User


class TutorSession(Base):
    __tablename__ = 'TutorSession'
    id = Column(Integer, primary_key=True)
    schedTimeIn = Column(String)
    schedTimeOut = Column(String)
    timeIn = Column(String)
    timeOut = Column(String)
    lead = Column(Integer)
    tutorId = Column(Integer)
    sessionId = Column(Integer)
    substitutable = Column(Integer)

    def get_session_tutors(self, session_id):
        tutors = session.query(User, TutorSession).filter(TutorSession.sessionId == session_id).filter(User.id == TutorSession.tutorId)
        session_leads = []
        session_tutors = []
        for user, tutor in tutors:
            if tutor.lead == 1:
                session_leads.append(user.firstName + ' ' + user.lastName)
            else:
                session_tutors.append(user.firstName + ' ' + user.lastName)
        return session_leads, session_tutors
