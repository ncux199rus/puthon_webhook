from abc import ABC, abstractmethod
from typing import Any, Dict

from app.domain.entities import WebhookEvent


class ExternalServicePort(ABC):
    @abstractmethod
    async def send_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        ...

    @abstractmethod
    async def get_deal(self, deal_id: str) -> Dict[str, Any]:
        ...


class EventRepositoryPort(ABC):
    @abstractmethod
    async def save(self, event: WebhookEvent) -> None:
        ...
