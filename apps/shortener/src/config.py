from sqlalchemy import URL
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    base_url: str = "http://localhost:8000"
    db_user: str = "shortener_service"
    db_password: SecretStr | None = None
    db_password_file: Path | None = None
    db_host: str = "shortener-db"
    db_port: int = 5432
    db_name: str = "shortener_db"

    @property
    def normalized_base_url(self) -> str:
        return self.base_url.rstrip("/")

    @property
    def database_url(self):
        password = self._resolve_password()
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.db_user,
            password=password,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
        )

    def _resolve_password(self) -> str:
        if self.db_password_file and self.db_password_file.exists():
            return self.db_password_file.read_text().strip()
        if self.db_password:
            return self.db_password.get_secret_value()
        raise RuntimeError("No DB password provided via file or env var")


settings = Settings()
