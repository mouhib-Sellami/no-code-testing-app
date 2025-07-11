import os
from no_code_testing_app_server.mailing.templates.base_mail import base_mail_template

APP_FRONT_URL = os.getenv('APP_FRONT_URL', 'http://localhost')
APP_NAME = os.getenv('APP_NAME', 'Auto test builder')

content = """
<h1>Hey {{ first_name }}, Welcome to the Testing Party! 🎉</h1>
<p>Guess what? You've been handpicked to join the epic {{ organization }} squad! 🦸‍♂️ Get ready to squash bugs and make software sparkle! ✨</p>
<p style="text-align: center; margin: 24px 0;">
    <a href="{{ link }}" class="button" target="_blank" style="padding: 12px 24px; background-color: #28a745; color: white; text-decoration: none; border-radius: 5px;">Create Your Superhero Password 🛡️</a>
</p>
<p class="highlight" style="color: #ff4500; font-weight: bold;">🚨 Heads up! This link expires in 1 hour, faster than a tester spotting a UI glitch! ⏰</p>
<div class="divider" style="border-top: 1px solid #ccc; margin: 20px 0;"></div>
<p>Accidentally got this invite? No worries, just pretend it's a 404 error and ignore it. Your password's still chilling, safe and sound. 😎</p>
<p>Let's break some code together! 🤓</p>
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
    organization = kwargs['organization']['name']
    reset_link = f"{APP_FRONT_URL}/reset/password/{reset_token}"

    return {
        'FromEmail': os.environ['MAIL_JET_FROM_EMAIL'],
        'FromName': 'No code app support',
        'Subject': 'Invitation',
        'Html-part': prepare_core(first_name=first_name, link=reset_link, organization=organization),
        'Recipients': [{'Email': receiver}],
    }
