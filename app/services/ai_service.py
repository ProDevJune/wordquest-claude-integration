"""
AI 서비스 (OpenAI + Solar API)
"""

import logging
import time
from typing import Optional, Dict, Any
import requests
import json

from ..core.config import settings

logger = logging.getLogger(__name__)

class AIService:
    """AI 서비스 (OpenAI + Solar API)"""
    
    def __init__(self):
        self.openai_api_key = settings.OPENAI_API_KEY
        self.solar_api_key = settings.SOLAR_API_KEY
        self.openai_model = settings.OPENAI_MODEL
        self.solar_model = settings.SOLAR_MODEL
        self.openai_base_url = settings.OPENAI_BASE_URL
        self.solar_base_url = settings.SOLAR_BASE_URL
        
        # API 사용 가능 여부 확인
        self.openai_available = bool(self.openai_api_key)
        self.solar_available = bool(self.solar_api_key)
        
        if not self.openai_available and not self.solar_available:
            logger.warning("⚠️ OpenAI API 키와 Solar API 키가 모두 설정되지 않았습니다.")
    
    def get_response(self, prompt: str, use_solar: bool = False) -> str:
        """AI 응답 생성"""
        try:
            if use_solar and self.solar_available:
                return self._get_solar_response(prompt)
            elif self.openai_available:
                return self._get_openai_response(prompt)
            else:
                return self._get_fallback_response(prompt)
        except Exception as e:
            logger.error(f"AI 응답 생성 중 오류: {e}")
            return f"AI 서비스 오류가 발생했습니다: {str(e)}"
    
    def _get_openai_response(self, prompt: str) -> str:
        """OpenAI API를 사용한 응답 생성"""
        try:
            start_time = time.time()
            
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.openai_model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            response = requests.post(
                f"{self.openai_base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    content = response_data["choices"][0]["message"]["content"]
                    response_time = time.time() - start_time
                    
                    logger.info(f"OpenAI 응답 생성 완료 (소요시간: {response_time:.2f}초)")
                    return content
                else:
                    logger.error("OpenAI API: 응답 형식이 올바르지 않습니다.")
                    return "OpenAI API: 응답 형식이 올바르지 않습니다."
            else:
                logger.error(f"OpenAI API 오류: {response.status_code} - {response.text}")
                return f"OpenAI API 오류: {response.status_code}"
                
        except requests.exceptions.Timeout:
            logger.error("OpenAI API 요청 시간 초과")
            return "OpenAI API 요청 시간이 초과되었습니다."
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenAI API 요청 오류: {e}")
            return f"OpenAI API 요청 오류: {str(e)}"
        except Exception as e:
            logger.error(f"OpenAI API 예상치 못한 오류: {e}")
            return f"OpenAI API 예상치 못한 오류: {str(e)}"
    
    def _get_solar_response(self, prompt: str) -> str:
        """Solar API를 사용한 응답 생성"""
        try:
            start_time = time.time()
            
            headers = {
                "Authorization": f"Bearer {self.solar_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.solar_model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            response = requests.post(
                f"{self.solar_base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    
                    if "choices" in response_data and len(response_data["choices"]) > 0:
                        content = response_data["choices"][0]["message"]["content"]
                        response_time = time.time() - start_time
                        
                        logger.info(f"Solar API 응답 생성 완료 (소요시간: {response_time:.2f}초)")
                        return content
                    else:
                        logger.error("Solar API: 응답 형식이 올바르지 않습니다.")
                        return "Solar API: 응답 형식이 올바르지 않습니다."
                        
                except json.JSONDecodeError:
                    logger.error("Solar API: JSON 응답 파싱 실패")
                    return "Solar API: JSON 응답 파싱 실패"
                    
            else:
                logger.error(f"Solar API 오류: {response.status_code} - {response.text}")
                return f"Solar API 오류: {response.status_code}"
                
        except requests.exceptions.Timeout:
            logger.error("Solar API 요청 시간 초과")
            return "Solar API 요청 시간이 초과되었습니다."
        except requests.exceptions.RequestException as e:
            logger.error(f"Solar API 요청 오류: {e}")
            return f"Solar API 요청 오류: {str(e)}"
        except Exception as e:
            logger.error(f"Solar API 예상치 못한 오류: {e}")
            return f"Solar API 예상치 못한 오류: {str(e)}"
    
    def _get_fallback_response(self, prompt: str) -> str:
        """폴백 응답 (API 키가 없을 때)"""
        logger.warning("API 키가 설정되지 않아 폴백 응답을 사용합니다.")
        
        # 간단한 규칙 기반 응답
        if "hello" in prompt.lower() or "안녕" in prompt:
            return "안녕하세요! 영어 학습 AI 시스템에 오신 것을 환영합니다!"
        elif "grammar" in prompt.lower() or "문법" in prompt:
            return "문법 검사를 원하시는군요. 영어 문장을 입력해주세요."
        elif "vocabulary" in prompt.lower() or "어휘" in prompt:
            return "어휘 분석을 원하시는군요. 영어 텍스트를 입력해주세요."
        else:
            return "죄송합니다. 현재 AI 서비스를 사용할 수 없습니다. API 키를 설정해주세요."
    
    def test_connection(self) -> Dict[str, bool]:
        """API 연결 테스트"""
        results = {
            "openai": False,
            "solar": False
        }
        
        # OpenAI 연결 테스트
        if self.openai_available:
            try:
                test_prompt = "Hello"
                response = self._get_openai_response(test_prompt)
                results["openai"] = not response.startswith("OpenAI API 오류")
            except Exception as e:
                logger.error(f"OpenAI 연결 테스트 실패: {e}")
                results["openai"] = False
        
        # Solar API 연결 테스트
        if self.solar_available:
            try:
                test_prompt = "안녕하세요"
                response = self._get_solar_response(test_prompt)
                results["solar"] = not response.startswith("Solar API 오류")
            except Exception as e:
                logger.error(f"Solar API 연결 테스트 실패: {e}")
                results["solar"] = False
        
        return results
    
    def get_api_status(self) -> Dict[str, Any]:
        """API 상태 정보 반환"""
        return {
            "openai": {
                "available": self.openai_available,
                "model": self.openai_model,
                "base_url": self.openai_base_url
            },
            "solar": {
                "available": self.solar_available,
                "model": self.solar_model,
                "base_url": self.solar_base_url
            },
            "fallback_available": not self.openai_available and not self.solar_available
        }
    
    def get_english_learning_prompt(self, user_input: str, context: str = "") -> str:
        """영어 학습을 위한 프롬프트 생성"""
        base_prompt = f"""
당신은 친절하고 전문적인 영어 선생님입니다. 
사용자의 영어 학습을 도와주세요.

사용자 질문: {user_input}

{context if context else ""}

다음 지침을 따라 답변해주세요:
1. 친근하고 격려하는 톤으로 답변
2. 한국어와 영어를 적절히 혼용하여 설명
3. 구체적인 예시와 함께 설명
4. 추가 학습 팁 제공
5. 사용자의 수준에 맞는 어휘 사용

답변을 시작하세요:
"""
        return base_prompt.strip()
    
    def get_grammar_check_prompt(self, text: str) -> str:
        """문법 검사를 위한 프롬프트 생성"""
        return f"""
당신은 전문적인 영어 문법 교정 선생님입니다.
다음 영어 텍스트의 문법을 검사하고 교정해주세요.

원문: {text}

다음 형식으로 답변해주세요:

## 🔍 문법 오류 목록
- 오류 1: [오류 설명]
- 오류 2: [오류 설명]
...

## ✏️ 교정된 텍스트
[교정된 전체 텍스트]

## 💡 개선 제안
- [구체적인 개선 제안]
- [학습 포인트]

## 📚 관련 문법 규칙
- [관련된 문법 규칙 설명]

친근하고 격려하는 톤으로 답변해주세요.
"""
    
    def get_vocabulary_analysis_prompt(self, text: str) -> str:
        """어휘 분석을 위한 프롬프트 생성"""
        return f"""
당신은 전문적인 영어 어휘 분석 선생님입니다.
다음 영어 텍스트의 어휘를 분석해주세요.

원문: {text}

다음 형식으로 답변해주세요:

## 📊 어휘 수준 평가
**수준**: [초급/중급/고급] - [수준 판단 근거]

## 📝 주요 어휘 목록
- **단어 1**: [의미] - [사용법 예시]
- **단어 2**: [의미] - [사용법 예시]
...

## 🚨 어려운 단어 설명
- **어려운 단어**: [상세한 의미와 사용법]

## 💡 어휘 개선 제안
- [구체적인 개선 방법]
- [동의어/유사어 제안]

## 🎯 학습 추천 단어
- [수준별 학습 추천 단어들]

## 📚 학습 전략
- [어휘 향상을 위한 구체적인 학습 방법]

친근하고 격려하는 톤으로 답변해주세요.
"""
