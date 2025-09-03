# WordQuest Claude Integration

## 📋 프로젝트 개요

**WordQuest Claude Integration**은 Streamlit을 활용하여 OpenAI와 Solar API를 연동하는 영어 학습 질의응답 시스템입니다. 이 프로젝트는 Upstage AI Lab 7기 개인 과제로 개발되었으며, WordQuest 영어 학습 플랫폼과의 연동을 통해 실용적인 AI 애플리케이션을 구현합니다.

## 🎯 주요 기능

### 1. AI 기반 영어 학습 시스템
- **OpenAI API**와 **Solar API**를 활용한 고성능 AI 응답
- **Streamlit** 기반의 직관적인 웹 인터페이스
- **실시간 AI 채팅**을 통한 영어 학습 지원

### 2. 영어 학습 도구
- **AI 채팅**: 실시간 영어 학습 대화
- **문법 검사**: AI 기반 영어 문법 검사 및 교정
- **어휘 도움**: 어휘 수준 분석 및 개선 제안
- **학습 대시보드**: 개인별 학습 진도 및 통계

### 3. 사용자 관리 시스템
- **회원가입/로그인**: JWT 기반 인증 시스템
- **프로필 관리**: 사용자 정보 및 설정 관리
- **학습 기록**: 모든 학습 활동의 자동 저장 및 추적

## 🏗️ 프로젝트 구조

```
wordquest-claude-integration/
├── main.py                    # Streamlit 메인 애플리케이션
├── run_app.py                 # 앱 실행 스크립트
├── app/                       # 애플리케이션 모듈
│   ├── core/                  # 핵심 기능
│   │   ├── config.py          # 설정 관리
│   │   ├── database.py        # WordQuest DB 연결
│   │   └── security.py        # 보안 및 인증
│   ├── services/              # 비즈니스 로직
│   │   ├── auth_service.py    # 사용자 인증
│   │   ├── ai_service.py      # AI API 연동
│   │   └── learning_service.py # 학습 데이터 관리
│   └── utils/                 # 유틸리티
├── langchain_claude/          # 기존 LangChain 모듈
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
OPENAI_API_KEY=your_openai_api_key_here
SOLAR_API_KEY=your_solar_api_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
```

### 3. 데이터베이스 설정

```bash
# WordQuest PostgreSQL 데이터베이스가 실행 중인지 확인
# 기본 설정: localhost:5432/wordquest
```

### 4. 앱 실행

```bash
# 실행 스크립트 사용 (권장)
python run_app.py

# 또는 직접 Streamlit 실행
streamlit run main.py --server.port 8001
```

## 🔧 주요 컴포넌트

### AI 서비스 (OpenAI + Solar API)
- **OpenAI API**: 안정적이고 성숙한 AI 서비스
- **Solar API**: 한국어 성능이 우수한 Upstage AI 서비스
- **이중 백업**: 한 API가 장애 시 다른 API로 자동 전환

### 사용자 인증 시스템
- **JWT 토큰**: 안전한 사용자 인증
- **비밀번호 해싱**: bcrypt를 사용한 보안 강화
- **입력 검증**: 사용자 입력의 안전성 보장

### 학습 데이터 관리
- **자동 저장**: 모든 학습 활동의 자동 기록
- **진도 추적**: 개인별 학습 진도 및 통계
- **WordQuest DB 공유**: 기존 데이터베이스 활용

## 📚 사용 예시

### AI 채팅
- 실시간으로 AI와 영어 학습 대화
- 한국어/영어 혼용 질문 가능
- Solar API 선택으로 한국어 성능 향상

### 문법 검사
- 영어 문장/문단 입력
- AI 기반 문법 오류 검사 및 교정
- 개선 제안 및 학습 포인트 제공

### 어휘 도움
- 영어 텍스트 어휘 수준 분석
- 어려운 단어 상세 설명
- 학습 추천 단어 및 전략 제시

## 🧪 테스트

```bash
# 환경 테스트
python test_environment.py

# 앱 실행 테스트
python run_app.py
```

## 📖 문서

- [설정 가이드](docs/setup-guide.md)
- [API 레퍼런스](docs/api-reference.md)
- [기술 설계](docs/technical-design.md)

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
- **GitHub**: [https://github.com/ProDevJune](https://github.com/ProDevJune)

## 🙏 감사의 말

- [Streamlit](https://streamlit.io/) - 빠르고 직관적인 웹앱 개발
- [OpenAI](https://openai.com/) - GPT 모델 제공
- [Upstage](https://upstage.ai/) - Solar API 제공
- [WordQuest](https://github.com/ProDevJune/WordQuest) - 영어 학습 플랫폼

---

**Upstage AI Lab 7기 개인 과제** - Streamlit 기반 OpenAI + Solar API 연동 프로젝트
