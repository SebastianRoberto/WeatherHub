"""
Configuración de la aplicación WeatherHub
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List
import os
import secrets


class Settings(BaseSettings):
    """Configuración de la aplicación - Solo variables sensibles desde .env"""
    
    # === CREDENCIALES Y DATOS SENSIBLES (desde .env) ===
    
    # Base de datos - URL completa con credenciales
    database_url: str
    
    # PostgreSQL Admin Configuration (para scripts de setup)
    postgres_user: str
    postgres_password: str
    postgres_host: str = "localhost"
    postgres_port: str = "5432"
    
    # OpenWeatherMap API - Credenciales
    openweather_api_key: str
    openweather_base_url: str = "https://api.openweathermap.org/data/2.5"
    
    # JWT - Clave secreta (generada automáticamente si no se proporciona)
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Generar JWT secret automáticamente si no se proporciona
        if not self.jwt_secret_key:
            self.jwt_secret_key = secrets.token_urlsafe(32)
            print("JWT secret generado automáticamente")
    
    # Server - Configuración básica
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # CORS - Orígenes permitidos (como string, se convierte a lista)
    cors_origins_str: str = "http://localhost:3000,http://localhost:5173"
    
    @property
    def cors_origins(self) -> List[str]:
        """Convierte string separado por comas en lista"""
        return [origin.strip() for origin in self.cors_origins_str.split(",")]
    
    # === CONFIGURACIÓN DE APLICACIÓN (valores por defecto) ===
    
    # ETL Configuration
    etl_batch_size: int = 10
    etl_retry_attempts: int = 3
    etl_retry_delay: int = 5
    # ETL scheduler (desde .env)
    etl_enabled: bool = False
    etl_interval_minutes: int = 60
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Instancia global de configuración
settings = Settings()
