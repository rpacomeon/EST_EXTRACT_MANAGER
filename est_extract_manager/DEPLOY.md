# 배포 가이드 (Deployment Guide)

## Streamlit Cloud 배포

### 1. GitHub에 프로젝트 업로드

```bash
# Git 초기화 (아직 안 했다면)
git init

# .gitignore 확인
git add .gitignore

# 파일 추가
git add .

# 첫 커밋
git commit -m "Initial commit: EST Config Verification Tool"

# GitHub 저장소 생성 후
git remote add origin https://github.com/YOUR_USERNAME/est_extract_manager.git
git branch -M main
git push -u origin main
```

### 2. Streamlit Cloud 설정

1. **Streamlit Cloud 접속**: https://share.streamlit.io/
2. **"New app" 클릭**
3. **GitHub 저장소 선택**
4. **Branch**: `main` 선택
5. **Main file path**: `app.py` 입력
6. **Advanced settings**:
   - Python version: 3.9 이상
   - Secrets: 환경 변수 설정 (선택사항)

### 3. 환경 변수 설정 (선택사항)

Streamlit Cloud의 "Secrets" 섹션에서 설정:

```toml
# .streamlit/secrets.toml (로컬 테스트용)
SHAREPOINT_SITE_URL = "your_sharepoint_url"
SHAREPOINT_LIST_NAME = "EST_Verification_Results"
SHAREPOINT_CLIENT_ID = "your_client_id"
SHAREPOINT_CLIENT_SECRET = "your_client_secret"
```

또는 Streamlit Cloud UI에서 직접 입력:
- `SHAREPOINT_SITE_URL`
- `SHAREPOINT_LIST_NAME`
- `SHAREPOINT_CLIENT_ID`
- `SHAREPOINT_CLIENT_SECRET`

### 4. 필수 파일 확인

배포 전 확인할 파일들:
- ✅ `requirements.txt` - 모든 의존성 포함
- ✅ `.gitignore` - 불필요한 파일 제외
- ✅ `README.md` - 프로젝트 설명
- ✅ `.streamlit/config.toml` - Streamlit 설정

### 5. 배포 후 확인사항

1. **앱이 정상 실행되는지 확인**
2. **파일 업로드 기능 테스트**
3. **감시 폴더 기능** (Streamlit Cloud에서는 제한적일 수 있음)
4. **결과 파일 다운로드 확인**

## 로컬 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# Streamlit 실행
streamlit run app.py
```

## 주의사항

- **Master_Config_List.xlsx**: Streamlit Cloud에 업로드하거나, 환경 변수로 경로 설정 필요
- **파일 저장**: Streamlit Cloud는 임시 파일 시스템을 사용하므로, 중요한 파일은 다운로드 필요
- **감시 폴더**: Streamlit Cloud에서는 파일 시스템 접근이 제한적일 수 있음

