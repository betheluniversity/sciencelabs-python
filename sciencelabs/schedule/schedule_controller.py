# Packages
from sqlalchemy import select

# Local
from sciencelabs import conn
from sciencelabs.db_repository import *
# TODO REMOVE * AND PUT IN DB CONNECTION ABOVE WHEN COMPLETING




class ScheduleController():
    def __init__(self):
        super(ScheduleController, self).__init__

    # TODO USE THIS METHOD TO FILL TABLE ON SCHEDULE
    def get_schedule_info(self):
        return []