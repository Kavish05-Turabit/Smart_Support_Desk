from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    BASE: str = "Base ENV variable"
    DATABASE_URL: str
    JWT_SHA256_HASH: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "../../.env"), 
        env_file_encoding='utf-8',
        extra='ignore'
    )
    pass

settings = Settings()