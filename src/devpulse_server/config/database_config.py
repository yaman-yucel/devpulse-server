from pydantic_settings import BaseSettings
from pydantic import Field

class DatabaseSettings(BaseSettings):
    """Configuration settings for the application."""
    
    database_url: str = Field(default="postgresql+asyncpg://afaruk:158158158@localhost:5452/last_tracker_db", description="Database connection URL") 
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        
db_settings = DatabaseSettings()