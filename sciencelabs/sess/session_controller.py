# Local
from sciencelabs.db_repository import Session
from sciencelabs.sciencelabs_controller import ScienceLabsController


class SessionController(ScienceLabsController):
    def __init__(self):
        super(SessionController, self).__init__()
