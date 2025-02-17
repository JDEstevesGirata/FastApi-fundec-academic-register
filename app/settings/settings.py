"""Setup"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """Configuración de la aplicación usando variables de entorno."""

    MONGO_URI: str = Field(default="mongodb://localhost:27017", validation_alias="MONGO_URI")
    MONGO_DB: str = Field(default="mi_base_de_datos", validation_alias="MONGO_DB")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
