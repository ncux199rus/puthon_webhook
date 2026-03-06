from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    EXTERNAL_SERVICE_URL: str = "https://httpbin.org"  # для теста
    WEBHOOK_SECRET: str = "secret"

    FINTABLO_API_BASE: str = "https://api.fintablo.ru"
    FINTABLO_API_KEY: str = "t1.nn6aHkNHkQBgJGCC6wWFffb8VNXtZV5NK5QdF"  # возьми из профиля аккаунта

    class Config:
        env_file = ".env"


settings = Settings()
