from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "dev"
    database_url: str = "postgresql+psycopg://finledger:finledger@db:5432/finledger"

    jwt_secret: str = "change-me"
    jwt_alg: str = "HS256"
    jwt_expires_min: int = 30

    aws_region: str = "sa-east-1"
    aws_s3_bucket: str = "your-bucket-name"


settings = Settings()