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
        try:
            # if a delayed alert exists, that means we don't want to show the alert on the current page
            # so we return None instead of the actual alert and keep the alert data in flask_session['ALERT'].
            # Once we go onto the new page, then DELAYED-ALERT is set to False so we display the real alert.
            #
            #
            #
            # Examples where this happens are both the "Session -> Create a Session" tab and
            # "Schedule -> Create New Schedule" tab.
            # When we hit "save" on these pages we go to either create-session/schedule-submit and then we are
            # redirected to a subsequent page where the error should be displayed. Without this logic the error is
            # displayed on the submit page which the user isn't going to see.
            # if flask_session['DELAYED-ALERT']:
            #     flask_session['DELAYED-ALERT'] = False
            #     return None
            test = 0
        except Exception as e:
            pass
        alert_return = flask_session['ALERT']
        flask_session['ALERT'] = []
        return alert_return

    # This method sets the alert for when one is needed next
    def set_alert(self, message_type, message):
        flask_session['ALERT'].append({
            'type': message_type,
            'message': message
        })

