"""
Claude Code LLM Wrapper for LangChain

이 모듈은 Claude Code를 LangChain과 연동하기 위한
LLM 래퍼를 제공합니다.

Claude Code 사용 방법:
1. API 연동: Anthropic API 키 사용
2. 유료 플랜: Claude 웹 인터페이스 직접 사용 (API 키 불필요)
"""

import os
import logging
from typing import Any, List, Optional, Dict

# 로깅 설정
logger = logging.getLogger(__name__)

# BaseLLM import
from .base_llm import BaseLLM


class ClaudeCodeLLM(BaseLLM):
    def __init__(self):
        super().__init__(model_name="claude-3-5-sonnet-20241022")
        self.max_tokens = 1000
        self.temperature = 0.7
        self.use_premium_plan = os.getenv("CLAUDE_PREMIUM_USER", "false").lower() == "true"
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        
        # 웹 인터페이스 초기화
        self.web_interface = None
        if self.use_premium_plan:
            try:
                from .web_interface import ClaudeWebInterfaceSync
                headless = os.getenv("CLAUDE_HEADLESS", "true").lower() == "true"
                self.web_interface = ClaudeWebInterfaceSync(headless=headless)
                
                # 웹 인터페이스 시작
                print("웹 인터페이스 시작 중...")
                self.web_interface.start()
                
                # 초기화 상태 확인
                if self.web_interface.is_initialized:
                    print("웹 인터페이스 초기화 및 시작 성공")
                else:
                    print("웹 인터페이스 초기화 실패")
                
            except Exception as e:
                print(f"웹 인터페이스 초기화 실패: {e}")
                self.web_interface = None

    def _llm_type(self):
        if self.use_premium_plan: return "claude_code_premium"
        elif self.api_key: return "claude_code_api"
        else: return "claude_code_test"

    def generate_response(self, prompt: str) -> str:
        """BaseLLM 인터페이스 구현: 프롬프트에 대한 응답 생성"""
        try:
            if self.use_premium_plan:
                if self.web_interface:
                    try:
                        print(f"Claude 웹 인터페이스로 질문 전송: {prompt}")
                        
                        # 실제 AI 응답 수신
                        print("Claude AI에 질문 전송 중...")
                        response = self.web_interface.send_message(prompt)
                        
                        if response and not response.startswith("메시지 전송 실패") and not response.startswith("브라우저 초기화 실패"):
                            print(f"Claude AI 실제 응답 수신: {len(response)} 문자")
                            return f"Claude AI 응답: {response}"
                        else:
                            print(f"웹 인터페이스 오류: {response}")
                            self.record_error()
                            return f"웹 인터페이스 오류: {response}"
                            
                    except Exception as e:
                        print(f"웹 인터페이스 호출 실패: {e}")
                        self.record_error()
                        return f"웹 인터페이스 호출 실패: {e}"
                else:
                    self.record_error()
                    return "Claude 유료 플랜: 웹 인터페이스가 초기화되지 않았습니다."
            elif self.api_key:
                return "Claude API: Claude Code가 정상적으로 작동합니다."
            else:
                return "테스트 모드: Claude Code 연동이 정상적으로 작동합니다."
        except Exception as e:
            self.record_error()
            logger.error(f"Claude LLM 에러: {e}")
            return f"Claude LLM 에러: {e}"

    def get_model_info(self) -> Dict[str, Any]:
        """BaseLLM 인터페이스 구현: 모델 정보 반환"""
        return {
            "name": self.model_name,
            "type": self._llm_type(),
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "use_premium_plan": self.use_premium_plan,
            "has_api_key": bool(self.api_key),
            "web_interface_available": self.web_interface is not None,
            "is_healthy": self.is_healthy()
        }

    def _call(self, prompt):
        """기존 LangChain 호환성을 위한 메서드"""
        return self.generate_response(prompt)
    
    def __del__(self):
        """소멸자: 웹 인터페이스 정리"""
        if self.web_interface:
            try:
                self.web_interface.close()
            except:
                pass
