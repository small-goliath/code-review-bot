from typing import Literal, Optional
from pydantic import computed_field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )
    PROJECT_NAME: str = "code-review-bot"
    
    CODE_REVIEW_TOOL: Literal["upsource", "github", "gitlab"]
    CODE_REVIEW_BASE_URL: str

    CODE_REVIEW_TOOL_ACCOUNT_USERNAME: str
    CODE_REVIEW_TOOL_ACCOUNT_PASSWORD: str

    OPENAI_API_KEYS: str
    OPENAI_MODEL: str
    REVIEW_FILES_RAW: str

    # WEBHOOK: Literal["google-chat", "slack"]
    WEBHOOK_URI: str

    @computed_field
    @property
    def REVIEW_FILES(self) -> list[str]:
        return [x.strip() for x in self.REVIEW_FILES_RAW.split(",") if x.strip()]

settings = Settings()