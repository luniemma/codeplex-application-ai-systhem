"""
Configuration Module for Codeplex AI
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Application Configuration"""
    
    # App Settings
    APP_NAME: str = os.getenv('APP_NAME', 'Codeplex AI')
    APP_VERSION: str = os.getenv('APP_VERSION', '1.0.0')
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    ENVIRONMENT: str = os.getenv('ENVIRONMENT', 'production')
    
    # API Settings
    API_HOST: str = os.getenv('API_HOST', '0.0.0.0')
    API_PORT: int = int(os.getenv('API_PORT', 8000))
    API_WORKERS: int = int(os.getenv('API_WORKERS', 4))
    
    # AI Model Keys
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL: str = os.getenv('OPENAI_MODEL', 'gpt-4')
    OPENAI_TEMPERATURE: float = float(os.getenv('OPENAI_TEMPERATURE', 0.7))
    
    ANTHROPIC_API_KEY: str = os.getenv('ANTHROPIC_API_KEY', '')
    ANTHROPIC_MODEL: str = os.getenv('ANTHROPIC_MODEL', 'claude-3-opus')
    
    GOOGLE_API_KEY: str = os.getenv('GOOGLE_API_KEY', '')
    GOOGLE_MODEL: str = os.getenv('GOOGLE_MODEL', 'gemini-pro')
    
    # Database
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///./codeplex.db')
    REDIS_URL: str = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', 'logs/codeplex.log')
    
    # Security
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET: str = os.getenv('JWT_SECRET', 'dev-jwt-secret-change-in-production')
    CORS_ORIGINS: str = os.getenv('CORS_ORIGINS', '*')
    
    # Features
    ENABLE_CACHING: bool = os.getenv('ENABLE_CACHING', 'True').lower() == 'true'
    ENABLE_RATE_LIMITING: bool = os.getenv('ENABLE_RATE_LIMITING', 'True').lower() == 'true'
    MAX_REQUEST_SIZE: int = int(os.getenv('MAX_REQUEST_SIZE', 10485760))
    REQUEST_TIMEOUT: int = int(os.getenv('REQUEST_TIMEOUT', 30))
    
    # Analytics
    ENABLE_ANALYTICS: bool = os.getenv('ENABLE_ANALYTICS', 'True').lower() == 'true'
    ANALYTICS_BATCH_SIZE: int = int(os.getenv('ANALYTICS_BATCH_SIZE', 100))
    
    # Cache
    CACHE_TTL: int = int(os.getenv('CACHE_TTL', 3600))
    CACHE_MAX_SIZE: int = int(os.getenv('CACHE_MAX_SIZE', 1000))


# Create global config instance
config = Config()

