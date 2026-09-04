from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = "development"
    DB_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/shop_api"
    DB_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/shop_api"
    ALLOWED_ORIGINS: list[str] = ["http://localhost", "http://127.0.0.1", "http://test"]
    ALLOWED_HOSTS: list[str] = ["localhost", "127.0.0.1", "test"]

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    @field_validator("ALLOWED_ORIGINS", "ALLOWED_HOSTS", mode="before")
    @classmethod
    def split_csv_list(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    def validate_security(self) -> None:
        if self.APP_ENV == "public-production":
            if not self.ALLOWED_ORIGINS:
                raise RuntimeError("ALLOWED_ORIGINS must be configured in public-production mode")
            if not self.ALLOWED_HOSTS:
                raise RuntimeError("ALLOWED_HOSTS must be configured in public-production mode")


settings = Settings()
