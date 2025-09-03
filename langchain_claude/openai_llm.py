"""
OpenAI API LLM Wrapper

이 모듈은 OpenAI API를 LangChain과 연동하기 위한
LLM 래퍼를 제공합니다.
"""

import os
import logging
from typing import Dict, Any, Optional
import time

# OpenAI 패키지 import
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("OpenAI 패키지가 설치되지 않았습니다. 'pip install openai'로 설치하세요.")

from .base_llm import BaseLLM
from .config.llm_config import config

logger = logging.getLogger(__name__)


class OpenAILLM(BaseLLM):
    """OpenAI API를 사용하는 LLM 클래스"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        # 설정에서 기본값 가져오기
        api_key = api_key or config.OPENAI_API_KEY
        model = model or config.OPENAI_MODEL
        
        if not api_key:
            raise ValueError("OpenAI API 키가 필요합니다. OPENAI_API_KEY 환경변수를 설정하거나 직접 전달하세요.")
        
        super().__init__(model_name=model)
        
        # OpenAI 클라이언트 초기화
        if OPENAI_AVAILABLE:
            self.client = openai.OpenAI(api_key=api_key)
            self.api_key = api_key
            self.base_url = config.OPENAI_BASE_URL
            
            # 클라이언트 설정
            if hasattr(self.client, 'base_url'):
                self.client.base_url = self.base_url
        else:
            raise ImportError("OpenAI 패키지가 설치되지 않았습니다.")
    
    def generate_response(self, prompt: str) -> str:
        """프롬프트에 대한 응답을 생성합니다."""
        try:
            start_time = time.time()
            
            # OpenAI API 호출
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            # 응답 추출
            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                response_time = time.time() - start_time
                
                logger.info(f"OpenAI 응답 생성 완료 (소요시간: {response_time:.2f}초)")
                return content
            else:
                self.record_error()
                return "OpenAI API: 응답이 비어있습니다."
                
        except Exception as e:
            self.record_error()
            error_msg = f"OpenAI LLM 예상치 못한 오류: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def get_model_info(self) -> Dict[str, Any]:
        """모델 정보를 반환합니다."""
        return {
            "name": self.model_name,
            "type": "openai",
            "provider": "OpenAI",
            "api_key_configured": bool(self.api_key),
            "base_url": self.base_url,
            "is_healthy": self.is_healthy(),
            "package_available": OPENAI_AVAILABLE
        }
    
    def test_connection(self) -> bool:
        """OpenAI API 연결을 테스트합니다."""
        try:
            # 간단한 테스트 요청
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            logger.error(f"OpenAI 연결 테스트 실패: {e}")
            return False
