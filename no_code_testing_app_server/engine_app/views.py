from engine_app.engines.MailingEngine import MailingEngine
from engine_app.engines.AIEngine import AIEngine
from engine_app.engines.AIAuditEngine import AIAuditEngine

mailing_engine: MailingEngine = MailingEngine.get_instance()
ai_engine: AIEngine = AIEngine.get_instance()
ai_audit_engine: AIAuditEngine = AIAuditEngine.get_instance()
