from app.adapters.secondary.http_client import HttpExternalService
from app.application.process_webhook_usecase import ProcessWebhookUseCase
from app.application.check_deal_event_usecase import CheckDealEventUseCase


def get_usecase() -> ProcessWebhookUseCase:
    external_service = HttpExternalService()
    return ProcessWebhookUseCase(external_service)

def get_check_deal_event_usecase() -> CheckDealEventUseCase:
    external_service = HttpExternalService()
    return CheckDealEventUseCase(external_service)