# -*- coding: utf-8 -*-
"""
配置管理
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    model_config = {"env_file": ".env", "case_sensitive": True}
    
    # 应用配置
    APP_NAME: str = "RBAC System"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./rbac.db"
    
    # JWT配置
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS配置
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]


# 全局配置实例
settings = Settings()