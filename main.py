#!/usr/bin/env python3
"""
WordQuest Claude Integration - Streamlit Web Application
영어 학습 AI 시스템의 메인 애플리케이션
"""

import streamlit as st
import os
import sys
import logging
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 환경 변수 로드
from dotenv import load_dotenv
load_dotenv()

# 앱 모듈들 import
from app.core.config import settings
from app.core.database import Database
# from app.services.auth_service import AuthService # This line is removed as per the new_code
# from app.services.ai_service import AIService # This line is removed as per the new_code
# from app.services.learning_service import LearningService # This line is removed as per the new_code

# 페이지 설정
st.set_page_config(
    page_title="🎓 영어 학습 AI 시스템",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 세션 상태 초기화
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'is_authenticated' not in st.session_state:
    st.session_state.is_authenticated = False
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'debug_mode' not in st.session_state:
    st.session_state.debug_mode = False

# 서비스 import
try:
    from app.services.auth_service import AuthService
    from app.services.ai_service import AIService
    from app.services.learning_service import LearningService
    auth_service = AuthService()
    ai_service = AIService()
    learning_service = LearningService()
    logger.info("✅ 모든 서비스 모듈을 성공적으로 불러왔습니다.")
except ImportError as e:
    error_msg = f"❌ 서비스 모듈을 불러올 수 없습니다: {e}"
    logger.error(error_msg)
    st.error(error_msg)
    st.stop()

def main():
    """메인 애플리케이션 함수"""
    try:
        st.title("🎓 영어 학습 AI 시스템")
        st.markdown("---")
        
        # 디버그 모드 토글
        if st.sidebar.checkbox("🐛 디버그 모드", value=st.session_state.debug_mode):
            st.session_state.debug_mode = True
            show_debug_info()
        else:
            st.session_state.debug_mode = False
        
        show_sidebar()
        
        if not st.session_state.is_authenticated:
            show_auth_pages()
        else:
            show_main_pages()
            
    except Exception as e:
        error_msg = f"메인 애플리케이션 실행 중 오류: {e}"
        logger.error(error_msg)
        st.error(error_msg)
        if st.session_state.debug_mode:
            st.exception(e)

def show_debug_info():
    """디버그 정보 표시"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🐛 디버그 정보")
    
    # 세션 상태 정보
    st.sidebar.json({
        "user_id": st.session_state.user_id,
        "is_authenticated": st.session_state.is_authenticated,
        "current_page": st.session_state.current_page,
        "debug_mode": st.session_state.debug_mode
    })
    
    # 서비스 상태 확인
    try:
        db_status = "연결됨" if learning_service.db.test_connection() else "연결 안됨"
        st.sidebar.markdown(f"**DB 상태**: {db_status}")
    except:
        st.sidebar.markdown("**DB 상태**: 확인 불가")
    
    # API 상태 확인
    try:
        api_status = ai_service.get_api_status()
        st.sidebar.markdown(f"**OpenAI**: {'✅' if api_status['openai']['available'] else '❌'}")
        st.sidebar.markdown(f"**Solar**: {'✅' if api_status['solar']['available'] else '❌'}")
    except:
        st.sidebar.markdown("**API 상태**: 확인 불가")

def show_sidebar():
    """사이드바 표시"""
    try:
        with st.sidebar:
            st.header("🎯 메뉴")
            
            if st.session_state.is_authenticated:
                # 인증된 사용자 메뉴
                st.success(f"👤 {st.session_state.user_info['username']}님 환영합니다!")
                
                if st.button("🏠 홈", use_container_width=True):
                    st.session_state.current_page = 'home'
                    st.rerun()
                
                if st.button("💬 AI 채팅", use_container_width=True):
                    st.session_state.current_page = 'chat'
                    st.rerun()
                
                if st.button("📊 학습 대시보드", use_container_width=True):
                    st.session_state.current_page = 'dashboard'
                    st.rerun()
                
                if st.button("✏️ 문법 검사", use_container_width=True):
                    st.session_state.current_page = 'grammar'
                    st.rerun()
                
                if st.button("📚 어휘 도움", use_container_width=True):
                    st.session_state.current_page = 'vocabulary'
                    st.rerun()
                
                if st.button("👤 프로필", use_container_width=True):
                    st.session_state.current_page = 'profile'
                    st.rerun()
                
                st.markdown("---")
                if st.button("🚪 로그아웃", use_container_width=True):
                    logout()
                    st.rerun()
            else:
                # 비인증 사용자 메뉴
                st.info("로그인하여 모든 기능을 이용하세요!")
                
                if st.button("🏠 홈", use_container_width=True):
                    st.session_state.current_page = 'home'
                    st.rerun()
                
                if st.button("💬 AI 채팅 (체험)", use_container_width=True):
                    st.session_state.current_page = 'chat'
                    st.rerun()
                    
    except Exception as e:
        error_msg = f"사이드바 표시 중 오류: {e}"
        logger.error(error_msg)
        st.sidebar.error(error_msg)
        if st.session_state.debug_mode:
            st.sidebar.exception(e)

def show_auth_pages():
    """인증 페이지 표시"""
    try:
        tab1, tab2 = st.tabs(["🔐 로그인", "📝 회원가입"])
        
        with tab1:
            show_login_page()
        
        with tab2:
            show_signup_page()
            
    except Exception as e:
        error_msg = f"인증 페이지 표시 중 오류: {e}"
        logger.error(error_msg)
        st.error(error_msg)
        if st.session_state.debug_mode:
            st.exception(e)

def show_login_page():
    """로그인 페이지"""
    try:
        st.header("🔐 로그인")
        
        with st.form("login_form"):
            email = st.text_input("📧 이메일", placeholder="your@email.com")
            password = st.text_input("🔒 비밀번호", type="password", placeholder="비밀번호를 입력하세요")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                submitted = st.form_submit_button("로그인", use_container_width=True)
            with col2:
                if st.form_submit_button("비밀번호 찾기", use_container_width=True):
                    st.info("비밀번호 찾기 기능은 준비 중입니다.")
            
            if submitted and email and password:
                try:
                    user = auth_service.login(email, password)
                    if user:
                        st.session_state.user_id = user['id']
                        st.session_state.is_authenticated = True
                        st.session_state.user_info = user
                        st.session_state.current_page = 'home'
                        st.success("로그인 성공! 🎉")
                        logger.info(f"사용자 로그인 성공: {email}")
                        st.rerun()
                    else:
                        st.error("이메일 또는 비밀번호가 올바르지 않습니다.")
                        logger.warning(f"로그인 실패: {email}")
                except Exception as e:
                    error_msg = f"로그인 중 오류가 발생했습니다: {e}"
                    logger.error(error_msg)
                    st.error(error_msg)
                    if st.session_state.debug_mode:
                        st.exception(e)
                        
    except Exception as e:
        error_msg = f"로그인 페이지 표시 중 오류: {e}"
        logger.error(error_msg)
        st.error(error_msg)
        if st.session_state.debug_mode:
            st.exception(e)

def show_signup_page():
    """회원가입 페이지"""
    try:
        st.header("📝 회원가입")
        
        # 비밀번호 요구사항 안내
        st.info("""
        **🔒 비밀번호 요구사항:**
        - 최소 8자 이상
        - 영문 대문자 포함 (A-Z)
        - 영문 소문자 포함 (a-z)
        - 숫자 포함 (0-9)
        - 특수문자 포함 (!@#$%^&*()_+-=[]{}|;:,.<>?)
        
        **✅ 예시:** `Password123!`, `MyPass456@`
        """)
        
        with st.form("signup_form"):
            username = st.text_input("👤 사용자명", placeholder="사용자명을 입력하세요")
            email = st.text_input("📧 이메일", placeholder="your@email.com")
            full_name = st.text_input("📛 실명", placeholder="실명을 입력하세요")
            password = st.text_input("🔒 비밀번호", type="password", placeholder="비밀번호를 입력하세요")
            password_confirm = st.text_input("🔒 비밀번호 확인", type="password", placeholder="비밀번호를 다시 입력하세요")
            
            submitted = st.form_submit_button("회원가입", use_container_width=True)
            
            if submitted:
                if not all([username, email, full_name, password, password_confirm]):
                    st.error("모든 필드를 입력해주세요.")
                elif password != password_confirm:
                    st.error("비밀번호가 일치하지 않습니다.")
                else:
                    try:
                        user = auth_service.signup(username, email, password, full_name)
                        if user:
                            st.success("회원가입 성공! 🎉 이제 로그인할 수 있습니다.")
                            st.info("로그인 탭에서 로그인해주세요.")
                            logger.info(f"새 사용자 회원가입 성공: {username} ({email})")
                        else:
                            st.error("회원가입에 실패했습니다. 비밀번호 요구사항을 확인해주세요.")
                            st.warning("💡 **비밀번호 예시:** `Password123!`, `MyPass456@`")
                            logger.warning(f"회원가입 실패: {username} ({email})")
                    except Exception as e:
                        error_msg = f"회원가입 중 오류가 발생했습니다: {e}"
                        logger.error(error_msg)
                        st.error(error_msg)
                        if st.session_state.debug_mode:
                            st.exception(e)
                            
    except Exception as e:
        error_msg = f"회원가입 페이지 표시 중 오류: {e}"
        logger.error(error_msg)
        st.error(error_msg)
        if st.session_state.debug_mode:
            st.exception(e)

def show_main_pages():
    """메인 페이지 표시"""
    try:
        if st.session_state.current_page == 'home':
            show_home_page()
        elif st.session_state.current_page == 'chat':
            show_chat_page()
        elif st.session_state.current_page == 'dashboard':
            show_dashboard_page()
        elif st.session_state.current_page == 'grammar':
            show_grammar_page()
        elif st.session_state.current_page == 'vocabulary':
            show_vocabulary_page()
        elif st.session_state.current_page == 'profile':
            show_profile_page()
            
    except Exception as e:
        error_msg = f"메인 페이지 표시 중 오류: {e}"
        logger.error(error_msg)
        st.error(error_msg)
        if st.session_state.debug_mode:
            st.exception(e)

def show_home_page():
    """홈 페이지"""
    try:
        st.header("🏠 홈")
        
        if st.session_state.is_authenticated:
            st.success(f"🎉 {st.session_state.user_info['full_name']}님, 영어 학습 AI 시스템에 오신 것을 환영합니다!")
            
            # 빠른 시작 카드
            col1, col2, col3 = st.columns(3)
            
            with col1:
                with st.container():
                    st.markdown("### 💬 AI 채팅")
                    st.markdown("영어 학습에 대해 AI와 대화해보세요!")
                    if st.button("채팅 시작", key="home_chat"):
                        st.session_state.current_page = 'chat'
                        st.rerun()
            
            with col2:
                with st.container():
                    st.markdown("### ✏️ 문법 검사")
                    st.markdown("영어 문장의 문법을 검사해보세요!")
                    if st.button("문법 검사", key="home_grammar"):
                        st.session_state.current_page = 'grammar'
                        st.rerun()
            
            with col3:
                with st.container():
                    st.markdown("### 📚 어휘 도움")
                    st.markdown("영어 텍스트의 어휘를 분석해보세요!")
                    if st.button("어휘 분석", key="home_vocab"):
                        st.session_state.current_page = 'vocabulary'
                        st.rerun()
            
            # 최근 활동
            st.markdown("---")
            st.subheader("📈 최근 활동")
            try:
                recent_activities = learning_service.get_recent_activities(st.session_state.user_id, limit=5)
                if recent_activities:
                    for activity in recent_activities:
                        st.markdown(f"- **{activity['activity_type']}**: {activity['description']} ({activity['created_at']})")
                else:
                    st.info("아직 학습 활동이 없습니다. 첫 번째 학습을 시작해보세요!")
            except Exception as e:
                st.warning(f"최근 활동을 불러올 수 없습니다: {e}")
                if st.session_state.debug_mode:
                    st.exception(e)
        else:
            st.info("로그인하여 모든 기능을 이용하세요!")
            
            # 체험 기능 안내
            st.markdown("### 🆓 체험 기능")
            st.markdown("로그인하지 않아도 AI 채팅을 체험해볼 수 있습니다!")
            
    except Exception as e:
        error_msg = f"홈 페이지 표시 중 오류: {e}"
        logger.error(error_msg)
        st.error(error_msg)
        if st.session_state.debug_mode:
            st.exception(e)

def show_chat_page():
    """AI 채팅 페이지"""
    try:
        st.header("💬 AI 채팅")
        
        # 채팅 히스토리 초기화
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # 채팅 히스토리 표시
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # 사용자 입력
        if prompt := st.chat_input("영어 학습에 대해 질문해보세요..."):
            # 사용자 메시지 추가
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # AI 응답 생성
            with st.chat_message("assistant"):
                with st.spinner("AI가 생각하고 있습니다..."):
                    try:
                        # Solar API 우선 사용 (한국어 성능이 좋음)
                        response = ai_service.get_response(prompt, use_solar=True)
                        st.markdown(response)
                        
                        # 채팅 히스토리에 추가
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        
                        # 학습 기록에 저장 (로그인된 사용자만)
                        if st.session_state.is_authenticated:
                            try:
                                learning_service.save_chat_message(
                                    st.session_state.user_id, 
                                    prompt, 
                                    response
                                )
                                logger.info(f"채팅 메시지 저장 완료: 사용자 {st.session_state.user_id}")
                            except Exception as e:
                                st.warning(f"학습 기록 저장에 실패했습니다: {e}")
                                logger.error(f"채팅 메시지 저장 실패: {e}")
                        
                    except Exception as e:
                        error_msg = f"AI 응답 생성 중 오류가 발생했습니다: {e}"
                        logger.error(error_msg)
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                        if st.session_state.debug_mode:
                            st.exception(e)
        
        # 채팅 히스토리 초기화 버튼
        if st.session_state.messages:
            if st.button("🗑️ 채팅 히스토리 초기화"):
                st.session_state.messages = []
                st.rerun()
                
    except Exception as e:
        error_msg = f"채팅 페이지 표시 중 오류: {e}"
        logger.error(error_msg)
        st.error(error_msg)
        if st.session_state.debug_mode:
            st.exception(e)

def show_dashboard_page():
    """학습 대시보드 페이지"""
    try:
        st.header("📊 학습 대시보드")
        
        if not st.session_state.is_authenticated:
            st.warning("로그인이 필요한 페이지입니다.")
            return
        
        try:
            # 사용자 통계
            stats = learning_service.get_user_stats(st.session_state.user_id)
            
            # 통계 카드
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("총 채팅 수", stats.get('total_chats', 0))
            
            with col2:
                st.metric("문법 검사 수", stats.get('total_grammar_checks', 0))
            
            with col3:
                st.metric("어휘 분석 수", stats.get('total_vocabulary_checks', 0))
            
            with col4:
                st.metric("학습 일수", stats.get('study_days', 0))
            
            # 주간 활동 차트
            st.markdown("---")
            st.subheader("📈 주간 활동")
            
            weekly_activities = learning_service.get_weekly_activities(st.session_state.user_id)
            if weekly_activities:
                import pandas as pd
                df = pd.DataFrame(list(weekly_activities.items()), columns=['요일', '활동 수'])
                st.bar_chart(df.set_index('요일'))
            else:
                st.info("아직 주간 활동 데이터가 없습니다.")
            
            # 최근 학습 기록
            st.markdown("---")
            st.subheader("📝 최근 학습 기록")
            
            recent_activities = learning_service.get_recent_activities(st.session_state.user_id, limit=10)
            if recent_activities:
                for activity in recent_activities:
                    st.markdown(f"- **{activity['activity_type']}**: {activity['description']} ({activity['created_at']})")
            else:
                st.info("아직 학습 기록이 없습니다.")
                
        except Exception as e:
            st.error(f"대시보드 데이터를 불러올 수 없습니다: {e}")
            if st.session_state.debug_mode:
                st.exception(e)
                
    except Exception as e:
        error_msg = f"대시보드 페이지 표시 중 오류: {e}"
        logger.error(error_msg)
        st.error(error_msg)
        if st.session_state.debug_mode:
            st.exception(e)

def show_grammar_page():
    """문법 검사 페이지"""
    try:
        st.header("✏️ 문법 검사")
        
        # 문법 검사 입력
        text_input = st.text_area(
            "영어 문장을 입력하세요",
            placeholder="검사할 영어 문장을 입력하세요...",
            height=150
        )
        
        if st.button("🔍 문법 검사", use_container_width=True):
            if text_input.strip():
                with st.spinner("문법을 검사하고 있습니다..."):
                    try:
                        # AI 서비스를 통한 문법 검사
                        prompt = ai_service.get_grammar_check_prompt(text_input)
                        result = ai_service.get_response(prompt, use_solar=True)
                        
                        # 결과 표시
                        st.markdown("## 📋 문법 검사 결과")
                        st.markdown(result)
                        
                        # 학습 기록에 저장 (로그인된 사용자만)
                        if st.session_state.is_authenticated:
                            try:
                                learning_service.save_grammar_check(
                                    st.session_state.user_id,
                                    text_input,
                                    result
                                )
                                st.success("✅ 문법 검사 결과가 학습 기록에 저장되었습니다.")
                                logger.info(f"문법 검사 저장 완료: 사용자 {st.session_state.user_id}")
                            except Exception as e:
                                st.warning(f"학습 기록 저장에 실패했습니다: {e}")
                                logger.error(f"문법 검사 저장 실패: {e}")
                        
                    except Exception as e:
                        st.error(f"문법 검사 중 오류가 발생했습니다: {e}")
                        if st.session_state.debug_mode:
                            st.exception(e)
            else:
                st.warning("검사할 텍스트를 입력해주세요.")
        
        # 이전 문법 검사 기록 (로그인된 사용자만)
        if st.session_state.is_authenticated:
            st.markdown("---")
            st.subheader("📚 이전 문법 검사 기록")
            
            try:
                grammar_checks = learning_service.get_grammar_checks(st.session_state.user_id, limit=5)
                if grammar_checks:
                    for check in grammar_checks:
                        with st.expander(f"📝 {check['created_at']}"):
                            st.markdown(f"**원문**: {check['original_text']}")
                            st.markdown(f"**결과**: {check['corrected_text']}")
                else:
                    st.info("아직 문법 검사 기록이 없습니다.")
            except Exception as e:
                st.warning(f"문법 검사 기록을 불러올 수 없습니다: {e}")
                if st.session_state.debug_mode:
                    st.exception(e)
                    
    except Exception as e:
        error_msg = f"문법 검사 페이지 표시 중 오류: {e}"
        logger.error(error_msg)
        st.error(error_msg)
        if st.session_state.debug_mode:
            st.exception(e)

def show_vocabulary_page():
    """어휘 도움 페이지"""
    try:
        st.header("📚 어휘 도움")
        
        # 어휘 분석 입력
        text_input = st.text_area(
            "분석할 영어 텍스트를 입력하세요",
            placeholder="어휘를 분석할 영어 텍스트를 입력하세요...",
            height=150
        )
        
        if st.button("🔍 어휘 분석", use_container_width=True):
            if text_input.strip():
                with st.spinner("어휘를 분석하고 있습니다..."):
                    try:
                        # AI 서비스를 통한 어휘 분석
                        prompt = ai_service.get_vocabulary_analysis_prompt(text_input)
                        result = ai_service.get_response(prompt, use_solar=True)
                        
                        # 결과 표시
                        st.markdown("## 📊 어휘 분석 결과")
                        st.markdown(result)
                        
                        # 학습 기록에 저장 (로그인된 사용자만)
                        if st.session_state.is_authenticated:
                            try:
                                learning_service.save_vocabulary_check(
                                    st.session_state.user_id,
                                    text_input,
                                    result
                                )
                                st.success("✅ 어휘 분석 결과가 학습 기록에 저장되었습니다.")
                                logger.info(f"어휘 분석 저장 완료: 사용자 {st.session_state.user_id}")
                            except Exception as e:
                                st.warning(f"학습 기록 저장에 실패했습니다: {e}")
                                logger.error(f"어휘 분석 저장 실패: {e}")
                        
                    except Exception as e:
                        st.error(f"어휘 분석 중 오류가 발생했습니다: {e}")
                        if st.session_state.debug_mode:
                            st.exception(e)
            else:
                st.warning("분석할 텍스트를 입력해주세요.")
        
        # 이전 어휘 분석 기록 (로그인된 사용자만)
        if st.session_state.is_authenticated:
            st.markdown("---")
            st.subheader("📚 이전 어휘 분석 기록")
            
            try:
                vocabulary_checks = learning_service.get_vocabulary_checks(st.session_state.user_id, limit=5)
                if vocabulary_checks:
                    for check in vocabulary_checks:
                        with st.expander(f"📚 {check['created_at']}"):
                            st.markdown(f"**원문**: {check['original_text']}")
                            st.markdown(f"**분석**: {check['analysis_result']}")
                else:
                    st.info("아직 어휘 분석 기록이 없습니다.")
            except Exception as e:
                st.warning(f"어휘 분석 기록을 불러올 수 없습니다: {e}")
                if st.session_state.debug_mode:
                    st.exception(e)
                    
    except Exception as e:
        error_msg = f"어휘 도움 페이지 표시 중 오류: {e}"
        logger.error(error_msg)
        st.error(error_msg)
        if st.session_state.debug_mode:
            st.exception(e)

def show_profile_page():
    """프로필 페이지"""
    try:
        st.header("👤 프로필")
        
        if not st.session_state.is_authenticated:
            st.warning("로그인이 필요한 페이지입니다.")
            return
        
        try:
            user_info = st.session_state.user_info
            
            # 사용자 정보
            st.subheader("📋 사용자 정보")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**👤 사용자명**: {user_info['username']}")
                st.markdown(f"**📧 이메일**: {user_info['email']}")
            
            with col2:
                st.markdown(f"**📛 실명**: {user_info['full_name']}")
                st.markdown(f"**📅 가입일**: {user_info['created_at']}")
            
            # 학습 통계 요약
            st.markdown("---")
            st.subheader("📊 학습 통계 요약")
            
            stats = learning_service.get_user_stats(st.session_state.user_id)
            progress = learning_service.get_learning_progress(st.session_state.user_id)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("총 학습 활동", stats.get('total_activities', 0))
            
            with col2:
                st.metric("학습 레벨", progress.get('level', '초급'))
            
            with col3:
                st.metric("학습 진행률", f"{progress.get('progress_percentage', 0)}%")
            
            # 비밀번호 변경
            st.markdown("---")
            st.subheader("🔒 비밀번호 변경")
            
            with st.form("password_change_form"):
                current_password = st.text_input("현재 비밀번호", type="password")
                new_password = st.text_input("새 비밀번호", type="password")
                new_password_confirm = st.text_input("새 비밀번호 확인", type="password")
                
                if st.form_submit_button("비밀번호 변경"):
                    if not all([current_password, new_password, new_password_confirm]):
                        st.error("모든 필드를 입력해주세요.")
                    elif new_password != new_password_confirm:
                        st.error("새 비밀번호가 일치하지 않습니다.")
                    else:
                        try:
                            if auth_service.change_password(st.session_state.user_id, current_password, new_password):
                                st.success("비밀번호가 성공적으로 변경되었습니다.")
                                logger.info(f"비밀번호 변경 완료: 사용자 {st.session_state.user_id}")
                            else:
                                st.error("현재 비밀번호가 올바르지 않습니다.")
                        except Exception as e:
                            st.error(f"비밀번호 변경 중 오류가 발생했습니다: {e}")
                            if st.session_state.debug_mode:
                                st.exception(e)
            
            # 계정 삭제
            st.markdown("---")
            st.subheader("⚠️ 계정 관리")
            
            if st.button("🗑️ 계정 삭제", type="secondary"):
                st.warning("정말로 계정을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.")
                
                if st.button("✅ 확인 - 계정 삭제", type="primary"):
                    try:
                        if auth_service.delete_account(st.session_state.user_id):
                            st.success("계정이 삭제되었습니다.")
                            logger.info(f"계정 삭제 완료: 사용자 {st.session_state.user_id}")
                            logout()
                            st.rerun()
                        else:
                            st.error("계정 삭제에 실패했습니다.")
                    except Exception as e:
                        st.error(f"계정 삭제 중 오류가 발생했습니다: {e}")
                        if st.session_state.debug_mode:
                            st.exception(e)
                            
        except Exception as e:
            st.error(f"프로필 정보를 불러올 수 없습니다: {e}")
            if st.session_state.debug_mode:
                st.exception(e)
                
    except Exception as e:
        error_msg = f"프로필 페이지 표시 중 오류: {e}"
        logger.error(error_msg)
        st.error(error_msg)
        if st.session_state.debug_mode:
            st.exception(e)

def logout():
    """로그아웃"""
    try:
        user_id = st.session_state.user_id
        st.session_state.user_id = None
        st.session_state.is_authenticated = False
        st.session_state.user_info = None
        st.session_state.current_page = 'home'
        st.session_state.messages = []
        st.success("로그아웃되었습니다.")
        logger.info(f"사용자 로그아웃: {user_id}")
    except Exception as e:
        logger.error(f"로그아웃 중 오류: {e}")

if __name__ == "__main__":
    main()
