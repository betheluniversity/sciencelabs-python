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
        tutor_ids = session.query(TutorSession.tutorId).filter(TutorSession.sessionId == session_id).filter(TutorSession.lead == 0)
        tutors = []
        for tutor in tutor_ids:
            tutors.append(User.get_user_by_id(self, tutor))
        return tutors

    def get_session_leads(self, session_id):
        lead_ids = session.query(TutorSession.tutorId).filter(TutorSession.sessionId == session_id).filter(TutorSession.lead == 1)
        leads = []
        for lead in lead_ids:
            leads.append(User.get_user_by_id(self, lead))
        return leads
