"""
Solar API LLM Wrapper

이 모듈은 Solar API를 LangChain과 연동하기 위한
LLM 래퍼를 제공합니다.

Solar API는 Upstage에서 제공하는 한국어 성능이 우수한 LLM API입니다.
"""

import os
import logging
import json
import time
from typing import Dict, Any, Optional

# HTTP 요청을 위한 패키지
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("requests 패키지가 설치되지 않았습니다. 'pip install requests'로 설치하세요.")

from .base_llm import BaseLLM
from .config.llm_config import config

logger = logging.getLogger(__name__)


class SolarLLM(BaseLLM):
    """Solar API를 사용하는 LLM 클래스"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        # 설정에서 기본값 가져오기
        api_key = api_key or config.SOLAR_API_KEY
        model = model or config.SOLAR_MODEL
        
        if not api_key:
            raise ValueError("Solar API 키가 필요합니다. SOLAR_API_KEY 환경변수를 설정하거나 직접 전달하세요.")
        
        super().__init__(model_name=model)
        
        # Solar API 설정
        self.api_key = api_key
        self.base_url = config.SOLAR_BASE_URL
        
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests 패키지가 설치되지 않았습니다.")
    
    def generate_response(self, prompt: str) -> str:
        """프롬프트에 대한 응답을 생성합니다."""
        try:
            start_time = time.time()
            
            # Solar API 호출
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # 응답 처리
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    
                    if "choices" in response_data and len(response_data["choices"]) > 0:
                        content = response_data["choices"][0]["message"]["content"]
                        response_time = time.time() - start_time
                        
                        logger.info(f"Solar API 응답 생성 완료 (소요시간: {response_time:.2f}초)")
                        return content
                    else:
                        self.record_error()
                        return "Solar API: 응답 형식이 올바르지 않습니다."
                        
                except json.JSONDecodeError:
                    self.record_error()
                    error_msg = "Solar API: JSON 응답 파싱 실패"
                    logger.error(error_msg)
                    return error_msg
                    
            else:
                self.record_error()
                error_msg = f"Solar API 오류: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return error_msg
                
        except Exception as e:
            self.record_error()
            error_msg = f"Solar LLM 예상치 못한 오류: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def get_model_info(self) -> Dict[str, Any]:
        """모델 정보를 반환합니다."""
        return {
            "name": self.model_name,
            "type": "solar",
            "provider": "Upstage",
            "api_key_configured": bool(self.api_key),
            "base_url": self.base_url,
            "is_healthy": self.is_healthy(),
            "package_available": REQUESTS_AVAILABLE
        }
    
    def test_connection(self) -> bool:
        """Solar API 연결을 테스트합니다."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 5
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Solar API 연결 테스트 실패: {e}")
            return False
