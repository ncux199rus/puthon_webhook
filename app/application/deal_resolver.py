from typing import List, Dict, Any
from datetime import date
import logging

logger = logging.getLogger(__name__)


class DealResolver:
    """
    Сервис прикладного уровня для поиска deal_id по названию события (event)
    среди items, полученных из Fintablo.
    """

    @staticmethod
    def resolve_deal_id_by_event(event_name: str, event_date: str, items: List[Dict[str, Any]]) -> int:
        """
        Ищет в списке items первую запись, где name == event_name.

        Возвращает:
            int: найденный id.

        Исключает:
            ValueError: если не найдено совпадение или нет id у найденного элемента.
        """
        event_date_str = event_date.strftime("%d.%m.%Y")
        matched_item = next(
            (
                item
                for item in items
                if isinstance(item, dict)
                and str(item.get("name") or "").strip() == event_name.strip()
                and str(item.get("actDate") or "").strip() == event_date_str
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
            "Resolved Fintablo deal id by event: event=%r -> id=%r",
            event_name,
            deal_id,
        )

        return int(deal_id)
