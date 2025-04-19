import base64
from django.conf import settings
from .templates.resetPassword.ForgetPasswordEmail import ForgetPasswordEmail
from engine_app import models
with open(settings.APP_LOGO, 'rb') as file:
    encode64 = base64.b64encode(file.read())


def generate_email(type, receiver, *args, **kwargs):
    mail = {}
    match(type):
        case models.MailJobs.EmailTypes.RESET_PASSWORD.value:
            mail = ForgetPasswordEmail(receiver).get_email(*args, **kwargs)

    mail.update({"Inline_attachments": [{
        "ContentType": "image/png",
        "Filename": "logo.png",
        "content": str(encode64.decode())
    }]})
    return mail
