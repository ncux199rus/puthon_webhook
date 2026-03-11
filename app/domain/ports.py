from abc import ABC, abstractmethod
from typing import Any, Dict, List

from app.domain.entities import WebhookEvent


class ExternalServicePort(ABC):
    @abstractmethod
    async def send_event(self, payload: Dict[str, Any], event: str, event_date:str) -> Dict[str, Any]:
        ...

    @abstractmethod
    async def get_deal(self, deal_id: str) -> Dict[str, Any]:
        ...

    @abstractmethod
    async def get_directions(self) -> List[Dict[str, Any]]:
        ...


class EventRepositoryPort(ABC):
    @abstractmethod
    async def save(self, event: WebhookEvent) -> None:
        ...
