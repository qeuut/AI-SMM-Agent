from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    BOT_TOKEN: str
    PROXY_API_KEY: str
    ADMIN_TELEGRAM_IDS: str = ""
    REDIS_URL: str = "redis://localhost:6379/0"
    N8N_WEBHOOK_URL: str
    CHANNEL_ID: str

    @property
    def admin_ids(self) -> list[int]:
        if not self.ADMIN_TELEGRAM_IDS:
            return []
        return [int(x.strip()) for x in self.ADMIN_TELEGRAM_IDS.split(",") if x.strip()]

settings = Settings()