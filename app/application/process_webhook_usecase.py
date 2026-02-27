from __future__ import annotations

from typing import Optional

from app.domain.entities import WebhookEvent, ProcessingStatus
from app.domain.ports import ExternalServicePort, EventRepositoryPort


class ProcessWebhookUseCase:
    def __init__(
        self,
        external_service: ExternalServicePort,
        event_repo: Optional[EventRepositoryPort] = None,
    ):
        self.external_service = external_service
        self.event_repo = event_repo

    async def execute(self, payload: dict) -> WebhookEvent:
        event = WebhookEvent.create(payload)

        try:
            response = await self.external_service.send_event(payload)
            event = WebhookEvent(
                id=event.id,
                payload={**payload, "response": response},
                status=ProcessingStatus.PROCESSED,
            )
        except Exception:
            event = WebhookEvent(
                id=event.id,
                payload=payload,
                status=ProcessingStatus.FAILED,
            )

        if self.event_repo:
            await self.event_repo.save(event)

        return event
