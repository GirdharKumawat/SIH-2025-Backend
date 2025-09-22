# Import necessary libraries
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

# Define the Settings class using Pydantic
class Settings(BaseSettings):
    # Environment
    environment: str

    # Database
    database_url: str
    
    # JWT
    secret_key: str
    access_token_expire_minutes: int

    # CORS
    allowed_origins: List[str]

    # Import from .env file
    model_config = SettingsConfigDict(env_file=".env")

# Create an instance of Settings
settings = Settings()
