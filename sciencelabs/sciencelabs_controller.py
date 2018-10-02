from flask import session, abort

import random
import string


class ScienceLabsController(object):
    def __init__(self):
        pass

    # I found this code on StackExchange. It generates a random 13 character string with 0-9, A-Z, a-z
    # This code is only valid in Python 3.6.2 or higher (currently on 3.6.5)
    def get_hash(self):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=13))

    def check_roles_and_route(self, allowed_roles):
        count = 0
        for role in allowed_roles:
            if role in session['USER-ROLES']:
                return
        abort(403)

