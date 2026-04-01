from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="NEURALFLOW_", env_file=".env", extra="ignore")

    host: str = "127.0.0.1"
    port: int = 7411
    log_level: str = "info"

    # One SQLite file per workspace; frontend passes active workspace path
    default_workspace_dir: str = "~/.neuralflow/workspaces/default"

    # CORS — Tauri webview origin
    cors_origins: list[str] = ["tauri://localhost", "http://localhost:1420", "http://127.0.0.1:1420"]


settings = Settings()
