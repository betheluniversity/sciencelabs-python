from sqlalchemy import *

from sciencelabs.db_repository import Base


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
        tutors = session.query(User.firstName, User.lastName, TutorSession.lead).filter(TutorSession.sessionId == session_id).filter(User.id == TutorSession.tutorId)
        session_leads = []
        session_tutors = []
        for tutor in tutors:
            if tutor.lead == 1:
                session_leads.append(tutor.firstName + ' ' + tutor.lastName)
            else:
                session_tutors.append(tutor.firstName + ' ' + tutor.lastName)
        return session_leads, session_tutors
