import logging
import httpx

from app.domain.ports import ExternalServicePort
from app.core.config import settings

logger = logging.getLogger(__name__)


class HttpExternalService(ExternalServicePort):
    def __init__(self) -> None:
        self.client = httpx.AsyncClient(
            base_url=settings.FINTABLO_API_BASE,  # "https://api.fintablo.ru"
            headers={
                "Authorization": f"Bearer {settings.FINTABLO_API_KEY}",
                "Content-Type": "application/json",
            },
            timeout=10.0,
        )

    async def _get_all_deals(self) -> list[dict]:
        logger.info("Requesting Fintablo deals list (GET /v1/deal)")

        resp = await self.client.get("/v1/deal")
        logger.info(
            "Fintablo GET /v1/deal response: status=%s body=%s",
            resp.status_code,
            resp.text,
        )
        resp.raise_for_status()

        data = resp.json()
        items = data.get("items") or []
        if not isinstance(items, list):
            logger.error("Unexpected items format in Fintablo response: %r", items)
            return []
        return items

    async def get_deal(self, deal_id: str) -> dict:
        """
        Формальная реализация абстрактного метода.
        Здесь можно либо вернуть все сделки, либо конкретную,
        но для текущей логики нам важнее _get_all_deals().
        """
        items = await self._get_all_deals()
        # Пример: ищем по id, если это вообще нужно
        for item in items:
            if str(item.get("id")) == str(deal_id):
                return item
        return {}

    async def send_event(self, payload: dict) -> dict:
        logger.info("Sending payload to Fintablo (before resolve event): %s", payload)

        event_name = str(payload.get("event") or "")
        if not event_name:
            logger.error("Missing event in payload: %r", payload)
            raise ValueError("event is required in payload")

        items = await self._get_all_deals()

        matched_item = next(
            (
                item
                for item in items
                if isinstance(item, dict)
                and str(item.get("name") or "").strip() == event_name.strip()
            ),
            None,
        )

        if not matched_item:
            logger.error(
                "No matching item found in Fintablo for event=%r; items count=%d",
                event_name,
                len(items),
            )
            raise ValueError("No matching deal item found for event")

        deal_id = matched_item.get("id")
        if deal_id is None:
            logger.error("Matched item has no id: %r", matched_item)
            raise ValueError("Matched item has no id")

        logger.info(
            "Matched event to Fintablo deal item: event=%r -> id=%r",
            event_name,
            deal_id,
        )

        url = f"/v1/deal/{deal_id}/add-stage"

        logger.info("Calling Fintablo add-stage: url=%s payload=%s", url, payload)

        resp = await self.client.post(url, json=payload)

        logger.info(
            "Fintablo add-stage response: status=%s body=%s",
            resp.status_code,
            resp.text,
        )

        resp.raise_for_status()
        try:
            return resp.json()
        except ValueError:
            return {"raw": resp.text}
