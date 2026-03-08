import logging
import httpx

from app.domain.ports import ExternalServicePort
from app.core.config import settings

# Логгер для вывода технической информации по интеграции с Fintablo
logger = logging.getLogger(__name__)


class HttpExternalService(ExternalServicePort):
    """
    Адаптер к внешнему API Fintablo.

    Отвечает за:
    - получение списка сделок/мероприятий из Fintablo (GET /v1/deal),
    - поиск нужной записи по названию события (event),
    - вызов изменения этапа сделки (POST /v1/deal/{deal_id}/add-stage).

    Используется application-слоем через интерфейс ExternalServicePort,
    чтобы домен не зависел напрямую от httpx и конкретного API.
    """

    def __init__(self) -> None:
        """
        Инициализация HTTP‑клиента с базовым URL и заголовками авторизации.

        - base_url: URL API Fintablo из конфига (FINTABLO_API_BASE),
        - Authorization: Bearer-токен из FINTABLO_API_KEY,
        - Content-Type: всегда JSON.
        """
        self.client = httpx.AsyncClient(
            base_url=settings.FINTABLO_API_BASE,  # например: "https://api.fintablo.ru"
            headers={
                "Authorization": f"Bearer {settings.FINTABLO_API_KEY}",
                "Content-Type": "application/json",
            },
            timeout=10.0,
        )

    async def _get_all_deals(self) -> list[dict]:
        """
        Вспомогательный метод: запрашивает полный список сделок/мероприятий в Fintablo.

        Делает:
        - GET /v1/deal
        - логирует ответ (статус + тело),
        - вытаскивает поле "items" из JSON-ответа,
        - гарантирует, что вернёт список (иначе — логирует ошибку и вернёт пустой список).

        Возвращает:
            list[dict]: список объектов, каждый из которых содержит id, name, даты и пр.
        """
        logger.info("Requesting Fintablo deals list (GET /v1/deal)")

        resp = await self.client.get("/v1/deal")
        # logger.info(
        #     "Fintablo GET /v1/deal response: status=%s body=%s",
        #     resp.status_code,
        #     resp.text,
        # )
        resp.raise_for_status()

        data = resp.json()
        items = data.get("items") or []
        if not isinstance(items, list):
            # Если формат изменился или API вернул что-то неожиданное
            # logger.error("Unexpected items format in Fintablo response: %r", items)
            return []
        return items

    async def get_deal(self, deal_id: str) -> dict:
        """
        Реализация абстрактного метода порта для совместимости с доменом.

        В текущей логике:
        - переиспользует _get_all_deals(),
        - по списку items ищет объект с указанным id.

        Параметры:
            deal_id (str): идентификатор сделки (из поля "id" в items Fintablo).

        Возвращает:
            dict: найденный объект сделки или пустой dict, если не найден.
        """
        items = await self._get_all_deals()

        for item in items:
            if str(item.get("id")) == str(deal_id):
                return item

        # Если ничего не нашли — возвращаем пустой словарь
        logger.warning("Deal with id=%s not found in Fintablo items", deal_id)
        return {}

    async def send_event(self, payload: dict) -> dict:
        """
        Основной метод интеграции: двигает сделку по этапу в Fintablo
        на основании события из amoCRM.

        Ожидаемый payload (пример):
        {
          "event": "Music Cycle Festival #GALAXY САНКТ-ПЕТЕРБУРГ",
          "status": "...",
          "orderNumber": 13560735.0,
          "budget": 12000.0,
          "tickets": 2.0,
          "date": "2026-02-27"
        }

        Алгоритм:
        1. Проверяем, что в payload есть поле "event" — название события.
        2. Получаем список всех сделок/мероприятий из Fintablo через _get_all_deals().
        3. Ищем в items запись, у которой name == event (строгое совпадение).
           Пример: "Music Cycle Festival #GALAXY САНКТ-ПЕТЕРБУРГ".
        4. Берём id найденной записи как целевой deal_id (например, 1471146).
        5. Делаем POST /v1/deal/{deal_id}/add-stage с исходным payload.
        6. Логируем ответ и возвращаем JSON-ответ Fintablo (или raw-текст).

        Исключения:
        - ValueError, если нет event в payload,
        - ValueError, если по event не найден ни один item,
        - ValueError, если у найденного item нет id,
        - httpx.HTTPStatusError, если Fintablo вернул неуспешный HTTP-статус.
        """
        logger.info(
            "Sending payload to Fintablo (before resolve event): %s",
            payload,
        )

        # 1. Достаём название события из нормализованных данных
        event_name = str(payload.get("event") or "")
        if not event_name:
            logger.error("Missing event in payload: %r", payload)
            raise ValueError("event is required in payload")

        # 2. Получаем все доступные мероприятия/сделки
        items = await self._get_all_deals()

        # 3. Ищем тот, у которого name совпадает с event (по строке)
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

        # 4. Формируем URL для изменения этапа конкретной сделки
        url = f"/v1/deal/{deal_id}/add-stage"

        logger.info("Calling Fintablo add-stage: url=%s payload=%s", url, payload)

        # 5. Отправляем POST с тем же payload, который получили после нормализации
        # resp = await self.client.post(url, json=payload)
        #
        # logger.info(
        #     "Fintablo add-stage response: status=%s body=%s",
        #     resp.status_code,
        #     resp.text,
        # )
        #
        # resp.raise_for_status()

        # 6. Пытаемся распарсить JSON-ответ; если не JSON — возвращаем raw-текст
        # try:
        #     return resp.json()
        # except ValueError:
        #     return {"raw": resp.text}
