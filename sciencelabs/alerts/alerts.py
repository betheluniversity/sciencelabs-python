#######################################################################################################################
# Alert stuff helps give user info on changes they make
from flask import session


# This method get's the current alert (if there is one) and then resets alert to nothing
def get_alert():
    alert_return = session['ALERT']
    session['ALERT'] = None
    return alert_return


# This method sets the alert for when one is needed next
def set_alert(message_type, message):
    session['ALERT'] = {
        'type': message_type,
        'message': message
    }
#######################################################################################################################
