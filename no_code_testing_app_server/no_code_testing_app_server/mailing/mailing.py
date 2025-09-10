import base64
from django.conf import settings
from .templates.resetPassword.ForgetPasswordEmail import ForgetPasswordEmail
from .templates.newUser.NewUserEmail import NewUserEmail
import os

from engine_app import models
with open(settings.APP_LOGO, 'rb') as file:
    encode64 = base64.b64encode(file.read())


def generate_email(type, receiver, email_content=None, *args, **kwargs):
    mail = {}
    match(type):
        case models.MailJobs.EmailTypes.RESET_PASSWORD.value:
            mail = ForgetPasswordEmail(receiver).get_email(*args, **kwargs)
        case models.MailJobs.EmailTypes.NEW_USER.value:
            mail = NewUserEmail(receiver).get_email(*args, **kwargs)
        case models.MailJobs.EmailTypes.AUDIT.value:
            mail = {
                'FromEmail': os.environ['MAIL_JET_FROM_EMAIL'],
                'FromName': 'No code app Audit',
                'Subject': 'Web Audit',
                'Html-part': email_content,
                'Recipients': [{'Email': receiver}],
            }

    mail.update({"Inline_attachments": [{
        "ContentType": "image/png",
        "Filename": "logo.png",
        "content": str(encode64.decode())
    }]})
    return mail
