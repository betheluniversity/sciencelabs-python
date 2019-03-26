import random
import string

from flask import abort
from flask import session as flask_session


class ScienceLabsController(object):
    def __init__(self):
        pass

    # I found this code on StackExchange. It generates a random 13 character string with 0-9, A-Z, a-z
    # This code is only valid in Python 3.6.2 or higher (currently on 3.6.5)
    def get_hash(self):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=13))

    def check_roles_and_route(self, allowed_roles):
        for role in allowed_roles:
            if role in flask_session['USER-ROLES']:
                return True
        abort(403)

    # This method get's the current alert (if there is one) and then resets alert to nothing
    def get_alert(self):
        alert_return = flask_session['ALERT']
        flask_session['ALERT'] = None
        return alert_return

    # This method sets the alert for when one is needed next
    def set_alert(self, message_type, message):
        flask_session['ALERT'] = {
            'type': message_type,
            'message': message
        }

    def set_second_alert(self, message_type, message):
        flask_session['ALERT_2'] = {
            'type': message_type,
            'message': message
        }

    def get_second_alert(self):
        alert_return = flask_session['ALERT_2']
        flask_session['ALERT_2'] = None
        return alert_return
