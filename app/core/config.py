"""
애플리케이션 설정 관리
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # 기본 설정
    APP_NAME: str = "WordQuest Claude Integration"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # 데이터베이스 설정 (WordQuest DB 공유)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://jayden@localhost:5432/wordquest")
    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_PORT: int = int(os.getenv("DATABASE_PORT", "5432"))
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "wordquest")
    DATABASE_USER: str = os.getenv("DATABASE_USER", "jayden")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "")
    
    # OpenAI API 설정
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    # Solar API 설정
    SOLAR_API_KEY: Optional[str] = os.getenv("SOLAR_API_KEY")
    SOLAR_MODEL: str = os.getenv("SOLAR_MODEL", "solar-mini-250422")
    SOLAR_BASE_URL: str = os.getenv("SOLAR_BASE_URL", "https://api.upstage.ai/v1")
    
    # JWT 설정
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # 보안 설정
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # 로깅 설정
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE")
    
    # 웹서버 설정
    HOST: str = os.getenv("HOST", "localhost")
    PORT: int = int(os.getenv("PORT", "9001"))
    
    # 캐시 설정
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    
    # 파일 업로드 설정
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Pydantic v2에서 extra 필드 허용

# 전역 설정 인스턴스
settings = Settings()

def get_database_url() -> str:
    """데이터베이스 URL 생성"""
    if settings.DATABASE_PASSWORD:
        return f"postgresql://{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}"
    else:
        return f"postgresql://{settings.DATABASE_USER}@{settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}"

def validate_settings() -> bool:
    """설정 유효성 검증"""
    required_vars = [
        "DATABASE_URL",
        "JWT_SECRET_KEY",
        "SECRET_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not getattr(settings, var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 필수 환경 변수가 설정되지 않았습니다: {missing_vars}")
        return False
    
    # API 키 확인
    if not settings.OPENAI_API_KEY and not settings.SOLAR_API_KEY:
        print("⚠️ OpenAI API 키 또는 Solar API 키 중 하나는 설정해야 합니다.")
    
    print("✅ 설정 검증 완료")
    return True
