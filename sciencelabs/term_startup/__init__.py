# Packages
from flask import render_template
from flask_classy import FlaskView, route

# Local
from sciencelabs.term_startup.term_startup_controller import TermStartupController


class TermStartupView(FlaskView):
    def __init__(self):
        self.base = TermStartupController()

    @route('/')
    def index(self):
        return render_template('term_startup/home.html')

    @route('/admin/transition/1')
    def step_one(self):
        return render_template('term_startup/step_one.html')

    @route('/admin/transition/2')
    def step_two(self):
        return render_template('term_startup/step_two.html')

    @route('/admin/transition/3')
    def step_three(self):
        return render_template('term_startup/step_three.html')

    @route('/admin/transition/4')
    def step_four(self):
        return render_template('term_startup/step_four.html')


