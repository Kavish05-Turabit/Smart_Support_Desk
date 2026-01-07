from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    BASE: str = "Base ENV variable"
    model_config = SettingsConfigDict(env_file=".env")
    pass

settings = Settings()