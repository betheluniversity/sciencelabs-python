from sciencelabs.db_repository import session
from sciencelabs.db_repository.db_tables import Session, Semester, User, TutorSession


class SessionFunctions:

    def get_closed_sessions(self):
        return (session.query(Session.id, Session.name, Session.date, Session.startTime, Session.endTime, Session.room)
                .filter(Session.semester_id == Semester.id).filter(Semester.active == 1)
                .filter(Session.startTime != None).all())

    def get_session(self, session_id):
        return session.query(Session).filter(Session.id == session_id).one()

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
