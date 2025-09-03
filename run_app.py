#!/usr/bin/env python3
"""
WordQuest Claude Integration - Streamlit 앱 실행 스크립트
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """메인 실행 함수"""
    print("🚀 WordQuest Claude Integration - Streamlit 앱 시작")
    print("=" * 60)
    
    # 프로젝트 루트 확인
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # 환경 변수 파일 확인
    env_file = project_root / ".env"
    if not env_file.exists():
        print("❌ .env 파일이 없습니다.")
        print("env.example을 복사하여 .env 파일을 생성하고 필요한 설정을 입력해주세요.")
        return False
    
    # Python 3.11 가상환경 확인
    venv_path = project_root / "venv_py311"
    if not venv_path.exists():
        print("❌ Python 3.11 가상환경이 없습니다.")
        print("다음 명령어로 가상환경을 생성해주세요:")
        print("python3.11 -m venv venv_py311")
        print("source venv_py311/bin/activate")
        return False
    
    # 가상환경 활성화
    activate_script = venv_path / "bin" / "activate_this.py"
    if activate_script.exists():
        exec(activate_script.read_text(), {'__file__': str(activate_script)})
        print("✅ Python 3.11 가상환경 활성화 완료")
    else:
        print("❌ 가상환경 활성화 스크립트를 찾을 수 없습니다.")
        return False
    
    # 의존성 설치 확인
    try:
        import streamlit
        print("✅ Streamlit이 설치되어 있습니다.")
    except ImportError:
        print("❌ Streamlit이 설치되지 않았습니다.")
        print("다음 명령어로 의존성을 설치해주세요:")
        print("source venv_py311/bin/activate")
        print("pip install -r requirements.txt")
        return False
    
    # 데이터베이스 연결 테스트
    try:
        from app.core.database import get_db
        db = get_db()
        if db.test_connection():
            print("✅ 데이터베이스 연결 성공")
        else:
            print("❌ 데이터베이스 연결 실패")
            print("WordQuest 데이터베이스가 실행 중인지 확인해주세요.")
            return False
    except Exception as e:
        print(f"❌ 데이터베이스 연결 테스트 실패: {e}")
        return False
    
    # 필요한 테이블 생성
    try:
        db.create_tables_if_not_exist()
        print("✅ 데이터베이스 테이블 확인 완료")
    except Exception as e:
        print(f"❌ 테이블 생성 실패: {e}")
        return False
    
    # Streamlit 앱 실행
    print("\n🌐 Streamlit 앱을 시작합니다...")
    print("브라우저에서 http://localhost:9001 을 열어주세요.")
    print("앱을 중지하려면 Ctrl+C를 누르세요.")
    print("-" * 60)
    
    try:
        # Streamlit 실행
        cmd = [
            str(venv_path / "bin" / "python"), "-m", "streamlit", "run", "main.py",
            "--server.port", "9001",
            "--server.address", "localhost",
            "--server.headless", "true"
        ]
        
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\n\n🛑 앱이 중지되었습니다.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Streamlit 실행 중 오류: {e}")
        return False
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
