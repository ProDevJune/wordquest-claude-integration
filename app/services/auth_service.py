"""
사용자 인증 및 관리 서비스
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from ..core.database import get_db
from ..core.security import get_security_manager, get_input_validator

logger = logging.getLogger(__name__)

class AuthService:
    """사용자 인증 서비스"""
    
    def __init__(self):
        self.db = get_db()
        self.security_manager = get_security_manager()
        self.input_validator = get_input_validator()
    
    def signup(self, username: str, email: str, password: str, full_name: str) -> Optional[Dict[str, Any]]:
        """사용자 회원가입"""
        try:
            # 입력 검증
            if not self._validate_signup_input(username, email, password, full_name):
                return None
            
            # 중복 확인
            if self._check_duplicate_user(username, email):
                logger.warning(f"중복 사용자 시도: username={username}, email={email}")
                return None
            
            # 비밀번호 해싱
            password_hash = self.security_manager.hash_password(password)
            
            # 사용자 생성
            user_data = {
                "username": username,
                "email": email,
                "password_hash": password_hash,
                "full_name": full_name,
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            query = """
            INSERT INTO claude_integration_users 
            (username, email, password_hash, full_name, created_at, is_active)
            VALUES (%(username)s, %(email)s, %(password_hash)s, %(full_name)s, %(created_at)s, %(is_active)s)
            RETURNING id, username, email, full_name, created_at, is_active
            """
            
            result = self.db.execute_query(query, user_data)
            
            if result:
                user = result[0]
                logger.info(f"사용자 회원가입 성공: {username}")
                return dict(user)
            
            return None
            
        except Exception as e:
            logger.error(f"회원가입 중 오류: {e}")
            return None
    
    def login(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """사용자 로그인"""
        try:
            # 이메일 형식 검증
            if not self.input_validator.validate_email(email):
                logger.warning(f"잘못된 이메일 형식: {email}")
                return None
            
            # 사용자 조회
            query = """
            SELECT id, username, email, password_hash, full_name, created_at, is_active, last_login
            FROM claude_integration_users 
            WHERE email = %s AND is_active = TRUE
            """
            
            result = self.db.execute_query(query, (email,))
            
            if not result:
                logger.warning(f"존재하지 않는 사용자 또는 비활성 계정: {email}")
                return None
            
            user = result[0]
            
            # 비밀번호 검증
            if not self.security_manager.verify_password(password, user['password_hash']):
                logger.warning(f"잘못된 비밀번호: {email}")
                return None
            
            # 마지막 로그인 시간 업데이트
            self._update_last_login(user['id'])
            
            # 민감한 정보 제거
            user_dict = dict(user)
            user_dict.pop('password_hash', None)
            
            logger.info(f"사용자 로그인 성공: {email}")
            return user_dict
            
        except Exception as e:
            logger.error(f"로그인 중 오류: {e}")
            return None
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """비밀번호 변경"""
        try:
            # 현재 비밀번호 확인
            query = "SELECT password_hash FROM claude_integration_users WHERE id = %s"
            result = self.db.execute_query(query, (user_id,))
            
            if not result:
                return False
            
            current_hash = result[0]['password_hash']
            
            if not self.security_manager.verify_password(current_password, current_hash):
                return False
            
            # 새 비밀번호 검증
            password_validation = self.input_validator.validate_password(new_password)
            if not password_validation['is_valid']:
                logger.warning(f"비밀번호 강도 부족: {password_validation['errors']}")
                return False
            
            # 새 비밀번호 해싱 및 업데이트
            new_password_hash = self.security_manager.hash_password(new_password)
            
            update_query = """
            UPDATE claude_integration_users 
            SET password_hash = %s, updated_at = %s
            WHERE id = %s
            """
            
            self.db.execute_query(update_query, (new_password_hash, datetime.utcnow(), user_id))
            
            logger.info(f"비밀번호 변경 성공: user_id={user_id}")
            return True
            
        except Exception as e:
            logger.error(f"비밀번호 변경 중 오류: {e}")
            return False
    
    def delete_account(self, user_id: int) -> bool:
        """계정 삭제"""
        try:
            # 사용자 비활성화 (실제 삭제 대신)
            query = """
            UPDATE claude_integration_users 
            SET is_active = FALSE, updated_at = %s
            WHERE id = %s
            """
            
            result = self.db.execute_query(query, (datetime.utcnow(), user_id))
            
            if result and result[0]['affected_rows'] > 0:
                logger.info(f"계정 비활성화 성공: user_id={user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"계정 삭제 중 오류: {e}")
            return False
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """사용자 ID로 사용자 정보 조회"""
        try:
            query = """
            SELECT id, username, email, full_name, created_at, is_active, last_login
            FROM claude_integration_users 
            WHERE id = %s AND is_active = TRUE
            """
            
            result = self.db.execute_query(query, (user_id,))
            
            if result:
                return dict(result[0])
            
            return None
            
        except Exception as e:
            logger.error(f"사용자 조회 중 오류: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """이메일로 사용자 정보 조회"""
        try:
            query = """
            SELECT id, username, email, full_name, created_at, is_active, last_login
            FROM claude_integration_users 
            WHERE email = %s AND is_active = TRUE
            """
            
            result = self.db.execute_query(query, (email,))
            
            if result:
                return dict(result[0])
            
            return None
            
        except Exception as e:
            logger.error(f"사용자 조회 중 오류: {e}")
            return None
    
    def reset_password(self, email: str) -> bool:
        """비밀번호 재설정"""
        try:
            # 사용자 존재 확인
            user = self.get_user_by_email(email)
            if not user:
                return False
            
            # 비밀번호 재설정 토큰 생성
            reset_token = self.security_manager.generate_password_reset_token(email)
            
            # TODO: 이메일로 토큰 전송
            logger.info(f"비밀번호 재설정 토큰 생성: {email}")
            
            return True
            
        except Exception as e:
            logger.error(f"비밀번호 재설정 중 오류: {e}")
            return False
    
    def _validate_signup_input(self, username: str, email: str, password: str, full_name: str) -> bool:
        """회원가입 입력 검증"""
        # 사용자명 검증
        username_validation = self.input_validator.validate_username(username)
        if not username_validation['is_valid']:
            logger.warning(f"사용자명 검증 실패: {username_validation['errors']}")
            return False
        
        # 이메일 검증
        if not self.input_validator.validate_email(email):
            logger.warning(f"이메일 형식 오류: {email}")
            return False
        
        # 비밀번호 검증
        password_validation = self.input_validator.validate_password(password)
        if not password_validation['is_valid']:
            logger.warning(f"비밀번호 강도 부족: {password_validation['errors']}")
            return False
        
        # 실명 검증
        if not full_name or len(full_name.strip()) < 2:
            logger.warning(f"실명 검증 실패: {full_name}")
            return False
        
        return True
    
    def _check_duplicate_user(self, username: str, email: str) -> bool:
        """중복 사용자 확인"""
        try:
            query = """
            SELECT COUNT(*) as count
            FROM claude_integration_users 
            WHERE username = %s OR email = %s
            """
            
            result = self.db.execute_query(query, (username, email))
            
            if result and result[0]['count'] > 0:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"중복 사용자 확인 중 오류: {e}")
            return True  # 오류 시 안전하게 중복으로 처리
    
    def _update_last_login(self, user_id: int):
        """마지막 로그인 시간 업데이트"""
        try:
            query = """
            UPDATE claude_integration_users 
            SET last_login = %s
            WHERE id = %s
            """
            
            self.db.execute_query(query, (datetime.utcnow(), user_id))
            
        except Exception as e:
            logger.error(f"마지막 로그인 시간 업데이트 중 오류: {e}")
    
    def create_access_token(self, user_id: int, username: str) -> str:
        """액세스 토큰 생성"""
        data = {
            "sub": str(user_id),
            "username": username,
            "type": "access"
        }
        return self.security_manager.create_access_token(data)
    
    def verify_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """액세스 토큰 검증"""
        return self.security_manager.verify_token(token)
