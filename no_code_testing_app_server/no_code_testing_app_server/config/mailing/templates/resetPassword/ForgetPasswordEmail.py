from no_code_testing_app_server.config.mail_jet_config import Email
from no_code_testing_app_server.config.mailing.templates.resetPassword import forgetPassword


class ForgetPasswordEmail(Email):

    def get_email(self, *args, **kwargs):
        return forgetPassword.get_email(receiver=self.receiver_email, *args, **kwargs)
