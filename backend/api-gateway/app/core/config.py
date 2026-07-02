from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Career Copilot API Gateway"
    app_env: str = "development"
    app_version: str = "0.1.0"

    api_prefix: str = "/api/v1"

    host: str = "127.0.0.1"
    port: int = 8000

    frontend_url: str = "http://localhost:3000"

    document_parser_service_url: str = "http://127.0.0.1:8001"
    agent_service_url: str = "http://127.0.0.1:8002"

    request_timeout_seconds: int = 60

    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()