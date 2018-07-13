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
        tutors = session.query(User.id, User.firstName, User.lastName, TutorSession.lead, TutorSession.timeIn, TutorSession.timeOut)\
            .filter(TutorSession.sessionId == session_id).filter(User.id == TutorSession.tutorId)
        session_leads = []
        session_tutors = []
        for tutor in tutors:
            if tutor.lead == 1:
                session_leads.append(tutor)
            else:
                session_tutors.append(tutor)
        return session_leads, session_tutors

    def get_tutor_session_info(self, tutor_id, session_id):
        return session.query(User.firstName, User.lastName, TutorSession.lead, TutorSession.timeIn, TutorSession.timeOut)\
            .filter(TutorSession.sessionId == session_id).filter(TutorSession.tutorId == tutor_id)\
            .filter(User.id == tutor_id).one()
