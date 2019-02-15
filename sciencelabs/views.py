from datetime import datetime
import json

# Packages
from flask import render_template, make_response, redirect, request
from flask import session as flask_session
from flask_classy import FlaskView, route

from sciencelabs import app
from sciencelabs.sciencelabs_controller import ScienceLabsController


class View(FlaskView):
    def __init__(self):
        self.slc = ScienceLabsController()

    def index(self):
        return render_template('index.html', **locals())

    @route("/logout", methods=["GET"])
    def logout(self):
        flask_session.clear()
        resp = make_response(redirect(app.config['LOGOUT_URL']))
        resp.set_cookie('MOD_AUTH_CAS_S', '', expires=datetime.now()+1)
        resp.set_cookie('MOD_AUTH_CAS', '', expires=datetime.now()+1)
        return resp

    @route("/set-semester", methods=["POST"])
    def set_semester_selector(self):
        semester_id = int(json.loads(request.data).get('id'))
        # Makes sure that semester_id is valid (always should be but just in case)
        try:
            # Sets the attribute 'active' of all the semesters to 0 so none are active
            for semester in flask_session['SEMESTER-LIST']:
                if semester['id'] == semester_id:
                    semester['active'] = 1  # activates the semester chosen
                    self.slc.set_alert('success', 'Successfully set semester to ' + semester['term'] + ' ' +
                                       str(semester['year']))
                else:
                    semester['active'] = 0  # deactivates all others
            # Sets the SELECTED-SEMESTER
            flask_session['SELECTED-SEMESTER'] = int(semester_id)
            return 'success'
        except Exception as error:
            self.slc.set_alert('danger', 'Failed to change semester: ' + str(error))
            return error
