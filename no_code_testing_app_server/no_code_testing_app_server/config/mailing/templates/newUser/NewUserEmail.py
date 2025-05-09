from no_code_testing_app_server.config.mail_jet_config import Email
from no_code_testing_app_server.config.mailing.templates.newUser import newUser


class NewUserEmail(Email):

    def get_email(self, *args, **kwargs):
        print(newUser.get_email(receiver=self.receiver_email, *args, **kwargs))
        return newUser.get_email(receiver=self.receiver_email, *args, **kwargs)
