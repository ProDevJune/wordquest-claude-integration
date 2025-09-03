"""
학습 데이터 관리 및 통계 서비스
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

from ..core.database import get_db

logger = logging.getLogger(__name__)

class LearningService:
    """학습 데이터 관리 및 통계 서비스"""
    
    def __init__(self):
        self.db = get_db()
    
    def save_chat_message(self, user_id: int, user_message: str, ai_response: str) -> bool:
        """채팅 메시지 저장"""
        try:
            query = """
            INSERT INTO claude_integration_chat_messages 
            (user_id, user_message, ai_response, created_at, message_type)
            VALUES (%s, %s, %s, %s, 'chat')
            """
            
            self.db.execute_query(query, (user_id, user_message, ai_response, datetime.utcnow()))
            
            # 학습 활동 기록
            self._record_learning_activity(
                user_id=user_id,
                activity_type="chat",
                description=f"AI와의 영어 학습 대화: {user_message[:50]}..."
            )
            
            logger.info(f"채팅 메시지 저장 완료: user_id={user_id}")
            return True
            
        except Exception as e:
            logger.error(f"채팅 메시지 저장 중 오류: {e}")
            return False
    
    def save_grammar_check(self, user_id: int, original_text: str, corrected_text: str) -> bool:
        """문법 검사 결과 저장"""
        try:
            query = """
            INSERT INTO claude_integration_grammar_checks 
            (user_id, original_text, corrected_text, created_at)
            VALUES (%s, %s, %s, %s)
            """
            
            self.db.execute_query(query, (user_id, original_text, corrected_text, datetime.utcnow()))
            
            # 학습 활동 기록
            self._record_learning_activity(
                user_id=user_id,
                activity_type="grammar_check",
                description=f"문법 검사 완료: {original_text[:50]}..."
            )
            
            logger.info(f"문법 검사 결과 저장 완료: user_id={user_id}")
            return True
            
        except Exception as e:
            logger.error(f"문법 검사 결과 저장 중 오류: {e}")
            return False
    
    def save_vocabulary_check(self, user_id: int, original_text: str, analysis_result: str) -> bool:
        """어휘 분석 결과 저장"""
        try:
            query = """
            INSERT INTO claude_integration_vocabulary_checks 
            (user_id, original_text, analysis_result, created_at)
            VALUES (%s, %s, %s, %s)
            """
            
            self.db.execute_query(query, (user_id, original_text, analysis_result, datetime.utcnow()))
            
            # 학습 활동 기록
            self._record_learning_activity(
                user_id=user_id,
                activity_type="vocabulary_check",
                description=f"어휘 분석 완료: {original_text[:50]}..."
            )
            
            logger.info(f"어휘 분석 결과 저장 완료: user_id={user_id}")
            return True
            
        except Exception as e:
            logger.error(f"어휘 분석 결과 저장 중 오류: {e}")
            return False
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """사용자 학습 통계 조회"""
        try:
            stats = {}
            
            # 총 채팅 수
            chat_query = """
            SELECT COUNT(*) as count
            FROM claude_integration_chat_messages 
            WHERE user_id = %s
            """
            chat_result = self.db.execute_query(chat_query, (user_id,))
            stats['total_chats'] = chat_result[0]['count'] if chat_result else 0
            
            # 총 문법 검사 수
            grammar_query = """
            SELECT COUNT(*) as count
            FROM claude_integration_grammar_checks 
            WHERE user_id = %s
            """
            grammar_result = self.db.execute_query(grammar_query, (user_id,))
            stats['grammar_checks'] = grammar_result[0]['count'] if grammar_result else 0
            
            # 총 어휘 분석 수
            vocab_query = """
            SELECT COUNT(*) as count
            FROM claude_integration_vocabulary_checks 
            WHERE user_id = %s
            """
            vocab_result = self.db.execute_query(vocab_query, (user_id,))
            stats['vocabulary_checks'] = vocab_result[0]['count'] if vocab_result else 0
            
            # 총 학습 활동 수
            activity_query = """
            SELECT COUNT(*) as count
            FROM claude_integration_learning_activities 
            WHERE user_id = %s
            """
            activity_result = self.db.execute_query(activity_query, (user_id,))
            stats['total_activities'] = activity_result[0]['count'] if activity_result else 0
            
            # 학습 일수 계산
            first_activity_query = """
            SELECT MIN(created_at) as first_date
            FROM claude_integration_learning_activities 
            WHERE user_id = %s
            """
            first_result = self.db.execute_query(first_activity_query, (user_id,))
            
            if first_result and first_result[0]['first_date']:
                first_date = first_result[0]['first_date']
                if isinstance(first_date, str):
                    first_date = datetime.fromisoformat(first_date.replace('Z', '+00:00'))
                days_diff = (datetime.utcnow() - first_date).days
                stats['study_days'] = max(1, days_diff)
            else:
                stats['study_days'] = 0
            
            # 총 학습 시간 (대략적인 추정)
            stats['total_study_time'] = (stats['total_chats'] * 5 + 
                                       stats['grammar_checks'] * 3 + 
                                       stats['vocabulary_checks'] * 3)
            
            return stats
            
        except Exception as e:
            logger.error(f"사용자 통계 조회 중 오류: {e}")
            return {
                'total_chats': 0,
                'grammar_checks': 0,
                'vocabulary_checks': 0,
                'total_activities': 0,
                'study_days': 0,
                'total_study_time': 0
            }
    
    def get_recent_activities(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """최근 학습 활동 조회"""
        try:
            # 먼저 learning_activities 테이블에서 조회 시도
            query = """
            SELECT activity_type, description, created_at, metadata
            FROM claude_integration_learning_activities 
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
            """
            
            result = self.db.execute_query(query, (user_id, limit))
            
            # 결과가 있으면 반환
            if result:
                activities = []
                for row in result:
                    activity = {
                        'type': row['activity_type'],
                        'description': row['description'],
                        'created_at': self._format_datetime(row['created_at']),
                        'metadata': row.get('metadata', {})
                    }
                    activities.append(activity)
                return activities
            
            # learning_activities에 데이터가 없으면 다른 테이블에서 대체 데이터 생성
            logger.info(f"사용자 {user_id}의 learning_activities 데이터가 없어 대체 데이터를 생성합니다.")
            
            # 채팅 메시지, 문법 검사, 어휘 분석에서 최근 활동 생성
            activities = []
            
            # 최근 채팅 메시지
            chat_query = """
            SELECT user_message, created_at
            FROM claude_integration_chat_messages 
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
            """
            chat_result = self.db.execute_query(chat_query, (user_id, limit))
            
            for row in chat_result:
                activities.append({
                    'type': 'chat',
                    'description': f"AI와의 영어 학습 대화: {row['user_message'][:50]}...",
                    'created_at': self._format_datetime(row['created_at']),
                    'metadata': {'source': 'chat_messages'}
                })
            
            # 최근 문법 검사
            grammar_query = """
            SELECT original_text, created_at
            FROM claude_integration_grammar_checks 
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
            """
            grammar_result = self.db.execute_query(grammar_query, (user_id, limit))
            
            for row in grammar_result:
                activities.append({
                    'type': 'grammar_check',
                    'description': f"문법 검사 완료: {row['original_text'][:50]}...",
                    'created_at': self._format_datetime(row['created_at']),
                    'metadata': {'source': 'grammar_checks'}
                })
            
            # 최근 어휘 분석
            vocab_query = """
            SELECT original_text, created_at
            FROM claude_integration_vocabulary_checks 
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
            """
            vocab_result = self.db.execute_query(vocab_query, (user_id, limit))
            
            for row in vocab_result:
                activities.append({
                    'type': 'vocabulary_check',
                    'description': f"어휘 분석 완료: {row['original_text'][:50]}...",
                    'created_at': self._format_datetime(row['created_at']),
                    'metadata': {'source': 'vocabulary_checks'}
                })
            
            # 날짜순으로 정렬하고 limit 적용
            activities.sort(key=lambda x: x['created_at'], reverse=True)
            return activities[:limit]
            
        except Exception as e:
            logger.error(f"최근 학습 활동 조회 중 오류: {e}")
            # 오류 발생 시 기본 활동 반환
            return [
                {
                    'type': 'system',
                    'description': '학습 활동을 불러오는 중입니다...',
                    'created_at': '방금 전',
                    'metadata': {'source': 'fallback'}
                }
            ]
    
    def get_weekly_activities(self, user_id: int) -> Dict[str, int]:
        """주간 학습 활동 통계"""
        try:
            # 최근 7일간의 활동
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=7)
            
            query = """
            SELECT 
                DATE(created_at) as activity_date,
                COUNT(*) as activity_count
            FROM claude_integration_learning_activities 
            WHERE user_id = %s 
            AND created_at BETWEEN %s AND %s
            GROUP BY DATE(created_at)
            ORDER BY activity_date
            """
            
            result = self.db.execute_query(query, (user_id, start_date, end_date))
            
            # 날짜별 활동 수를 딕셔너리로 변환
            weekly_data = {}
            for row in result:
                date_str = row['activity_date'].strftime('%Y-%m-%d') if hasattr(row['activity_date'], 'strftime') else str(row['activity_date'])
                weekly_data[date_str] = row['activity_count']
            
            # 빈 날짜는 0으로 채우기
            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')
                if date_str not in weekly_data:
                    weekly_data[date_str] = 0
                current_date += timedelta(days=1)
            
            return weekly_data
            
        except Exception as e:
            logger.error(f"주간 학습 활동 조회 중 오류: {e}")
            return {}
    
    def get_grammar_checks(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """문법 검사 기록 조회"""
        try:
            query = """
            SELECT original_text, corrected_text, created_at
            FROM claude_integration_grammar_checks 
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
            """
            
            result = self.db.execute_query(query, (user_id, limit))
            
            checks = []
            for row in result:
                check = {
                    'original_text': row['original_text'],
                    'corrected_text': row['corrected_text'],
                    'created_at': self._format_datetime(row['created_at'])
                }
                checks.append(check)
            
            return checks
            
        except Exception as e:
            logger.error(f"문법 검사 기록 조회 중 오류: {e}")
            return []
    
    def get_vocabulary_checks(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """어휘 분석 기록 조회"""
        try:
            query = """
            SELECT original_text, analysis_result, created_at
            FROM claude_integration_vocabulary_checks 
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
            """
            
            result = self.db.execute_query(query, (user_id, limit))
            
            checks = []
            for row in result:
                check = {
                    'original_text': row['original_text'],
                    'analysis_result': row['analysis_result'],
                    'created_at': self._format_datetime(row['created_at'])
                }
                checks.append(check)
            
            return checks
            
        except Exception as e:
            logger.error(f"어휘 분석 기록 조회 중 오류: {e}")
            return []
    
    def get_chat_history(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """채팅 기록 조회"""
        try:
            query = """
            SELECT user_message, ai_response, created_at
            FROM claude_integration_chat_messages 
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
            """
            
            result = self.db.execute_query(query, (user_id, limit))
            
            chats = []
            for row in result:
                chat = {
                    'user_message': row['user_message'],
                    'ai_response': row['ai_response'],
                    'created_at': self._format_datetime(row['created_at'])
                }
                chats.append(chat)
            
            return chats
            
        except Exception as e:
            logger.error(f"채팅 기록 조회 중 오류: {e}")
            return []
    
    def _record_learning_activity(self, user_id: int, activity_type: str, description: str, metadata: Optional[Dict] = None):
        """학습 활동 기록"""
        try:
            query = """
            INSERT INTO claude_integration_learning_activities 
            (user_id, activity_type, description, metadata, created_at)
            VALUES (%s, %s, %s, %s, %s)
            """
            
            metadata_json = json.dumps(metadata) if metadata else None
            
            self.db.execute_query(query, (user_id, activity_type, description, metadata_json, datetime.utcnow()))
            
        except Exception as e:
            logger.error(f"학습 활동 기록 중 오류: {e}")
    
    def _format_datetime(self, dt) -> str:
        """날짜시간 형식 변환"""
        try:
            if isinstance(dt, str):
                # 문자열인 경우 파싱
                dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
            
            if isinstance(dt, datetime):
                # 한국 시간으로 변환 (UTC+9)
                kst_time = dt + timedelta(hours=9)
                return kst_time.strftime('%Y-%m-%d %H:%M')
            else:
                return str(dt)
        except Exception:
            return str(dt)
    
    def get_learning_progress(self, user_id: int) -> Dict[str, Any]:
        """학습 진도 조회"""
        try:
            stats = self.get_user_stats(user_id)
            
            # 진도 계산
            total_activities = stats['total_activities']
            
            if total_activities == 0:
                progress = {
                    'level': '초급',
                    'percentage': 0,
                    'next_milestone': '첫 번째 학습 활동',
                    'milestone_progress': 0
                }
            elif total_activities < 10:
                progress = {
                    'level': '초급',
                    'percentage': (total_activities / 10) * 100,
                    'next_milestone': '10회 학습 활동',
                    'milestone_progress': total_activities
                }
            elif total_activities < 50:
                progress = {
                    'level': '중급',
                    'percentage': ((total_activities - 10) / 40) * 100,
                    'next_milestone': '50회 학습 활동',
                    'milestone_progress': total_activities - 10
                }
            else:
                progress = {
                    'level': '고급',
                    'percentage': 100,
                    'next_milestone': '모든 마일스톤 달성!',
                    'milestone_progress': 50
                }
            
            return {
                'stats': stats,
                'progress': progress
            }
            
        except Exception as e:
            logger.error(f"학습 진도 조회 중 오류: {e}")
            return {
                'stats': {},
                'progress': {
                    'level': '초급',
                    'percentage': 0,
                    'next_milestone': '데이터 로드 실패',
                    'milestone_progress': 0
                }
            }
