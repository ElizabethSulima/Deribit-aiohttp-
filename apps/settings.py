from pathlib import Path

from dotenv import load_dotenv
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv()


class Config(BaseSettings):
    model_config = SettingsConfigDict(extra="allow")

    ROOT_DIR: Path = Path(__file__).parent.resolve()
    MEDIA_DIR: Path = ROOT_DIR / "media"

    # RabbitMQ
    RABBIT_USER: str = "quest"
    RABBIT_PASSWORD: str = "quest"
    RABBIT_HOST: str = "localhost"
    RABBIT_PORT: int = 6379

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # JWT token
    SECRET_KEY: str = ""
    ALGORITHM: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 0

    # DB settings
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "db"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432

    @computed_field
    def dsn(self) -> str:
        return (
            f"postgresql://{self.DB_USER}:"
            f"{self.DB_PASSWORD}@{self.DB_HOST}:"
            f"{self.DB_PORT}/{self.DB_NAME}"
        )

    @computed_field
    def rabbit_url(self) -> str:
        return (
            f"amqp://{self.RABBIT_USER}:"
            f"{self.RABBIT_PASSWORD}@{self.RABBIT_HOST}"
        )

    @computed_field
    def redis_url(self) -> str:
        return f"redis://{self.RABBIT_HOST}:{self.REDIS_PORT}/0"

    @computed_field
    def async_dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:"
            f"{self.DB_PASSWORD}@{self.DB_HOST}:"
            f"{self.DB_PORT}/{self.DB_NAME}"
        )


config = Config()
