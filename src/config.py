from pathlib import Path
from typing import Dict, Any
import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "development"
    log_level: str = "INFO"
    port: int = 8000

    supabase_url: str = ""
    supabase_key: str = ""
    supabase_db_url: str = ""

    openrouter_api_key: str = ""
    apify_api_token: str = ""

    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


class ClientConfig(BaseModel):
    id: str
    name: str
    niche: str
    raw_config: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def load_from_dir(cls, client_dir: Path) -> "ClientConfig":
        config_file = client_dir / "config.yaml"
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found at {config_file}")

        with open(config_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        client_data = data.get("client", {})
        return cls(
            id=client_data.get("id", client_dir.name),
            name=client_data.get("name", client_dir.name),
            niche=client_data.get("niche", "general"),
            raw_config=data,
        )


settings = Settings()
