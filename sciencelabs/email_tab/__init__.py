# Packages
from flask import abort, render_template, request, redirect, url_for, session
from flask_classy import FlaskView, route

# Local
from sciencelabs.email_tab.email_controller import EmailController
from sciencelabs.db_repository.user_functions import User
from sciencelabs.alerts.alerts import *


class EmailView(FlaskView):
    route_base = 'email'

    def __init__(self):
        self.base = EmailController()
        self.user = User()

    @route('/create')
    def index(self):
        if 'Administrator' not in session['USER-ROLES']:
            abort(403)

        current_alert = get_alert()
        role_list = self.user.get_all_roles()
        user_list = self.user.get_all_current_users()
        return render_template('email_tab/base.html', **locals())

    @route('/confirm', methods=['post'])
    def send_email_confirm(self):
        if 'Administrator' not in session['USER-ROLES']:
            abort(403)

        form = request.form
        group_id_strings = form.getlist('groups')
        groups = []
        for group in group_id_strings:  # Need to convert strings to ints for template comparison (groups, cc, and bcc)
            groups.append(int(group))
        subject = form.get('subject')
        cc_ids = form.getlist('cc')
        cc = []
        for cc_id in cc_ids:
            cc.append(int(cc_id))
        bcc_ids = form.getlist('bcc')
        bcc = []
        for bcc_id in bcc_ids:
            bcc.append(int(bcc_id))
        message = form.get('message')
        role_list = self.user.get_all_roles()
        user_list = self.user.get_all_current_users()
        return render_template('email_tab/send_email_confirm.html', **locals())

    @route('/send', methods=['post'])
    def send(self):
        if 'Administrator' not in session['USER-ROLES']:
            abort(403)

        try:
            # TODO: actually send email
            form = request.form
            group_id_strings = form.getlist('groups')
            groups = []
            for group in group_id_strings:  # Need to convert strings to ints for template comparison (groups, cc, bcc)
                groups.append(int(group))
            cc_ids = form.getlist('cc')
            cc = []
            for cc_id in cc_ids:
                cc.append(int(cc_id))
            bcc_ids = form.getlist('bcc')
            bcc = []
            for bcc_id in bcc_ids:
                bcc.append(int(bcc_id))
            user_names = self.user.get_users_to_email(groups, cc, bcc)
            users_string = ', '.join(user_names)
            set_alert('success', 'Email sent successfully to the following users: ' + users_string)
        except Exception as error:
            set_alert('danger', 'Failed to send email: ' + str(error))
        return redirect(url_for('EmailView:index'))
