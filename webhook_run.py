import uvicorn
from main import app
from app.core.config import settings


def main() -> None:
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()