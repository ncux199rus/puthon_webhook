from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict
from uuid import UUID, uuid4
from datetime import date


class ProcessingStatus(Enum):
    RECEIVED = "received"
    PROCESSED = "processed"
    FAILED = "failed"


@dataclass(frozen=True)
class WebhookEvent:
    id: UUID
    payload: Dict[str, Any]
    status: ProcessingStatus = ProcessingStatus.RECEIVED

    @classmethod
    def create(cls, payload: Dict[str, Any]) -> "WebhookEvent":
        return cls(id=uuid4(), payload=payload)

@dataclass(frozen=True)
class NormalizedDeal:
    status: str
    order_number: float
    event: str
    budget: float
    tickets: float
    date: date