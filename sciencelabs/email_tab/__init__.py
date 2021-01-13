# Packages
from flask import render_template, request, redirect, url_for
from flask_classy import FlaskView, route

# Local
from sciencelabs.email_tab.email_controller import EmailController
from sciencelabs.db_repository.user_functions import User
from sciencelabs.sciencelabs_controller import ScienceLabsController
from sciencelabs import app


class EmailView(FlaskView):
    route_base = 'email'

    def __init__(self):
        self.base = EmailController()
        self.user = User()
        self.slc = ScienceLabsController()

    @route('/create')
    def index(self):
        self.slc.check_roles_and_route(['Administrator'])

        role_list = self.user.get_all_roles()
        user_list = self.user.get_all_current_users()
        return render_template('email_tab/base.html', **locals())

    @route('/')
    def email_redirect(self):
        return redirect(url_for('EmailView:index'))

    @route('/confirm-email', methods=['post'])
    def send_email_confirm(self):
        self.slc.check_roles_and_route(['Administrator'])
        data = request.get_json()

        subject = data['subject']
        message = data['message']
        group_id_strings = data['selected_recipients']
        cc_ids = data['selected_cc']
        bcc_ids = data['selected_bcc']

        groups = []
        for group in group_id_strings:  # Need to convert strings to ints for template comparison (groups, cc, and bcc)
            groups.append(int(group))
        cc = []
        for cc_id in cc_ids:
            cc.append(int(cc_id))
        bcc = []
        for bcc_id in bcc_ids:
            bcc.append(int(bcc_id))

        recipients = self.user.get_recipient_emails(cc)
        bcc_emails = self.user.get_bcc_emails(groups, bcc)

        return render_template('email_tab/email_confirm_modal.html', **locals())

    @route('/send', methods=['post'])
    def send(self):
        self.slc.check_roles_and_route(['Administrator'])

        data = request.get_json()
        subject = data['subject']
        message = data['message']
        recipients = data['recipients']
        bcc = data['bcc']

        success = self.base.send_message(subject, message, recipients, bcc, False)
        if success:
            self.slc.set_alert('success', 'Email sent successfully')
        else:
            self.slc.set_alert('danger', 'Failed to send email')
        return 'success'
