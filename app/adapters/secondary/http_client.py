import httpx

from app.domain.ports import ExternalServicePort
from app.core.config import settings


class HttpExternalService(ExternalServicePort):
    def __init__(self) -> None:
        self.client = httpx.AsyncClient(base_url=settings.EXTERNAL_SERVICE_URL)

    async def send_event(self, payload: dict) -> dict:
        # для теста шлём на /post httpbin
        response = await self.client.post("/post", json=payload)
        response.raise_for_status()
        return response.json()
