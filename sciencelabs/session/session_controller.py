# Packages
from sqlalchemy import select

# Local
from sciencelabs import conn
from sciencelabs.db_repository import session


class SessionController:
    def __init__(self):
        super(SessionController, self).__init__

    def get_closed_sessions(self):
        session_list = conn.execute(select([session]).where(session.c.semester_id == 40013)) # TODO This will need to be updated so you can pass in a semester id
        sessions = []
        for row in session_list:
            sessions.append([  # calling out individual row. Order is name, date, start, end, room
                row[15],
                row[3],
                str(row[6]) + ' - ' + str(row[7]),
                row[8]
            ])
        return sessions
