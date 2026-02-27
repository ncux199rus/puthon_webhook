"""
main.py — Entry point для uvicorn main:app
Стандарт FastAPI структура: main.py в корне + app/ пакет
"""
from fastapi import FastAPI
from app.presentation.webhook_handler import router  # После фикса импортов

app = FastAPI(
    title="Webhook Processor",
    description="Чистая архитектура DDD FastAPI для webhook → process → external service",
    version="1.0.0"
)

app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Webhook processor ready", "status": "ok"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8007,
        reload=True,
        log_level="info"
    )
