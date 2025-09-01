# WordQuest Claude Integration 기술 설계서

## 🏗️ 시스템 아키텍처 상세 설계

### 1. LangChain 모듈 설계

#### 1.1 Core Components
```python
# langchain-claude/core.py
from langchain_core.language_models import BaseLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

class ClaudeIntegrationCore:
    def __init__(self, api_key: str):
        self.llm = ClaudeCodeLLM(api_key=api_key)
        self.prompt_template = PromptTemplate(
            input_variables=["question", "context"],
            template="You are an expert English teacher. Answer the following question: {question}\nContext: {context}"
        )
        self.chain = self.prompt_template | self.llm | StrOutputParser()
```

#### 1.2 Claude Code LLM Wrapper
```python
# langchain-claude/claude_llm.py
import anthropic
from langchain_core.language_models import BaseLLM
from langchain_core.outputs import Generation, LLMResult

class ClaudeCodeLLM(BaseLLM):
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        super().__init__()
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    
    @property
    def _llm_type(self) -> str:
        return "claude_code"
```

### 2. 영어 Q&A 시스템 설계

#### 2.1 Q&A Engine Architecture
```python
# english-qa-system/qa_engine.py
from typing import Dict, List, Optional
from langchain_core.memory import BaseMemory
from langchain_core.tools import BaseTool

class EnglishQAEngine:
    def __init__(self, llm, memory: Optional[BaseMemory] = None):
        self.llm = llm
        self.memory = memory or ConversationBufferMemory()
        self.tools = self._initialize_tools()
        self.agent = self._create_agent()
    
    def _initialize_tools(self) -> List[BaseTool]:
        return [
            GrammarCheckerTool(),
            VocabularyAnalyzerTool(),
            PronunciationGuideTool(),
            LearningPathTool()
        ]
    
    def ask(self, question: str, user_context: Optional[Dict] = None) -> str:
        # 질문 분석 및 분류
        question_type = self._analyze_question(question)
        
        # 컨텍스트 기반 응답 생성
        response = self.agent.run({
            "question": question,
            "question_type": question_type,
            "user_context": user_context,
            "conversation_history": self.memory.load_memory_variables({})
        })
        
        # 메모리에 대화 저장
        self.memory.save_context(
            {"input": question},
            {"output": response}
        )
        
        return response
```

#### 2.2 Custom Tools 구현
```python
# english-qa-system/tools.py
from langchain_core.tools import BaseTool
from typing import Optional

class GrammarCheckerTool(BaseTool):
    name = "grammar_checker"
    description = "Check English grammar and provide corrections"
    
    def _run(self, text: str) -> str:
        prompt = f"Please check the grammar of this text and provide corrections: {text}"
        return self.llm.predict(prompt)

class VocabularyAnalyzerTool(BaseTool):
    name = "vocabulary_analyzer"
    description = "Analyze vocabulary level and suggest improvements"
    
    def _run(self, text: str) -> str:
        prompt = f"Analyze the vocabulary level of this text and suggest improvements: {text}"
        return self.llm.predict(prompt)
```

### 3. WordQuest 연동 인터페이스 설계

#### 3.1 API Client 설계
```python
# wordquest-connector/api_client.py
import httpx
from typing import Dict, List, Optional

class WordQuestAPIClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {api_key}"}
        )
    
    async def get_user_learning_data(self, user_id: str) -> Dict:
        """사용자 학습 데이터 조회"""
        response = await self.client.get(
            f"{self.base_url}/api/users/{user_id}/learning-data"
        )
        return response.json()
    
    async def update_learning_progress(self, user_id: str, progress: Dict) -> Dict:
        """학습 진도 업데이트"""
        response = await self.client.post(
            f"{self.base_url}/api/users/{user_id}/progress",
            json=progress
        )
        return response.json()
```

#### 3.2 데이터 매핑 및 변환
```python
# wordquest-connector/data_mapper.py
from typing import Dict, List

class WordQuestDataMapper:
    @staticmethod
    def map_user_context(wordquest_data: Dict) -> Dict:
        """WordQuest 데이터를 Claude Integration 컨텍스트로 변환"""
        return {
            "user_level": wordquest_data.get("current_level", "beginner"),
            "learning_topics": wordquest_data.get("topics", []),
            "weak_areas": wordquest_data.get("weak_areas", []),
            "learning_goals": wordquest_data.get("goals", []),
            "recent_activities": wordquest_data.get("recent_activities", [])
        }
    
    @staticmethod
    def map_qa_response(claude_response: str, user_id: str) -> Dict:
        """Claude 응답을 WordQuest 형식으로 변환"""
        return {
            "user_id": user_id,
            "question": claude_response.get("question"),
            "answer": claude_response.get("answer"),
            "confidence": claude_response.get("confidence", 0.9),
            "timestamp": datetime.utcnow().isoformat(),
            "learning_points": claude_response.get("learning_points", [])
        }
```

### 4. 실시간 채팅 시스템 설계

#### 4.1 WebSocket 기반 채팅
```python
# english-qa-system/chat_system.py
import asyncio
from fastapi import WebSocket
from typing import Dict, List

class ChatManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_sessions: Dict[str, Dict] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.user_sessions[user_id] = {"websocket": websocket, "context": {}}
    
    async def disconnect(self, websocket: WebSocket, user_id: str):
        self.active_connections.remove(websocket)
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
    
    async def send_message(self, user_id: str, message: str):
        if user_id in self.user_sessions:
            websocket = self.user_sessions[user_id]["websocket"]
            await websocket.send_text(message)
```

#### 4.2 메시지 처리 및 응답
```python
# english-qa-system/message_processor.py
class MessageProcessor:
    def __init__(self, qa_engine: EnglishQAEngine):
        self.qa_engine = qa_engine
    
    async def process_message(self, user_id: str, message: str, context: Dict) -> str:
        # 메시지 전처리
        processed_message = self._preprocess_message(message)
        
        # Q&A 엔진을 통한 응답 생성
        response = await self.qa_engine.ask_async(
            processed_message, 
            user_context=context
        )
        
        # 응답 후처리
        formatted_response = self._format_response(response)
        
        return formatted_response
```

### 5. 성능 최적화 전략

#### 5.1 캐싱 시스템
```python
# utils/cache_manager.py
import redis
from typing import Any, Optional
import json

class CacheManager:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url)
        self.default_ttl = 3600  # 1시간
    
    def get(self, key: str) -> Optional[Any]:
        """캐시에서 데이터 조회"""
        data = self.redis_client.get(key)
        return json.loads(data) if data else None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """캐시에 데이터 저장"""
        ttl = ttl or self.default_ttl
        return self.redis_client.setex(
            key, 
            ttl, 
            json.dumps(value)
        )
```

#### 5.2 비동기 처리 최적화
```python
# utils/async_processor.py
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Callable, Any

class AsyncProcessor:
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    async def process_batch(self, tasks: List[Callable], *args) -> List[Any]:
        """배치 작업 비동기 처리"""
        loop = asyncio.get_event_loop()
        
        # ThreadPoolExecutor를 사용한 비동기 실행
        futures = [
            loop.run_in_executor(self.executor, task, *args)
            for task in tasks
        ]
        
        results = await asyncio.gather(*futures)
        return results
```

### 6. 보안 및 인증 설계

#### 6.1 API 인증
```python
# security/auth.py
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from typing import Optional

class AuthManager:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.security = HTTPBearer()
    
    async def verify_token(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> Dict:
        """JWT 토큰 검증"""
        try:
            payload = jwt.decode(
                credentials.credentials, 
                self.secret_key, 
                algorithms=["HS256"]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
```

#### 6.2 Rate Limiting
```python
# security/rate_limiter.py
import time
from collections import defaultdict
from typing import Dict, Tuple

class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = defaultdict(list)
    
    def is_allowed(self, user_id: str) -> bool:
        """사용자 요청 제한 확인"""
        now = time.time()
        user_requests = self.requests[user_id]
        
        # 윈도우 시간 이전의 요청 제거
        user_requests = [req_time for req_time in user_requests 
                        if now - req_time < self.window_seconds]
        
        if len(user_requests) >= self.max_requests:
            return False
        
        # 새 요청 추가
        user_requests.append(now)
        self.requests[user_id] = user_requests
        return True
```

## 🔧 구현 우선순위 및 일정

### Phase 1: 핵심 기능 (9월 2일)
- [ ] LangChain 기본 구조 구현
- [ ] Claude Code API 연동
- [ ] 기본 Q&A 엔진 구현
- [ ] 단위 테스트 작성

### Phase 2: 고급 기능 (9월 3일 오전)
- [ ] Memory 및 Tool 구현
- [ ] WordQuest 연동 인터페이스
- [ ] 실시간 채팅 기능
- [ ] 통합 테스트

### Phase 3: 최적화 및 배포 (9월 3일 오후)
- [ ] 성능 최적화
- [ ] 보안 강화
- [ ] 문서화 완성
- [ ] GitHub 배포

---

**문서 버전**: 1.0  
**작성일**: 2025년 9월 1일  
**작성자**: ProDevJune  
**검토자**: -
