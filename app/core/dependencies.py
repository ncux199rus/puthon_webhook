from app.adapters.secondary.http_client import HttpExternalService
from app.application.process_webhook_usecase import ProcessWebhookUseCase


def get_usecase() -> ProcessWebhookUseCase:
    external_service = HttpExternalService()
    return ProcessWebhookUseCase(external_service)
