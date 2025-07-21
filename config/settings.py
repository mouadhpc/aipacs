# Configuration principale de l'application IA PACS
import os
from pathlib import Path
from typing import Optional
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """Configuration de l'application"""
    
    # Configuration générale
    app_name: str = "AI PACS Application"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Configuration base de données
    database_url: str = Field(
        default="postgresql://ai_pacs_user:changeme@localhost:5432/ai_pacs",
        env="DATABASE_URL"
    )
    
    # Configuration Redis
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    
    # Configuration DICOM
    dicom_ae_title: str = Field(default="IA_SERVER", env="DICOM_AE_TITLE")
    dicom_port: int = Field(default=11112, env="DICOM_PORT")
    dicom_host: str = Field(default="0.0.0.0", env="DICOM_HOST")
    
    # Configuration PACS interne
    pacs_ae_title: str = Field(default="PACS_INTERNE", env="PACS_AE_TITLE")
    pacs_host: str = Field(default="localhost", env="PACS_HOST")
    pacs_port: int = Field(default=11111, env="PACS_PORT")
    
    # Configuration API
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_prefix: str = Field(default="/api/v1", env="API_PREFIX")
    
    # Configuration sécurité
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    access_token_expire_minutes: int = Field(default=30, env="TOKEN_EXPIRE_MINUTES")
    
    # Configuration IA
    ai_model_path: str = Field(
        default="./models/ai_model.pth",
        env="AI_MODEL_PATH"
    )
    ai_confidence_threshold: float = Field(default=0.8, env="AI_CONFIDENCE_THRESHOLD")
    ai_batch_size: int = Field(default=4, env="AI_BATCH_SIZE")
    
    # Configuration stockage
    data_directory: str = Field(default="./data", env="DATA_DIRECTORY")
    temp_directory: str = Field(default="./temp", env="TEMP_DIRECTORY")
    log_directory: str = Field(default="./logs", env="LOG_DIRECTORY")
    
    # Configuration rapports
    report_template_dir: str = Field(
        default="./templates/reports",
        env="REPORT_TEMPLATE_DIR"
    )
    report_output_format: str = Field(default="DICOM_SR", env="REPORT_OUTPUT_FORMAT")  # DICOM_SR ou PDF
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Instance globale des paramètres
settings = Settings()

# Création des répertoires nécessaires
for directory in [settings.data_directory, settings.temp_directory, settings.log_directory]:
    Path(directory).mkdir(parents=True, exist_ok=True)