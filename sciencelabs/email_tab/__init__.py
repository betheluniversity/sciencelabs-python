# Packages
from flask import render_template, request
from flask_classy import FlaskView, route

# Local
from sciencelabs.email_tab.email_controller import EmailController
from sciencelabs.db_repository.user_functions import User


class EmailView(FlaskView):
    route_base = 'email'

    def __init__(self):
        self.base = EmailController()
        self.user = User()

    @route('/create')
    def index(self):
        role_list = self.user.get_all_roles()
        user_list = self.user.get_all_current_users()
        return render_template('email_tab/base.html', **locals())

    @route('/confirm', methods=['post'])
    def send_email_confirm(self):
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
