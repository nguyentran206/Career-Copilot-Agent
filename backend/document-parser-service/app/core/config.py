from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "document-parser-service"
    app_env: str = "development"
    app_version: str = "0.1.0"

    api_prefix: str = "/api/v1"

    host: str = "127.0.0.1"
    port: int = 8001

    allowed_extensions: str = "pdf"
    max_file_size_mb: int = 5
    min_extracted_text_length: int = 50

    enable_ocr: bool = False
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def allowed_extension_set(self) -> set[str]:
        return {
            ext.strip().lower()
            for ext in self.allowed_extensions.split(",")
            if ext.strip()
        }

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024


settings = Settings()