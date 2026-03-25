from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "ai_reviewer"
    debug: bool = False
    environment: str = "development"

    host: str = "0.0.0.0"
    port: int = 8000

    database_url: str

    redis_url: str
    redis_ttl: int

    github_token: str
    github_secret: str

    claude_api_key: str
    claude_model: str = "claude-sonnet-4-6"

    cors_origins: list = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]  # to be refined with urls depending on environment
    cors_credentials: bool = True
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]

    log_level: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()
