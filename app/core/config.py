from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    WEBHOOK_SECRET: str
    FINTABLO_API_BASE: str
    FINTABLO_API_KEY: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()