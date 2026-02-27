from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    EXTERNAL_SERVICE_URL: str = "https://httpbin.org"  # для теста
    WEBHOOK_SECRET: str = "secret"

    class Config:
        env_file = ".env"


settings = Settings()
