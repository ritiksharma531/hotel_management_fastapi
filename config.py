from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    JWT_ALGORITHM: str
    debug: bool = False

    class Config:
        env_file = ".env"

settings = Settings()