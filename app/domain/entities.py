from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict
from uuid import UUID, uuid4


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
