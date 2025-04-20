import os
from no_code_testing_app_server.config.mailing.templates.base_mail import base_mail_template

APP_FRONT_URL = os.getenv('APP_FRONT_URL', 'http://localhost')
APP_NAME = os.getenv('APP_NAME', 'Auto test builder')

content = """
<h1>Hello {{ first_name }}!</h1>
<p>A password reset request was made for your account. If this was you, click the button below to reset your password.</p>
<p style="text-align: center; margin: 24px 0;">
    <a href="{{ link }}" class="button" target="_blank">Reset Password</a>
</p>
<p class="highlight">This link will expire in 1 hour for security reasons.</p>
<div class="divider"></div>
<p>If you didn't request this, you can safely ignore this email. Your password remains unchanged until you use the link above.</p>
"""


def prepare_core(**kwargs):

    formatted_body = content
    for key, value in kwargs.items():
        formatted_body = formatted_body.replace(f"{{{{ {key} }}}}", str(value))

    formatted_email = base_mail_template.replace(
        "{% block content %}{% endblock %}", formatted_body)
    formatted_email = formatted_email.replace(
        "{{ APP_FRONT_URL }}", APP_FRONT_URL)
    formatted_email = formatted_email.replace("{{ APP_NAME }}", APP_NAME)

    return formatted_email


def get_email(receiver, *args, **kwargs):
    first_name = kwargs['first_name']
    reset_token = kwargs['reset_token']
    reset_link = f"{APP_FRONT_URL}/reset/password/{reset_token}"

    return {
        'FromEmail': os.environ['MAIL_JET_FROM_EMAIL'],
        'FromName': 'No code app support',
        'Subject': 'Reset password',
        'Html-part': prepare_core(first_name=first_name, link=reset_link),
        'Recipients': [{'Email': receiver}],
    }
