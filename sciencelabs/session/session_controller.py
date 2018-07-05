# Packages
from sqlalchemy import select

# Local
from sciencelabs import conn
from sciencelabs.db_repository import session, semester
from sciencelabs.sciencelabs_controller import ScienceLabsController


class SessionController(ScienceLabsController):
    def __init__(self):
        super(SessionController, self).__init__()

    def get_closed_sessions(self):
        semester_list = conn.execute(select([semester.c.id]).where(semester.c.active == 1))
        for data in semester_list:
            active_semester = data[0]
        session_list = conn.execute(select([session]).where(session.c.semester_id == active_semester)) # TODO This will need to be updated so you can pass in a semester id
        sessions = []
        for row in session_list:
            if row[6] is None:  # startTime
                continue
            else:
                sessions.append([  # calling out individual row. Order is name, date, start, end, room
                    row[15] + ' (' + self.format_date(str(row[3])) + ')',  # name + date
                    self.format_date(str(row[3])),  # date
                    str(row[6]) + ' - ' + str(row[7]),  # startTime - endTime
                    row[8],  # room
                    'tutors',
                    'edit/delete'
                ])
        return sessions
