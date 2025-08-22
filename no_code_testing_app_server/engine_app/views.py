from engine_app.engines.MailingEngine import MailingEngine
from engine_app.engines.AIEngine import AIEngine

mailing_engine: MailingEngine = MailingEngine.get_instance()
ai_engine: AIEngine = AIEngine.get_instance()
