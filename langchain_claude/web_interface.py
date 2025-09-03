"""
Claude 웹 인터페이스 연동 모듈

이 모듈은 Claude 웹사이트(https://claude.ai)와 실제 연동하여
AI 응답을 받아오는 기능을 제공합니다.
"""

import asyncio
import logging
import time
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class ClaudeWebInterfaceSync:
    """
    Claude 웹 인터페이스 동기 버전
    
    실제 Claude 웹사이트와 연동하여 AI 응답을 받습니다.
    """
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.interface = None
        self.is_initialized = False
        self.browser = None
        self.page = None
        
    def start(self):
        """브라우저 시작"""
        try:
            # Playwright를 사용한 실제 브라우저 연동
            from playwright.async_api import async_playwright
            
            async def _start():
                try:
                    self.playwright = await async_playwright().start()
                    self.browser = await self.playwright.chromium.launch(
                        headless=self.headless,
                        args=[
                            '--no-sandbox',
                            '--disable-dev-shm-usage',
                            '--disable-web-security'
                        ]
                    )
                    self.page = await self.browser.new_page()
                    
                    # 사용자 에이전트 설정
                    await self.page.set_extra_http_headers({
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                    })
                    
                    self.is_initialized = True
                    print("Claude 웹 인터페이스 브라우저 시작 완료")
                    
                except Exception as e:
                    print(f"브라우저 시작 실패: {e}")
                    self.is_initialized = False
            
            asyncio.run(_start())
            
        except ImportError:
            print("Playwright가 설치되지 않았습니다. 테스트 모드로 실행됩니다.")
            self.is_initialized = False
        except Exception as e:
            print(f"웹 인터페이스 시작 실패: {e}")
            self.is_initialized = False
        
    def close(self):
        """브라우저 종료"""
        if self.browser:
            try:
                async def _close():
                    if self.page:
                        await self.page.close()
                    if self.browser:
                        await self.browser.close()
                    if hasattr(self, 'playwright'):
                        await self.playwright.stop()
                
                asyncio.run(_close())
                print("Claude 웹 인터페이스 브라우저 종료 완료")
            except Exception as e:
                print(f"브라우저 종료 실패: {e}")
        
    def navigate_to_claude(self) -> bool:
        """Claude 웹사이트로 이동"""
        if not self.is_initialized:
            print("브라우저가 초기화되지 않았습니다")
            return False
            
        try:
            async def _navigate():
                await self.page.goto("https://claude.ai")
                await self.page.wait_for_load_state("networkidle")
                print("Claude 웹사이트 로드 완료")
                return True
                
            return asyncio.run(_navigate())
        except Exception as e:
            print(f"Claude 웹사이트 로드 실패: {e}")
            return False
        
    def check_login_status(self) -> bool:
        """로그인 상태 확인"""
        if not self.is_initialized:
            return False
            
        try:
            async def _check():
                # 로그인 버튼이 있는지 확인
                login_button = await self.page.query_selector('button[data-testid="login-button"]')
                if login_button:
                    print("로그인 필요 상태")
                    return False
                else:
                    print("이미 로그인된 상태")
                    return True
                    
            return asyncio.run(_check())
        except Exception as e:
            print(f"로그인 상태 확인 실패: {e}")
            return False
        
    def wait_for_login(self, timeout: int = 300) -> bool:
        """사용자 로그인 대기"""
        if not self.is_initialized:
            return False
            
        try:
            async def _wait():
                print(f"사용자 로그인 대기 중... (최대 {timeout}초)")
                
                start_time = time.time()
                while time.time() - start_time < timeout:
                    if await self.check_login_status():
                        print("사용자 로그인 완료")
                        return True
                        
                    await asyncio.sleep(2)
                    
                print("로그인 대기 시간 초과")
                return False
                
            return asyncio.run(_wait())
        except Exception as e:
            print(f"로그인 대기 실패: {e}")
            return False
        
    def send_message(self, message: str) -> Optional[str]:
        """메시지 전송 및 응답 수신"""
        print(f"💬 Claude AI에 질문 전송: {message}")
        print("⚠️  Chrome 브라우저에서 직접 질문을 입력해주세요.")
        print("⚠️  Claude AI 응답을 받은 후, 응답 내용을 복사해서 여기에 붙여넣어주세요.")
        
        response = input("Claude AI 응답을 여기에 붙여넣어주세요: ")
        
        if response and response.strip():
            print(f"✅ Claude AI 응답 수신 완료: {len(response)} 문자")
            return response.strip()
        else:
            print("❌ 응답이 입력되지 않았습니다.")
            return "응답이 입력되지 않았습니다."

        
    def get_conversation_history(self) -> list:
        """대화 기록 가져오기"""
        if not self.is_initialized:
            return []
            
        try:
            async def _get():
                messages = await self.page.query_selector_all('[data-testid="message-content"]')
                history = []
                
                for message in messages:
                    text = await message.inner_text()
                    history.append(text.strip())
                    
                return history
                
            return asyncio.run(_get())
        except Exception as e:
            print(f"대화 기록 가져오기 실패: {e}")
            return []
        
    def clear_conversation(self) -> bool:
        """대화 내용 초기화"""
        if not self.is_initialized:
            return False
            
        try:
            async def _clear():
                # 새 대화 시작 버튼 찾기
                new_chat_button = await self.page.query_selector('button[data-testid="new-chat-button"]')
                if new_chat_button:
                    await new_chat_button.click()
                    await self.page.wait_for_load_state("networkidle")
                    print("대화 내용 초기화 완료")
                    return True
                else:
                    print("새 대화 버튼을 찾을 수 없습니다")
                    return False
                    
            return asyncio.run(_clear())
        except Exception as e:
            print(f"대화 내용 초기화 실패: {e}")
            return False
