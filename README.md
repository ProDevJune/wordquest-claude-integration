# WordQuest Claude Integration

## 📋 프로젝트 개요

**WordQuest Claude Integration**은 LangChain을 활용하여 Claude Code와 연동하는 영어 학습 질의응답 시스템입니다. 이 프로젝트는 Upstage AI Lab 7기 개인 과제로 개발되었으며, WordQuest 영어 학습 플랫폼과의 연동을 통해 실용적인 AI 애플리케이션을 구현합니다.

## 🎯 주요 기능

### 1. LangChain 기반 Claude Code 연동
- **Claude Code 모델**을 활용한 고성능 영어 학습 지원
- **LangChain 프레임워크**를 통한 체계적인 AI 애플리케이션 구현
- **Chain, Memory, Tool, Agent** 등 LangChain 핵심 기능 활용

### 2. 영어 질의응답 시스템
- 영어 문법, 어휘, 표현에 대한 실시간 질의응답
- 문맥을 고려한 맞춤형 학습 조언 제공
- 학습자 수준에 따른 적응형 답변 생성

### 3. WordQuest 연동 인터페이스
- WordQuest 플랫폼과의 원활한 연동
- 사용자 학습 데이터 기반 개인화된 답변
- 학습 진도 및 성과 분석 통합

## 🏗️ 프로젝트 구조

```
wordquest-claude-integration/
├── langchain-claude/           # LangChain + Claude Code 구현
│   ├── __init__.py
│   ├── claude_llm.py          # Claude Code LLM 래퍼
│   ├── chains.py              # LangChain 체인 구현
│   ├── memory.py              # 대화 메모리 관리
│   └── tools.py               # 커스텀 도구들
├── wordquest-connector/        # WordQuest 연동 인터페이스
│   ├── __init__.py
│   ├── api_client.py          # WordQuest API 클라이언트
│   ├── data_mapper.py         # 데이터 매핑 로직
│   └── auth.py                # 인증 처리
├── english-qa-system/          # 영어 질의응답 시스템
│   ├── __init__.py
│   ├── qa_engine.py           # 질의응답 엔진
│   ├── prompt_templates.py    # 프롬프트 템플릿
│   └── response_processor.py  # 응답 후처리
├── examples/                   # 사용 예시 및 데모
│   ├── basic_qa.py            # 기본 Q&A 예시
│   ├── wordquest_integration.py # WordQuest 연동 예시
│   └── advanced_features.py   # 고급 기능 데모
├── docs/                       # 문서
│   ├── setup_guide.md         # 설정 가이드
│   ├── api_reference.md       # API 레퍼런스
│   └── integration_guide.md   # WordQuest 연동 가이드
├── requirements.txt            # 의존성 관리
├── env.example                # 환경 변수 예시
└── README.md                  # 프로젝트 설명
```

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 프로젝트 클론
git clone https://github.com/ProDevJune/wordquest-claude-integration.git
cd wordquest-claude-integration

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

```bash
# 환경 변수 파일 복사
cp env.example .env

# .env 파일에서 API 키 설정
# ANTHROPIC_API_KEY=your_actual_api_key_here
```

### 3. 기본 사용 예시

```python
from langchain_claude.claude_llm import ClaudeLLM
from english_qa_system.qa_engine import EnglishQAEngine

# Claude Code LLM 초기화
claude_llm = ClaudeLLM()

# 영어 Q&A 엔진 초기화
qa_engine = EnglishQAEngine(claude_llm)

# 질의응답 실행
question = "What's the difference between 'affect' and 'effect'?"
response = qa_engine.ask(question)
print(response)
```

## 🔧 주요 컴포넌트

### LangChain Claude 모듈
- **ClaudeLLM**: Claude Code 모델을 LangChain LLM으로 래핑
- **EnglishQAChain**: 영어 학습에 특화된 체인 구현
- **ConversationMemory**: 대화 컨텍스트 메모리 관리
- **CustomTools**: 영어 학습 도구들 (문법 검사, 어휘 분석 등)

### WordQuest 연동 모듈
- **WordQuestAPIClient**: WordQuest API와의 통신
- **UserDataMapper**: 사용자 학습 데이터 매핑
- **LearningProgressTracker**: 학습 진도 추적

### 영어 Q&A 시스템
- **QuestionAnalyzer**: 질문 분석 및 분류
- **ResponseGenerator**: Claude Code를 활용한 응답 생성
- **AnswerValidator**: 답변 품질 검증

## 📚 사용 예시

### 기본 영어 질의응답

```python
from english_qa_system.qa_engine import EnglishQAEngine

qa_engine = EnglishQAEngine()

# 문법 질문
response = qa_engine.ask("When should I use 'who' vs 'whom'?")
print(response)

# 어휘 질문
response = qa_engine.ask("What's the difference between 'big' and 'large'?")
print(response)
```

### WordQuest 연동 활용

```python
from wordquest_connector.api_client import WordQuestAPIClient
from english_qa_system.qa_engine import EnglishQAEngine

# WordQuest API 클라이언트 초기화
wordquest_client = WordQuestAPIClient()

# 사용자 학습 데이터 가져오기
user_data = wordquest_client.get_user_learning_data(user_id="123")

# 개인화된 Q&A 엔진 초기화
qa_engine = EnglishQAEngine(user_context=user_data)

# 개인화된 질의응답
response = qa_engine.ask("I'm struggling with past perfect tense")
print(response)
```

## 🧪 테스트

```bash
# 전체 테스트 실행
pytest

# 특정 모듈 테스트
pytest tests/test_claude_llm.py
pytest tests/test_qa_engine.py
```

## 📖 문서

- [설정 가이드](docs/setup_guide.md)
- [API 레퍼런스](docs/api_reference.md)
- [WordQuest 연동 가이드](docs/integration_guide.md)

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 연락처

- **개발자**: ProDevJune
- **이메일**: [이메일 주소]
- **GitHub**: [https://github.com/ProDevJune](https://github.com/ProDevJune)

## 🙏 감사의 말

- [LangChain](https://github.com/langchain-ai/langchain) - 강력한 LLM 애플리케이션 프레임워크
- [Anthropic](https://www.anthropic.com/) - Claude Code 모델 제공
- [WordQuest](https://github.com/ProDevJune/WordQuest) - 영어 학습 플랫폼

---

**Upstage AI Lab 7기 개인 과제** - LangChain을 활용한 Claude Code 연동 프로젝트
