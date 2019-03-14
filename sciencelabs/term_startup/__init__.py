# Packages
from flask import render_template, request, redirect, url_for, session as flask_session
from flask_classy import FlaskView, route

# Local
from sciencelabs.db_repository.schedule_functions import Schedule
from sciencelabs.db_repository.user_functions import User
from sciencelabs.sciencelabs_controller import ScienceLabsController


class TermStartupView(FlaskView):
    route_base = 'admin/transition/'

    def __init__(self):
        self.schedule = Schedule()
        self.slc = ScienceLabsController()
        self.user = User()

    @route('/1/')
    def index(self):
        self.slc.check_roles_and_route(['Administrator'])

        semester = self.schedule.get_active_semester()
        return render_template('term_startup/step_one.html', **locals())

    @route('/2')
    def step_two(self):
        self.slc.check_roles_and_route(['Administrator'])

        return render_template('term_startup/step_two.html', **locals())

    @route('/3')
    def step_three(self):
        self.slc.check_roles_and_route(['Administrator'])

        return render_template('term_startup/step_three.html')

    @route('/4')
    def step_four(self):
        self.slc.check_roles_and_route(['Administrator'])

        return render_template('term_startup/step_four.html')

    @route('/set-term', methods=['post'])
    def set_term(self):
        self.slc.check_roles_and_route(['Administrator'])
        form = request.form
        term = form.get('term')
        year = form.get('year')
        start_date = form.get('start-date')
        end_date = form.get('end-date')

        try:
            self.schedule.set_current_term(term, year, start_date, end_date)  # Sets the new term to active
            self.user.deactivate_students()  # Soft deletes all students
            self.user.demote_tutors()  # Demotes all lead tutors to regular tutors
            # self.user.populate_courses_cron()  # Pulls in new courses and profs from banner
            semester = Schedule().get_active_semester()
            flask_session['SEMESTER-LIST'] = \
                [{'id': semester.id, 'term': semester.term, 'year': semester.year, 'active': semester.active}] + \
                flask_session['SEMESTER-LIST']
            flask_session['SELECTED-SEMESTER'] = semester.id
            self.slc.set_alert('success', 'Term set successfully!')
            return redirect(url_for('TermStartupView:step_two'))
        except Exception as error:
            self.slc.set_alert('danger', 'Failed to set term: ' + str(error))
            return redirect(url_for('TermStartupView:index'))
