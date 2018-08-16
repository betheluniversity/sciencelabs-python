# Packages
from flask import render_template, request, redirect, url_for
from flask_classy import FlaskView, route

# Local
from sciencelabs.term_startup.term_startup_controller import TermStartupController
from sciencelabs.db_repository.schedule_functions import Schedule

#######################################################################################################################
# Alert stuff helps give user info on changes they make

alert = None  # Default alert to nothing


# This method get's the current alert (if there is one) and then resets alert to nothing
def get_alert():
    global alert
    alert_return = alert
    alert = None
    return alert_return


# This method sets the alert for when one is needed next
def set_alert(message_type, message):
    global alert
    alert = {
        'type': message_type,
        'message': message
    }
#######################################################################################################################


class TermStartupView(FlaskView):
    route_base = 'admin/transition/'

    def __init__(self):
        self.base = TermStartupController()
        self.schedule = Schedule()

    @route('/1/')
    def index(self):
        current_alert = get_alert()
        semester = self.schedule.get_active_semester()
        return render_template('term_startup/step_one.html', **locals())

    @route('/2')
    def step_two(self):
        current_alert = get_alert()
        return render_template('term_startup/step_two.html', **locals())

    @route('/3')
    def step_three(self):
        return render_template('term_startup/step_three.html')

    @route('/4')
    def step_four(self):
        return render_template('term_startup/step_four.html')

    @route('/set_term', methods=['post'])
    def set_term(self):
        try:
            form = request.form
            term = form.get('term')
            year = form.get('year')
            start_date = form.get('start-date')
            end_date = form.get('end-date')
            self.schedule.set_current_term(term, year, start_date, end_date)
            set_alert('success', 'Term set successfully!')
            return redirect(url_for('TermStartupView:step_two'))
        except Exception as error:
            set_alert('danger', 'Failed to set term: ' + str(error))
            return redirect(url_for('TermStartupView:index'))


