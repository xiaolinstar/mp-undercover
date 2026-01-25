from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Env
    APP_ENV: str = "dev"  # dev, test, prod

    # Flask
    SECRET_KEY: str = "default-secret-key"
    FLASK_DEBUG: bool = True
    DEBUG: bool = True
    TESTING: bool = False

    # WeChat
    WECHAT_TOKEN: str = ""
    WECHAT_APP_ID: str = ""
    WECHAT_APP_SECRET: str = ""
    ENABLE_WECHAT_PUSH: bool = False

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def __init__(self, **values):
        super().__init__(**values)
        
        # Adjust flags based on environment
        if self.APP_ENV == "prod":
            self.FLASK_DEBUG = False
            self.DEBUG = False
            self.TESTING = False
        elif self.APP_ENV == "test":
            self.TESTING = True
            # Optional: ensure debug is consistent for tests
            # self.FLASK_DEBUG = False 

settings = Settings()
