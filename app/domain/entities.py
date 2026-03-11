from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict
from uuid import UUID, uuid4
from datetime import date


class ProcessingStatus(Enum):
    RECEIVED = "received"
    PROCESSED = "processed"
    FAILED = "failed"

class JobItem(TypedDict):
    """
    Элемент массива jobs в ответе Fintablo:
    {
        "id": int,
        "quantity": int
    }
    """
    id: int
    quantity: int


class GoodItem(TypedDict):
    """
    Элемент массива goods в ответе Fintablo:
    {
        "id": int,
        "quantity": int
    }
    """
    id: int
    quantity: int


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
    name: str
    jobs: List[JobItem]
    directionId: int
    statusId:int
    amount:int
    actDate: date
    nds: int


class DealItem(TypedDict, total=False):
    """
    Описание одной сделки/мероприятия из items Fintablo.

    Пример структуры:
    {
        "id": int,
        "name": string,
        "jobs": [JobItem, ...],
        "goods": [GoodItem, ...],
        "directionId": int,
        "amount": int,
        "currency": string,
        "customCostPrice": int | null,
        "statusId": int,
        "partnerId": int | null,
        "responsibleId": int | null,
        "comment": string,
        "startDate": string (дата "DD.MM.YYYY"),
        "endDate": string | null,
        "actDate": string | null,
        "nds": int | null
    }
    """
    id: int
    name: str
    jobs: List[JobItem]
    goods: List[GoodItem]
    directionId: int
    amount: int
    currency: str
    customCostPrice: Optional[int]
    statusId: int
    partnerId: Optional[int]
    responsibleId: Optional[int]
    comment: str
    startDate: str
    endDate: Optional[str]
    actDate: Optional[str]
    nds: Optional[int]