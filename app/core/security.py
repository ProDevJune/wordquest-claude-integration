"""
보안 및 인증 관리
"""

import logging
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext

from .config import settings

logger = logging.getLogger(__name__)

# 비밀번호 해싱 컨텍스트
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SecurityManager:
    """보안 관리자"""
    
    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire_minutes = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    
    def hash_password(self, password: str) -> str:
        """비밀번호 해싱"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """비밀번호 검증"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def generate_salt(self, length: int = 32) -> str:
        """솔트 생성"""
        return secrets.token_hex(length)
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """액세스 토큰 생성"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """토큰 검증"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("토큰이 만료되었습니다")
            return None
        except jwt.JWTError as e:
            logger.warning(f"토큰 검증 실패: {e}")
            return None
    
    def generate_password_reset_token(self, email: str) -> str:
        """비밀번호 재설정 토큰 생성"""
        expire = datetime.utcnow() + timedelta(hours=24)
        to_encode = {"email": email, "exp": expire, "type": "password_reset"}
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_password_reset_token(self, token: str) -> Optional[str]:
        """비밀번호 재설정 토큰 검증"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") == "password_reset":
                return payload.get("email")
        except jwt.JWTError:
            pass
        return None
    
    def generate_email_verification_token(self, email: str) -> str:
        """이메일 인증 토큰 생성"""
        expire = datetime.utcnow() + timedelta(hours=48)
        to_encode = {"email": email, "exp": expire, "type": "email_verification"}
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_email_verification_token(self, token: str) -> Optional[str]:
        """이메일 인증 토큰 검증"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") == "email_verification":
                return payload.get("email")
        except jwt.JWTError:
            pass
        return None

class RateLimiter:
    """요청 제한 관리"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # 실제로는 Redis 사용 권장
    
    def is_allowed(self, user_id: str) -> bool:
        """사용자 요청이 허용되는지 확인"""
        now = datetime.utcnow()
        user_requests = self.requests.get(user_id, [])
        
        # 윈도우 시간 이전의 요청 제거
        user_requests = [req_time for req_time in user_requests 
                        if (now - req_time).seconds < self.window_seconds]
        
        if len(user_requests) < self.max_requests:
            user_requests.append(now)
            self.requests[user_id] = user_requests
            return True
        
        return False
    
    def get_remaining_requests(self, user_id: str) -> int:
        """남은 요청 수 반환"""
        now = datetime.utcnow()
        user_requests = self.requests.get(user_id, [])
        
        # 윈도우 시간 이전의 요청 제거
        user_requests = [req_time for req_time in user_requests 
                        if (now - req_time).seconds < self.window_seconds]
        
        return max(0, self.max_requests - len(user_requests))

class InputValidator:
    """입력 검증"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """이메일 형식 검증"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password: str) -> Dict[str, Any]:
        """비밀번호 강도 검증"""
        result = {
            "is_valid": True,
            "errors": [],
            "strength": "weak"
        }
        
        if len(password) < 8:
            result["is_valid"] = False
            result["errors"].append("비밀번호는 최소 8자 이상이어야 합니다.")
        
        if not any(c.isupper() for c in password):
            result["errors"].append("대문자를 포함해야 합니다.")
        
        if not any(c.islower() for c in password):
            result["errors"].append("소문자를 포함해야 합니다.")
        
        if not any(c.isdigit() for c in password):
            result["errors"].append("숫자를 포함해야 합니다.")
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            result["errors"].append("특수문자를 포함해야 합니다.")
        
        if len(result["errors"]) == 0:
            result["strength"] = "strong"
        elif len(result["errors"]) <= 2:
            result["strength"] = "medium"
        
        if len(result["errors"]) > 0:
            result["is_valid"] = False
        
        return result
    
    @staticmethod
    def validate_username(username: str) -> Dict[str, Any]:
        """사용자명 검증"""
        result = {
            "is_valid": True,
            "errors": []
        }
        
        if len(username) < 3:
            result["is_valid"] = False
            result["errors"].append("사용자명은 최소 3자 이상이어야 합니다.")
        
        if len(username) > 20:
            result["is_valid"] = False
            result["errors"].append("사용자명은 최대 20자까지 가능합니다.")
        
        if not username.replace("_", "").replace("-", "").isalnum():
            result["is_valid"] = False
            result["errors"].append("사용자명은 영문자, 숫자, 언더스코어(_), 하이픈(-)만 사용 가능합니다.")
        
        return result
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """입력 텍스트 정리"""
        import html
        # HTML 이스케이프
        text = html.escape(text)
        # SQL 인젝션 방지를 위한 기본적인 정리
        text = text.replace("'", "''")
        text = text.replace(";", "")
        return text.strip()

# 전역 보안 관리자 인스턴스
security_manager = SecurityManager()
rate_limiter = RateLimiter()
input_validator = InputValidator()

def get_security_manager() -> SecurityManager:
    """보안 관리자 인스턴스 반환"""
    return security_manager

def get_rate_limiter() -> RateLimiter:
    """요청 제한 관리자 인스턴스 반환"""
    return rate_limiter

def get_input_validator() -> InputValidator:
    """입력 검증기 인스턴스 반환"""
    return input_validator
