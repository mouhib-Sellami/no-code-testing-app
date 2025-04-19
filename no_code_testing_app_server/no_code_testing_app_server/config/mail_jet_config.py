import os
from mailjet_rest import Client
from no_code_testing_app_server.config.singleton_config.Singleton import singleton
from abc import ABC, abstractmethod


class Email(ABC):
    def __init__(self, receiver_email) -> None:
        self.receiver_email = receiver_email
        self.sender = os.getenv("MAIL_JET_FROM_EMAIL")

    @abstractmethod
    def get_email(self,*arg,**kwargs):
        pass


@singleton
class MailJet:
    def __init__(self, *args, **kwargs):
        api_key = os.environ['MAIL_JET_API_KEY']
        api_secret = os.environ['MAIL_JET_SECRET_KEY']
        self.MAIL_JET_CLIENT = Client(auth=(api_key, api_secret))

    def send_email(self, payload):
        MAIL_DATA_TEMPLATE = payload
        result = self.MAIL_JET_CLIENT.send.create(
            data=MAIL_DATA_TEMPLATE)
        if not result.status_code == 200:
            raise (Exception(
                f"mail on task {payload.__dict__} failed with status {result.status_code}"))
