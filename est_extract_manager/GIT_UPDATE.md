# Git 업데이트 가이드

## 경로 구분자 차이 설명

### Windows vs Linux/Unix
- **Windows**: 백슬래시 `\` 사용 (예: `C:\Users\...`)
- **Linux/Unix/Streamlit Cloud**: 슬래시 `/` 사용 (예: `/mount/src/...`)

### Python의 Path 객체
Python의 `pathlib.Path`는 **자동으로 처리**합니다:
- Windows에서 `\` 사용해도 자동 변환
- Linux에서 `/` 사용해도 자동 변환
- 코드에서는 `Path()` 객체 사용 시 자동 처리됨

### 현재 코드 상태
- ✅ `pathlib.Path` 사용으로 자동 처리됨
- ✅ `validate_path()`에서 `\`를 `/`로 변환하는 로직 있음
- ✅ Streamlit Cloud 경로도 처리됨

## Git 업데이트해야 할 파일 목록

### 필수 파일 (코드)

```bash
# 핵심 Python 파일들
git add app.py
git add config.py
git add verifier.py
git add processor.py
git add log_parser.py
git add reporter.py
git add monitor.py
git add sharepoint_utils.py
git add utils.py

# 설정 파일
git add .gitignore
git add .streamlit/config.toml
git add .cursorrules

# 의존성 및 데이터
git add requirements.txt
git add Master_Config_List.xlsx
```

### 문서 파일 (선택사항)

```bash
git add README.md
git add DEPLOY.md
git add setup_streamlit_cloud.md
git add CHANGES.md
git add RUN.md
```

### 실행 스크립트 (선택사항)

```bash
git add run.bat
git add run.ps1
```

## 제외할 파일들 (.gitignore에 의해 자동 제외)

- `__pycache__/` - Python 캐시
- `test_logs/` - 테스트 파일
- `temp/` - 임시 파일
- `Results/` - 결과 파일 (선택사항)
- `Logs/` - 로그 파일 (선택사항)

## 빠른 커밋 명령어

```bash
# 모든 Python 파일과 설정 파일 추가
git add *.py
git add .gitignore
git add .streamlit/
git add .cursorrules
git add requirements.txt
git add Master_Config_List.xlsx

# 문서 파일 추가 (선택사항)
git add *.md
git add run.bat run.ps1

# 커밋
git commit -m "Update: 경로 처리 개선 및 디버깅 기능 추가"
```

## 최근 변경 사항 요약

1. **경로 처리 개선**: Windows/Linux 경로 자동 처리
2. **Streamlit Cloud 지원**: 중복 경로 자동 수정
3. **로컬 경로 기본값**: 로컬 마스터 파일 자동 사용
4. **입력란 리셋**: 비우면 기본값으로 자동 리셋
5. **디버깅 기능**: 문제 발생 시 원인 파악 용이

