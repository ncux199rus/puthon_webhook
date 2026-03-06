from fastapi import APIRouter, Depends, HTTPException, Request, status
from typing import Any, Dict

from app.application.process_webhook_usecase import ProcessWebhookUseCase
from app.core.config import settings
from app.core.dependencies import get_usecase

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.get("/incoming")
async def webhook_get_ping():
    return {"status": "ok"}


@router.post("/incoming")
async def receive_webhook(
    request: Request,
    usecase: ProcessWebhookUseCase = Depends(get_usecase),
):
    signature = request.headers.get("X-Webhook-Signature")

    if settings.WEBHOOK_SECRET and signature != settings.WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature",
        )

    body = await request.json()

    logger.error(f"Received webhook body: {body}")

    if not isinstance(body, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Expected JSON object with keys: status, order_number, event, budget, tickets, date",
        )

    event = await usecase.execute(body)

    return {
        "status": event.status.value,
        "event_id": str(event.id),
    }
