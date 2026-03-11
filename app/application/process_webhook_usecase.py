from __future__ import annotations
import logging

from typing import Optional, Dict, Any
from datetime import datetime, date

from app.domain.entities import WebhookEvent, ProcessingStatus, NormalizedDeal
from app.domain.ports import ExternalServicePort, EventRepositoryPort

logger = logging.getLogger(__name__)


def parse_float(value: Any) -> float:
    if value is None:
        return 0.0
    try:
        return float(str(value).replace(" ", "").replace(",", "."))
    except ValueError:
        return 0.0


def parse_date(date_str):
    # Превращаем строку в объект даты, а затем форматируем обратно в строку
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    return date_obj.strftime('%d.%m.%Y')


async def normalize_payload(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    raw:
    {
       "status": "Успешно реализовано",
       "order_number": "13560735",
       "event": "Music Cycle Festival #GALAXY САНКТ-ПЕТЕРБУРГ",
       "budget": "12000",
       "tickets": "2",
       "date": "2026-02-27"
       "event_date": "2026-02-27"
    }
    """

    # Получаем все направления
    # directions = await get_directions()
    return {
        "name": str(raw.get("status") or ""),
        "jobs": [
            {
                "id": 23343,
                "quantity": int(raw.get("tickets"))
            }],
        "directionId": 162395,
        "statusId": 86062,
        "amount": int(raw.get("budget")),
        "actDate": parse_date(raw.get("date")),
        "nds": 0
    }


class ProcessWebhookUseCase:
    def __init__(
            self,
            external_service: ExternalServicePort,
            event_repo: Optional[EventRepositoryPort] = None,
    ):
        self.external_service = external_service
        self.event_repo = event_repo

    async def execute(self, payload: Dict[str, Any]) -> WebhookEvent:
        event = WebhookEvent.create(payload)

        try:
            normalized = await normalize_payload(payload)
            eventName = payload.get("event")
            event_date = parse_date(payload.get("event_date"))
            # Получаем все направления
            fintablo_payload = normalized

            response = await self.external_service.send_event(fintablo_payload, eventName, event_date )

            logger.info(f"Response: {response}")

            event = WebhookEvent(
                id=event.id,
                payload={
                    "raw": payload,
                    "normalized": fintablo_payload,
                    "response": response,
                },
                status=ProcessingStatus.PROCESSED,
            )
        except Exception:
            logger.exception("ProcessWebhookUseCase failed", extra={"payload": payload})
            event = WebhookEvent(
                id=event.id,
                payload=payload,
                status=ProcessingStatus.FAILED,
            )

        if self.event_repo:
            await self.event_repo.save(event)

        return event
