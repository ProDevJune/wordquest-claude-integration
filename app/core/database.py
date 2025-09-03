"""
WordQuest 데이터베이스 연결 및 관리
"""

import logging
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extensions import connection, cursor

from .config import settings, get_database_url

logger = logging.getLogger(__name__)

class Database:
    """WordQuest 데이터베이스 연결 관리"""
    
    def __init__(self):
        self.connection_pool = None
        self._init_connection_pool()
    
    def _init_connection_pool(self):
        """연결 풀 초기화"""
        try:
            database_url = get_database_url()
            self.connection_pool = SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=database_url
            )
            logger.info("✅ 데이터베이스 연결 풀 초기화 완료")
        except Exception as e:
            logger.error(f"❌ 데이터베이스 연결 풀 초기화 실패: {e}")
            self.connection_pool = None
    
    @contextmanager
    def get_connection(self):
        """데이터베이스 연결 컨텍스트 매니저"""
        conn = None
        try:
            if self.connection_pool:
                conn = self.connection_pool.getconn()
                yield conn
            else:
                # 연결 풀이 없으면 직접 연결
                conn = psycopg2.connect(get_database_url())
                yield conn
        except Exception as e:
            logger.error(f"데이터베이스 연결 오류: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                if self.connection_pool:
                    self.connection_pool.putconn(conn)
                else:
                    conn.close()
    
    @contextmanager
    def get_cursor(self, commit: bool = True):
        """데이터베이스 커서 컨텍스트 매니저"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            try:
                yield cursor
                if commit:
                    conn.commit()
            except Exception as e:
                conn.rollback()
                raise
            finally:
                cursor.close()
    
    def test_connection(self) -> bool:
        """데이터베이스 연결 테스트"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT version();")
                result = cursor.fetchone()
                logger.info(f"✅ 데이터베이스 연결 성공: {result['version'][:50]}...")
                return True
        except Exception as e:
            logger.error(f"❌ 데이터베이스 연결 테스트 실패: {e}")
            return False
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """쿼리 실행 및 결과 반환"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                else:
                    return [{"affected_rows": cursor.rowcount}]
        except Exception as e:
            logger.error(f"쿼리 실행 오류: {e}")
            raise
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """여러 쿼리 실행"""
        try:
            with self.get_cursor() as cursor:
                cursor.executemany(query, params_list)
                return cursor.rowcount
        except Exception as e:
            logger.error(f"여러 쿼리 실행 오류: {e}")
            raise
    
    def table_exists(self, table_name: str) -> bool:
        """테이블 존재 여부 확인"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    );
                """, (table_name,))
                result = cursor.fetchone()
                return result['exists']
        except Exception as e:
            logger.error(f"테이블 존재 확인 오류: {e}")
            return False
    
    def create_tables_if_not_exist(self):
        """필요한 테이블들이 없으면 생성"""
        try:
            # 사용자 테이블
            if not self.table_exists('claude_integration_users'):
                self._create_users_table()
            
            # 채팅 메시지 테이블
            if not self.table_exists('claude_integration_chat_messages'):
                self._create_chat_messages_table()
            
            # 문법 검사 테이블
            if not self.table_exists('claude_integration_grammar_checks'):
                self._create_grammar_checks_table()
            
            # 어휘 분석 테이블
            if not self.table_exists('claude_integration_vocabulary_checks'):
                self._create_vocabulary_checks_table()
            
            # 학습 활동 테이블
            if not self.table_exists('claude_integration_learning_activities'):
                self._create_learning_activities_table()
            
            logger.info("✅ 필요한 테이블 생성 완료")
            
        except Exception as e:
            logger.error(f"❌ 테이블 생성 중 오류: {e}")
            raise
    
    def _create_users_table(self):
        """사용자 테이블 생성"""
        query = """
        CREATE TABLE claude_integration_users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            last_login TIMESTAMP
        );
        """
        self.execute_query(query)
    
    def _create_chat_messages_table(self):
        """채팅 메시지 테이블 생성"""
        query = """
        CREATE TABLE claude_integration_chat_messages (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES claude_integration_users(id) ON DELETE CASCADE,
            user_message TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            message_type VARCHAR(20) DEFAULT 'chat'
        );
        """
        self.execute_query(query)
    
    def _create_grammar_checks_table(self):
        """문법 검사 테이블 생성"""
        query = """
        CREATE TABLE claude_integration_grammar_checks (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES claude_integration_users(id) ON DELETE CASCADE,
            original_text TEXT NOT NULL,
            corrected_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        self.execute_query(query)
    
    def _create_vocabulary_checks_table(self):
        """어휘 분석 테이블 생성"""
        query = """
        CREATE TABLE claude_integration_vocabulary_checks (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES claude_integration_users(id) ON DELETE CASCADE,
            original_text TEXT NOT NULL,
            analysis_result TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        self.execute_query(query)
    
    def _create_learning_activities_table(self):
        """학습 활동 테이블 생성"""
        query = """
        CREATE TABLE claude_integration_learning_activities (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES claude_integration_users(id) ON DELETE CASCADE,
            activity_type VARCHAR(50) NOT NULL,
            description TEXT NOT NULL,
            metadata JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        self.execute_query(query)
    
    def close(self):
        """데이터베이스 연결 종료"""
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("✅ 데이터베이스 연결 풀 종료")

# 전역 데이터베이스 인스턴스
db = Database()

def get_db() -> Database:
    """데이터베이스 인스턴스 반환"""
    return db
