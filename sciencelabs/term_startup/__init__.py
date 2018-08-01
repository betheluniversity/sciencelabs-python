# Packages
from flask import render_template, request
from flask_classy import FlaskView, route

# Local
from sciencelabs.term_startup.term_startup_controller import TermStartupController
from sciencelabs.db_repository.schedule_functions import Schedule


class TermStartupView(FlaskView):
    route_base = 'admin/transition/'

    def __init__(self):
        self.base = TermStartupController()
        self.schedule = Schedule()

    @route('/1/')
    def index(self):
        semester = self.schedule.get_active_semester()

        return render_template('term_startup/step_one.html', **locals())

    @route('/2')
    def step_two(self):
        return render_template('term_startup/step_two.html')

    @route('/3')
    def step_three(self):
        return render_template('term_startup/step_three.html')

    @route('/4')
    def step_four(self):
        return render_template('term_startup/step_four.html')

    @route('/set_term', methods=['post'])
    def set_term(self):
        form = request.form
        term = form.get('term')
        # TODO: Set term
        return 'success'


