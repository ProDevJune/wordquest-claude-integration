import os
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class LLMConfig:
    """LLM 설정을 관리하는 클래스"""
    
    # Claude Code (기존)
    CLAUDE_CODE_ENABLED: bool = True
    CLAUDE_CODE_MODEL: str = "claude-3-sonnet"
    
    # OpenAI (신규)
    OPENAI_ENABLED: bool = False
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    
    # Solar (신규)
    SOLAR_ENABLED: bool = False
    SOLAR_API_KEY: Optional[str] = None
    SOLAR_MODEL: str = "solar-1-mini"
    SOLAR_BASE_URL: str = "https://api.upstage.ai/v1"
    
    def __post_init__(self):
        """환경 변수에서 설정을 로드합니다."""
        self._load_from_env()
    
    def _load_from_env(self):
        """환경 변수에서 API 키와 설정을 로드합니다."""
        # OpenAI 설정
        if os.getenv("OPENAI_API_KEY"):
            self.OPENAI_ENABLED = True
            self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        
        if os.getenv("OPENAI_MODEL"):
            self.OPENAI_MODEL = os.getenv("OPENAI_MODEL")
        
        if os.getenv("OPENAI_BASE_URL"):
            self.OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
        
        # Solar 설정
        if os.getenv("SOLAR_API_KEY"):
            self.SOLAR_ENABLED = True
            self.SOLAR_API_KEY = os.getenv("SOLAR_API_KEY")
        
        if os.getenv("SOLAR_MODEL"):
            self.SOLAR_MODEL = os.getenv("SOLAR_MODEL")
        
        if os.getenv("SOLAR_BASE_URL"):
            self.SOLAR_BASE_URL = os.getenv("SOLAR_BASE_URL")
    
    def get_available_llms(self) -> Dict[str, bool]:
        """사용 가능한 LLM 목록을 반환합니다."""
        return {
            "claude_code": self.CLAUDE_CODE_ENABLED,
            "openai": self.OPENAI_ENABLED and bool(self.OPENAI_API_KEY),
            "solar": self.SOLAR_ENABLED and bool(self.SOLAR_API_KEY)
        }
    
    def validate_config(self) -> Dict[str, str]:
        """설정 유효성을 검증하고 문제점을 반환합니다."""
        issues = {}
        
        if self.OPENAI_ENABLED and not self.OPENAI_API_KEY:
            issues["openai"] = "OPENAI_API_KEY가 설정되지 않았습니다."
        
        if self.SOLAR_ENABLED and not self.SOLAR_API_KEY:
            issues["solar"] = "SOLAR_API_KEY가 설정되지 않았습니다."
        
        return issues

# 전역 설정 인스턴스
config = LLMConfig()
