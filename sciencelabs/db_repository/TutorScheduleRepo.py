from sqlalchemy import *

from sciencelabs.db_repository import Base
from sciencelabs.db_repository import session
from sciencelabs.db_repository.UserRepo import User


class TutorSchedule(Base):
    __tablename__ = 'TutorSchedule'
    id = Column(Integer, primary_key=True)
    schedTimeIn = Column(String)
    schedTimeOut = Column(String)
    lead = Column(Integer)
    tutorId = Column(Integer)
    scheduleId = Column(Integer)

    def get_schedule_tutors(self, schedule_id):
        tutors = session.query(User, TutorSchedule).filter(TutorSchedule.scheduleId == schedule_id).filter(User.id == TutorSchedule.tutorId)
        schedule_leads = []
        schedule_tutors = []
        for user, tutor in tutors:
            if tutor.lead == 1:
                schedule_leads.append(user.firstName + ' ' + user.lastName)
            else:
                schedule_tutors.append(user.firstName + ' ' + user.lastName)
        return schedule_leads, schedule_tutors
