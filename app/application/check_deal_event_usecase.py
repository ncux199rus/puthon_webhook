from typing import Dict, Any

from app.domain.ports import ExternalServicePort


class CheckDealEventUseCase:
    def __init__(self, external_service: ExternalServicePort) -> None:
        self.external_service = external_service

    async def execute(self, deal_id: str, event: str) -> Dict[str, Any]:
        deal = await self.external_service.get_deal(deal_id)

        # Ожидаем, что в ответе есть массив items, у каждого есть name
        items = deal.get("items") or []

        matched = any(
            isinstance(item, dict) and item.get("name") == event
            for item in items
        )

        return {
            "deal_id": deal_id,
            "event": event,
            "matched": matched,
            "items": items,
        }
