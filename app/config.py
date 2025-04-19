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
    
    # code review tool
    CODE_REVIEW_TOOL: Literal["upsource", "github", "gitlab"]
    UPSOURCE_BASE_URL: Optional[str] = None
    UPSOURCE_USERNAME: Optional[str] = None
    UPSOURCE_PASSWORD: Optional[str] = None

    GITLAB_BASE_URL: Optional[str] = None
    GITLAB_ACCESS_TOKEN: Optional[str] = None

    GITHUB_BASE_URL: Optional[str] = None
    GITHUB_ACCESS_TOKEN: Optional[str] = None

    # openai
    OPENAI_API_KEYS: str
    OPENAI_MODEL: str
    REVIEW_FILES_RAW: str

    # webhook
    WEBHOOK: Literal["google-chat", "slack", "discord"]
    WEBHOOK_URI: str

    @computed_field
    @property
    def REVIEW_FILES(self) -> list[str]:
        return [x.strip() for x in self.REVIEW_FILES_RAW.split(",") if x.strip()]
    
    @model_validator(mode="after")
    def validate_fields_by_code_review_tools(cls, values):
        if values.CODE_REVIEW_TOOL == "upsource":
            if not values.UPSOURCE_BASE_URL:
                raise ValueError(f"{values.CODE_REVIEW_TOOL}를 사용할 경우 UPSOURCE_BASE_URL 필수입니다.")
            if not values.UPSOURCE_USERNAME:
                raise ValueError(f"{values.CODE_REVIEW_TOOL}를 사용할 경우 UPSOURCE_USERNAME 필수입니다.")
            if not values.UPSOURCE_PASSWORD:
                raise ValueError(f"{values.CODE_REVIEW_TOOL}를 사용할 경우 UPSOURCE_PASSWORD 필수입니다.")
        elif values.CODE_REVIEW_TOOL == "gitlab":
            if not values.GITLAB_BASE_URL:
                raise ValueError(f"{values.CODE_REVIEW_TOOL}를 사용할 경우 GITLAB_BASE_URL 필수입니다.")
            if not values.GITLAB_ACCESS_TOKEN:
                raise ValueError(f"{values.CODE_REVIEW_TOOL}를 사용할 경우 GITLAB_ACCESS_TOKEN 필수입니다.")
        elif values.CODE_REVIEW_TOOL == "github":
            if not values.GITHUB_BASE_URL:
                raise ValueError(f"{values.CODE_REVIEW_TOOL}를 사용할 경우 GITHUB_BASE_URL 필수입니다.")
            if not values.GITHUB_ACCESS_TOKEN:
                raise ValueError(f"{values.CODE_REVIEW_TOOL}를 사용할 경우 GITHUB_ACCESS_TOKEN 필수입니다.")
        else:
            raise ValueError(f"{values.CODE_REVIEW_TOOL}는 지원되지 않습니다.")
        return values

settings = Settings()