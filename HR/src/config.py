from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_url: str = Field(default="postgresql://hr:hr@localhost:5432/hr", alias="DB_URL")
    public_url: str = Field(default="http://192.168.1.92:8000", alias="PUBLIC_URL")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    smtp_host: str = Field(default="smtp.yandex.ru", alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_user: str = Field(default="maximumkh@yandex.ru", alias="SMTP_USER")
    smtp_password: str = Field(default="", alias="SMTP_PASSWORD")
    email_from: str = Field(default="maximumkh@yandex.ru", alias="EMAIL_FROM")
    email_to: str = Field(default="homutov.m@gmail.com", alias="EMAIL_TO")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore", "populate_by_name": True}


settings = Settings()
