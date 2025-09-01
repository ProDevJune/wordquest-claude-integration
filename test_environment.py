#!/usr/bin/env python3
"""
WordQuest Claude Integration 환경 테스트 스크립트
"""

import os
import sys
from dotenv import load_dotenv


def test_python_version():
    """Python 버전 확인"""
    print("=== Python 버전 확인 ===")
    version = sys.version_info
    print(f"Python 버전: {version.major}.{version.minor}.{version.micro}")

    if version.major == 3 and version.minor >= 11:
        print("✅ Python 3.11+ 버전 확인 완료")
        return True
    else:
        print("❌ Python 3.11+ 버전이 필요합니다")
        return False


def test_environment_variables():
    """환경 변수 확인"""
    print("\n=== 환경 변수 확인 ===")
    load_dotenv()

    required_vars = ["ANTHROPIC_API_KEY", "ENVIRONMENT", "DEBUG", "LOG_LEVEL"]

    all_set = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if var == "ANTHROPIC_API_KEY":
                # API 키는 마스킹하여 표시
                masked_value = value[:10] + "..." if len(value) > 10 else "***"
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: 설정되지 않음")
            all_set = False

    return all_set


def test_imports():
    """필수 모듈 임포트 테스트"""
    print("\n=== 모듈 임포트 테스트 ===")

    modules_to_test = [
        ("langchain", "LangChain"),
        ("langchain_core", "LangChain Core"),
        ("langchain_anthropic", "LangChain Anthropic"),
        ("anthropic", "Anthropic"),
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("pydantic", "Pydantic"),
        ("sqlalchemy", "SQLAlchemy"),
        ("psycopg2", "PostgreSQL"),
        ("dotenv", "Python-dotenv"),
        ("loguru", "Loguru"),
        ("pytest", "Pytest"),
    ]

    all_imported = True
    for module_name, display_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {display_name}: 임포트 성공")
        except ImportError as e:
            print(f"❌ {display_name}: 임포트 실패 - {e}")
            all_imported = False

    return all_imported


def test_langchain_components():
    """LangChain 컴포넌트 테스트"""
    print("\n=== LangChain 컴포넌트 테스트 ===")

    try:
        from langchain_core.prompts import PromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from langchain_anthropic import ChatAnthropic

        # PromptTemplate 테스트
        PromptTemplate(
            input_variables=["question"], template="Answer this question: {question}"
        )
        print("✅ PromptTemplate: 생성 성공")

        # OutputParser 테스트
        StrOutputParser()
        print("✅ StrOutputParser: 생성 성공")

        # ChatAnthropic 테스트 (API 키 없이도 객체 생성 가능)
        try:
            ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                anthropic_api_key="test_key",  # 테스트용 키
            )
            print("✅ ChatAnthropic: 객체 생성 성공")
        except Exception as e:
            print(f"⚠️ ChatAnthropic: 객체 생성 실패 (API 키 필요) - {e}")

        return True

    except Exception as e:
        print(f"❌ LangChain 컴포넌트 테스트 실패: {e}")
        return False


def test_database_connection():
    """데이터베이스 연결 테스트"""
    print("\n=== 데이터베이스 연결 테스트 ===")

    try:
        import psycopg2

        # PostgreSQL 연결 테스트
        try:
            conn = psycopg2.connect(
                host="localhost",
                database="wordquest",
                user="jayden",
                password="",  # 비밀번호가 없는 경우
            )
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ PostgreSQL 연결 성공: {version[0][:50]}...")
            cursor.close()
            conn.close()
            return True

        except Exception as e:
            print(f"❌ PostgreSQL 연결 실패: {e}")
            return False

    except ImportError:
        print("❌ psycopg2 모듈을 찾을 수 없습니다")
        return False


def main():
    """메인 테스트 함수"""
    print("🚀 WordQuest Claude Integration 환경 테스트 시작\n")

    tests = [
        ("Python 버전", test_python_version),
        ("환경 변수", test_environment_variables),
        ("모듈 임포트", test_imports),
        ("LangChain 컴포넌트", test_langchain_components),
        ("데이터베이스 연결", test_database_connection),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 테스트 중 오류 발생: {e}")
            results.append((test_name, False))

    # 결과 요약
    print("\n" + "=" * 50)
    print("📊 테스트 결과 요약")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\n총 {total}개 테스트 중 {passed}개 통과")

    if passed == total:
        print("🎉 모든 테스트 통과! 개발 환경이 준비되었습니다.")
        return True
    else:
        print("⚠️ 일부 테스트 실패. 환경 설정을 확인해주세요.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
