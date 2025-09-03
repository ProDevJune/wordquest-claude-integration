from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BaseLLM(ABC):
    """모든 LLM이 구현해야 할 공통 인터페이스"""
    
    def __init__(self, model_name: str = "default"):
        self.model_name = model_name
        self.is_available = True
        self.error_count = 0
        self.max_retries = 3
    
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """프롬프트에 대한 응답을 생성합니다."""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """모델 정보를 반환합니다."""
        pass
    
    def is_healthy(self) -> bool:
        """LLM이 정상 작동하는지 확인합니다."""
        return self.is_available and self.error_count < self.max_retries
    
    def record_error(self):
        """에러 발생을 기록합니다."""
        self.error_count += 1
        if self.error_count >= self.max_retries:
            self.is_available = False
            logger.warning(f"{self.model_name} LLM이 비활성화되었습니다.")
    
    def reset_errors(self):
        """에러 카운트를 리셋합니다."""
        self.error_count = 0
        self.is_available = True
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model_name})"
    
    def __repr__(self) -> str:
        return self.__str__()
