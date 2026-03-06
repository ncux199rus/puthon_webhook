from __future__ import annotations

from typing import Optional, Dict, Any
from datetime import datetime, date

from app.domain.entities import WebhookEvent, ProcessingStatus, NormalizedDeal
from app.domain.ports import ExternalServicePort, EventRepositoryPort


def parse_float(value: Any) -> float:
    if value is None:
        return 0.0
    try:
        return float(str(value).replace(" ", "").replace(",", "."))
    except ValueError:
        return 0.0


def parse_date(value: Any) -> date:
    if not value:
        raise ValueError("Дата не задана")
    s = str(value)
    return datetime.strptime(s, "%Y-%m-%d").date()  # формат 2026-02-27[web:113]


def normalize_payload(raw: Dict[str, Any]) -> NormalizedDeal:
    """
    raw:
    {
       "status": "Успешно реализовано",
       "order_number": "13560735",
       "event": "Music Cycle Festival #GALAXY САНКТ-ПЕТЕРБУРГ",
       "budget": "12000",
       "tickets": "2",
       "date": "2026-02-27"
    }
    """
    return NormalizedDeal(
        status=str(raw.get("status") or ""),
        order_number=parse_float(raw.get("order_number")),
        event=str(raw.get("event") or ""),
        budget=parse_float(raw.get("budget")),
        tickets=parse_float(raw.get("tickets")),
        date=parse_date(raw.get("date")),
    )


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
            normalized = normalize_payload(payload)

            fintablo_payload = {
                "status": normalized.status,
                "orderNumber": normalized.order_number,
                "event": normalized.event,
                "budget": normalized.budget,
                "tickets": normalized.tickets,
                "date": normalized.date.isoformat(),  # "2026-02-27"
            }

            response = await self.external_service.send_event(fintablo_payload)

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
            event = WebhookEvent(
                id=event.id,
                payload=payload,
                status=ProcessingStatus.FAILED,
            )

        if self.event_repo:
            await self.event_repo.save(event)

        return event
