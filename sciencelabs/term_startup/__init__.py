# Packages
from flask import render_template
from flask_classy import FlaskView, route

# Local
from sciencelabs.term_startup.term_startup_controller import TermStartupController


class TermStartupView(FlaskView):
    route_base = 'admin/transition/'

    def __init__(self):
        self.base = TermStartupController()

    @route('/1/')
    def index(self):
        return render_template('term_startup/step_one.html')

    @route('/2')
    def step_two(self):
        return render_template('term_startup/step_two.html')

    @route('/3')
    def step_three(self):
        return render_template('term_startup/step_three.html')

    @route('/4')
    def step_four(self):
        return render_template('term_startup/step_four.html')


