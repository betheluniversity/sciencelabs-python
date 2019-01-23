import socket
from flask_mail import Mail, Message
from sciencelabs import app


class EmailController():
    def __init__(self):
        super(EmailController, self).__init__()

    def send_message(self, subject, body, recipients, bcc, html=False):
        if app.config['ENVIRON'] != 'prod':
            print('Would have sent email to: ' + str(recipients))
            recipients = app.config['TEST_EMAILS']
        mail = Mail(app)
        msg = Message(subject=subject,
                      sender='noreply@bethel.edu',
                      recipients=recipients,
                      bcc=bcc)
        if html:
            msg.html = body
        else:
            msg.body = body
        try:
            mail.send(msg)
        except socket.error:
            print("Failed to send message: {}".format(body))
            return False
        return True
