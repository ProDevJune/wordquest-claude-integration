# WordQuest Claude Integration API 레퍼런스

## 📚 개요

이 문서는 WordQuest Claude Integration 프로젝트의 모든 API 인터페이스와 사용법을 설명합니다. LangChain 기반의 Claude Code 연동 시스템으로, 영어 학습을 위한 질의응답 서비스를 제공합니다.

## 🏗️ 모듈 구조

```
wordquest-claude-integration/
├── langchain-claude/           # LangChain + Claude Code 핵심
├── english-qa-system/          # 영어 Q&A 시스템
├── wordquest-connector/        # WordQuest 연동 인터페이스
├── utils/                      # 유틸리티 및 헬퍼
└── security/                   # 보안 및 인증
```

## 🔧 LangChain Claude 모듈

### ClaudeCodeLLM

Claude Code 모델을 LangChain LLM으로 래핑하는 클래스입니다.

#### 클래스 정의
```python
class ClaudeCodeLLM(BaseLLM):
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022")
```

#### 매개변수
- **api_key** (str): Anthropic API 키
- **model** (str): 사용할 Claude 모델명 (기본값: claude-3-5-sonnet-20241022)

#### 메서드

##### `_call(prompt: str, stop: Optional[List[str]] = None) -> str`
텍스트 생성 요청을 처리합니다.

**매개변수:**
- **prompt** (str): 입력 프롬프트
- **stop** (Optional[List[str]]): 생성 중단 토큰 리스트

**반환값:**
- **str**: 생성된 텍스트

**사용 예시:**
```python
from langchain_claude import ClaudeCodeLLM

llm = ClaudeCodeLLM(api_key="your_api_key")
response = llm._call("What is the difference between 'affect' and 'effect'?")
print(response)
```

#### 속성

##### `_llm_type: str`
LLM 타입을 반환합니다. 항상 "claude_code"를 반환합니다.

### ClaudeIntegrationCore

Claude Code와 LangChain을 통합하는 핵심 클래스입니다.

#### 클래스 정의
```python
class ClaudeIntegrationCore:
    def __init__(self, api_key: str)
```

#### 매개변수
- **api_key** (str): Anthropic API 키

#### 메서드

##### `ask(question: str, context: str = "") -> str`
질문에 대한 답변을 생성합니다.

**매개변수:**
- **question** (str): 사용자 질문
- **context** (str): 추가 컨텍스트 정보 (기본값: "")

**반환값:**
- **str**: 생성된 답변

**사용 예시:**
```python
from langchain_claude import ClaudeIntegrationCore

core = ClaudeIntegrationCore(api_key="your_api_key")
answer = core.ask(
    "When should I use present perfect tense?",
    context="I'm learning English grammar basics"
)
print(answer)
```

## 🎯 영어 Q&A 시스템

### EnglishQAEngine

영어 학습을 위한 질의응답 엔진입니다.

#### 클래스 정의
```python
class EnglishQAEngine:
    def __init__(self, llm, memory: Optional[BaseMemory] = None)
```

#### 매개변수
- **llm**: LangChain LLM 객체
- **memory** (Optional[BaseMemory]): 대화 메모리 (기본값: None)

#### 메서드

##### `ask(question: str, user_context: Optional[Dict] = None) -> str`
영어 학습 질문에 대한 답변을 생성합니다.

**매개변수:**
- **question** (str): 영어 학습 관련 질문
- **user_context** (Optional[Dict]): 사용자 학습 컨텍스트

**반환값:**
- **str**: 학습에 최적화된 답변

**사용 예시:**
```python
from english_qa_system import EnglishQAEngine
from langchain_claude import ClaudeCodeLLM

llm = ClaudeCodeLLM(api_key="your_api_key")
qa_engine = EnglishQAEngine(llm)

# 기본 질문
answer = qa_engine.ask("What's the difference between 'big' and 'large'?")

# 컨텍스트가 있는 질문
user_context = {
    "level": "intermediate",
    "topics": ["vocabulary", "synonyms"],
    "weak_areas": ["prepositions"]
}
answer = qa_engine.ask(
    "How can I improve my preposition usage?",
    user_context=user_context
)
```

##### `ask_async(question: str, user_context: Optional[Dict] = None) -> str`
비동기로 질문에 대한 답변을 생성합니다.

**매개변수:**
- **question** (str): 영어 학습 관련 질문
- **user_context** (Optional[Dict]): 사용자 학습 컨텍스트

**반환값:**
- **str**: 학습에 최적화된 답변

**사용 예시:**
```python
import asyncio

async def get_answer():
    answer = await qa_engine.ask_async(
        "Explain the passive voice in English",
        user_context={"level": "advanced"}
    )
    return answer

answer = asyncio.run(get_answer())
```

### Custom Tools

영어 학습을 위한 커스텀 도구들입니다.

#### GrammarCheckerTool

문법 검사 및 교정을 제공하는 도구입니다.

```python
class GrammarCheckerTool(BaseTool):
    name = "grammar_checker"
    description = "Check English grammar and provide corrections"
```

**사용 예시:**
```python
from english_qa_system.tools import GrammarCheckerTool

grammar_tool = GrammarCheckerTool()
result = grammar_tool.run("I goes to school everyday")
print(result)  # "I go to school everyday" (correction)
```

#### VocabularyAnalyzerTool

어휘 수준 분석 및 개선 제안을 제공하는 도구입니다.

```python
class VocabularyAnalyzerTool(BaseTool):
    name = "vocabulary_analyzer"
    description = "Analyze vocabulary level and suggest improvements"
```

**사용 예시:**
```python
from english_qa_system.tools import VocabularyAnalyzerTool

vocab_tool = VocabularyAnalyzerTool()
result = vocab_tool.run("The weather is nice today")
print(result)  # 어휘 수준 분석 및 개선 제안
```

## 🔗 WordQuest 연동 인터페이스

### WordQuestAPIClient

WordQuest 플랫폼과의 API 통신을 담당하는 클라이언트입니다.

#### 클래스 정의
```python
class WordQuestAPIClient:
    def __init__(self, base_url: str, api_key: str)
```

#### 매개변수
- **base_url** (str): WordQuest API 기본 URL
- **api_key** (str): WordQuest API 인증 키

#### 메서드

##### `get_user_learning_data(user_id: str) -> Dict`
사용자의 학습 데이터를 조회합니다.

**매개변수:**
- **user_id** (str): 사용자 ID

**반환값:**
- **Dict**: 사용자 학습 데이터

**반환 데이터 구조:**
```json
{
    "user_id": "123",
    "current_level": "intermediate",
    "topics": ["grammar", "vocabulary", "pronunciation"],
    "weak_areas": ["prepositions", "tenses"],
    "goals": ["fluent conversation", "business English"],
    "recent_activities": [
        {
            "type": "quiz",
            "score": 85,
            "date": "2025-09-01T10:00:00Z"
        }
    ]
}
```

**사용 예시:**
```python
from wordquest_connector import WordQuestAPIClient

client = WordQuestAPIClient(
    base_url="http://localhost:8000",
    api_key="your_wordquest_api_key"
)

user_data = await client.get_user_learning_data("user123")
print(f"User level: {user_data['current_level']}")
```

##### `update_learning_progress(user_id: str, progress: Dict) -> Dict`
사용자의 학습 진도를 업데이트합니다.

**매개변수:**
- **user_id** (str): 사용자 ID
- **progress** (Dict): 업데이트할 학습 진도 데이터

**진도 데이터 구조:**
```json
{
    "topic": "grammar",
    "score": 90,
    "time_spent": 1800,
    "questions_answered": 15,
    "correct_answers": 13
}
```

**반환값:**
- **Dict**: 업데이트 결과

**사용 예시:**
```python
progress_data = {
    "topic": "vocabulary",
    "score": 85,
    "time_spent": 1200,
    "questions_answered": 20,
    "correct_answers": 17
}

result = await client.update_learning_progress("user123", progress_data)
print(f"Progress updated: {result['status']}")
```

### WordQuestDataMapper

WordQuest 데이터와 Claude Integration 데이터 간의 변환을 담당합니다.

#### 클래스 정의
```python
class WordQuestDataMapper
```

#### 정적 메서드

##### `map_user_context(wordquest_data: Dict) -> Dict`
WordQuest 데이터를 Claude Integration 컨텍스트로 변환합니다.

**매개변수:**
- **wordquest_data** (Dict): WordQuest 사용자 데이터

**반환값:**
- **Dict**: Claude Integration용 컨텍스트

**사용 예시:**
```python
from wordquest_connector import WordQuestDataMapper

mapper = WordQuestDataMapper()
context = mapper.map_user_context(user_data)

qa_engine = EnglishQAEngine(llm)
answer = qa_engine.ask("How can I improve?", user_context=context)
```

##### `map_qa_response(claude_response: str, user_id: str) -> Dict`
Claude 응답을 WordQuest 형식으로 변환합니다.

**매개변수:**
- **claude_response** (str): Claude API 응답
- **user_id** (str): 사용자 ID

**반환값:**
- **Dict**: WordQuest 형식의 응답 데이터

## 🚀 실시간 채팅 시스템

### ChatManager

WebSocket 기반 실시간 채팅을 관리하는 클래스입니다.

#### 클래스 정의
```python
class ChatManager:
    def __init__(self)
```

#### 메서드

##### `connect(websocket: WebSocket, user_id: str)`
새로운 WebSocket 연결을 수락하고 사용자 세션을 생성합니다.

**매개변수:**
- **websocket** (WebSocket): WebSocket 연결 객체
- **user_id** (str): 사용자 ID

**사용 예시:**
```python
from fastapi import WebSocket
from english_qa_system import ChatManager

chat_manager = ChatManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await chat_manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # 메시지 처리
    except:
        await chat_manager.disconnect(websocket, user_id)
```

##### `disconnect(websocket: WebSocket, user_id: str)`
WebSocket 연결을 종료하고 사용자 세션을 정리합니다.

**매개변수:**
- **websocket** (WebSocket): WebSocket 연결 객체
- **user_id** (str): 사용자 ID

##### `send_message(user_id: str, message: str)`
특정 사용자에게 메시지를 전송합니다.

**매개변수:**
- **user_id** (str): 메시지를 받을 사용자 ID
- **message** (str): 전송할 메시지

### MessageProcessor

채팅 메시지를 처리하고 응답을 생성하는 클래스입니다.

#### 클래스 정의
```python
class MessageProcessor:
    def __init__(self, qa_engine: EnglishQAEngine)
```

#### 매개변수
- **qa_engine** (EnglishQAEngine): 영어 Q&A 엔진

#### 메서드

##### `process_message(user_id: str, message: str, context: Dict) -> str`
사용자 메시지를 처리하고 응답을 생성합니다.

**매개변수:**
- **user_id** (str): 사용자 ID
- **message** (str): 사용자 메시지
- **context** (Dict): 사용자 컨텍스트

**반환값:**
- **str**: 생성된 응답

**사용 예시:**
```python
from english_qa_system import MessageProcessor

processor = MessageProcessor(qa_engine)

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await chat_manager.connect(websocket, user_id)
    
    # 사용자 컨텍스트 로드
    user_context = await wordquest_client.get_user_learning_data(user_id)
    
    try:
        while True:
            message = await websocket.receive_text()
            response = await processor.process_message(user_id, message, user_context)
            await websocket.send_text(response)
    except:
        await chat_manager.disconnect(websocket, user_id)
```

## 🛠️ 유틸리티 및 헬퍼

### CacheManager

Redis 기반 캐싱 시스템을 관리하는 클래스입니다.

#### 클래스 정의
```python
class CacheManager:
    def __init__(self, redis_url: str = "redis://localhost:6379")
```

#### 매개변수
- **redis_url** (str): Redis 연결 URL

#### 메서드

##### `get(key: str) -> Optional[Any]`
캐시에서 데이터를 조회합니다.

**매개변수:**
- **key** (str): 캐시 키

**반환값:**
- **Optional[Any]**: 캐시된 데이터 또는 None

##### `set(key: str, value: Any, ttl: int = None) -> bool`
캐시에 데이터를 저장합니다.

**매개변수:**
- **key** (str): 캐시 키
- **value** (Any): 저장할 데이터
- **ttl** (int): TTL (초), 기본값은 1시간

**반환값:**
- **bool**: 저장 성공 여부

**사용 예시:**
```python
from utils import CacheManager

cache = CacheManager()

# 데이터 캐싱
cache.set("user_123_context", user_context, ttl=1800)  # 30분

# 캐시된 데이터 조회
cached_context = cache.get("user_123_context")
if cached_context:
    print("Using cached context")
else:
    print("Loading fresh context")
```

### AsyncProcessor

비동기 작업 처리를 최적화하는 클래스입니다.

#### 클래스 정의
```python
class AsyncProcessor:
    def __init__(self, max_workers: int = 4)
```

#### 매개변수
- **max_workers** (int): 최대 워커 스레드 수

#### 메서드

##### `process_batch(tasks: List[Callable], *args) -> List[Any]`
배치 작업을 비동기로 처리합니다.

**매개변수:**
- **tasks** (List[Callable]): 실행할 작업 리스트
- **args**: 작업에 전달할 인자들

**반환값:**
- **List[Any]**: 작업 결과 리스트

**사용 예시:**
```python
from utils import AsyncProcessor

processor = AsyncProcessor(max_workers=4)

def analyze_text(text):
    # 텍스트 분석 작업
    return {"length": len(text), "words": len(text.split())}

texts = ["Hello world", "Python programming", "AI and ML"]
tasks = [analyze_text] * len(texts)

results = await processor.process_batch(tasks, texts)
print(results)
```

## 🔒 보안 및 인증

### AuthManager

JWT 기반 인증을 관리하는 클래스입니다.

#### 클래스 정의
```python
class AuthManager:
    def __init__(self, secret_key: str)
```

#### 매개변수
- **secret_key** (str): JWT 서명에 사용할 비밀키

#### 메서드

##### `verify_token(credentials: HTTPAuthorizationCredentials) -> Dict`
JWT 토큰을 검증하고 페이로드를 반환합니다.

**매개변수:**
- **credentials** (HTTPAuthorizationCredentials): HTTP 인증 헤더

**반환값:**
- **Dict**: 토큰 페이로드

**사용 예시:**
```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from security import AuthManager

auth_manager = AuthManager(secret_key="your_secret_key")

@app.get("/protected")
async def protected_endpoint(token: Dict = Depends(auth_manager.verify_token)):
    user_id = token.get("user_id")
    return {"message": f"Hello user {user_id}"}
```

### RateLimiter

API 요청 제한을 관리하는 클래스입니다.

#### 클래스 정의
```python
class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600)
```

#### 매개변수
- **max_requests** (int): 윈도우 시간 내 최대 요청 수
- **window_seconds** (int): 윈도우 시간 (초)

#### 메서드

##### `is_allowed(user_id: str) -> bool`
사용자의 요청이 허용되는지 확인합니다.

**매개변수:**
- **user_id** (str): 사용자 ID

**반환값:**
- **bool**: 요청 허용 여부

**사용 예시:**
```python
from security import RateLimiter

rate_limiter = RateLimiter(max_requests=100, window_seconds=3600)

@app.post("/api/qa")
async def ask_question(request: QARequest, user_id: str):
    if not rate_limiter.is_allowed(user_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # 질문 처리
    response = await qa_engine.ask(request.question)
    return {"answer": response}
```

## 📊 에러 코드 및 응답

### HTTP 상태 코드

| 코드 | 의미 | 설명 |
|------|------|------|
| 200 | OK | 요청 성공 |
| 201 | Created | 리소스 생성 성공 |
| 400 | Bad Request | 잘못된 요청 |
| 401 | Unauthorized | 인증 실패 |
| 403 | Forbidden | 권한 부족 |
| 404 | Not Found | 리소스 없음 |
| 429 | Too Many Requests | 요청 제한 초과 |
| 500 | Internal Server Error | 서버 내부 오류 |

### 에러 응답 형식

```json
{
    "error": {
        "code": "INVALID_INPUT",
        "message": "Invalid question format",
        "details": "Question must be a non-empty string"
    },
    "timestamp": "2025-09-01T22:30:00Z",
    "request_id": "req_123456789"
}
```

### 에러 코드 목록

| 코드 | 의미 | HTTP 상태 코드 |
|------|------|----------------|
| INVALID_INPUT | 잘못된 입력 | 400 |
| UNAUTHORIZED | 인증 실패 | 401 |
| FORBIDDEN | 권한 부족 | 403 |
| RESOURCE_NOT_FOUND | 리소스 없음 | 404 |
| RATE_LIMIT_EXCEEDED | 요청 제한 초과 | 429 |
| INTERNAL_ERROR | 서버 내부 오류 | 500 |
| CLAUDE_API_ERROR | Claude API 오류 | 502 |
| WORDQUEST_API_ERROR | WordQuest API 오류 | 502 |

## 🧪 테스트 및 디버깅

### 단위 테스트 실행

```bash
# 전체 테스트 실행
pytest

# 특정 모듈 테스트
pytest tests/test_claude_llm.py
pytest tests/test_qa_engine.py

# 커버리지 포함 테스트
pytest --cov=langchain_claude --cov=english_qa_system
```

### 통합 테스트 실행

```bash
# API 통합 테스트
pytest tests/integration/test_api.py

# WordQuest 연동 테스트
pytest tests/integration/test_wordquest_connector.py
```

### 디버깅 모드 활성화

```python
import logging

# 디버그 로깅 활성화
logging.basicConfig(level=logging.DEBUG)

# 특정 모듈 로깅 활성화
logging.getLogger("langchain_claude").setLevel(logging.DEBUG)
```

---

**문서 버전**: 1.0  
**작성일**: 2025년 9월 1일  
**작성자**: ProDevJune  
**검토자**: -  
**다음 업데이트**: 구현 완료 후
