# Streamlit Cloud 배포 체크리스트

## ✅ 필수 파일 확인

- [x] `requirements.txt` - 모든 Python 패키지 포함
- [x] `.gitignore` - 불필요한 파일 제외
- [x] `README.md` - 프로젝트 설명
- [x] `.streamlit/config.toml` - Streamlit 설정
- [x] `app.py` - 메인 애플리케이션

## 📋 Git 커밋 전 체크리스트

### 1. 민감한 정보 제거
- [ ] `Master_Config_List.xlsx`에 민감한 데이터가 있는지 확인
- [ ] 환경 변수 파일 (`.env`) 제외 확인
- [ ] SharePoint 자격 증명 하드코딩 확인

### 2. 테스트 파일 정리
- [ ] `test_logs/` 폴더 제외 확인
- [ ] `temp/` 폴더 제외 확인
- [ ] 테스트 스크립트 제외 확인

### 3. 결과 파일 정리
- [ ] `Results/` 폴더에 샘플 데이터가 있는지 확인
- [ ] 필요시 `.gitignore`에 `Results/` 추가

## 🚀 배포 단계

### Step 1: Git 초기화 및 커밋
```bash
git init
git add .
git commit -m "Initial commit: EST Config Verification Tool"
```

### Step 2: GitHub 저장소 생성
1. GitHub에서 새 저장소 생성
2. 저장소 URL 복사

### Step 3: 원격 저장소 연결 및 푸시
```bash
git remote add origin https://github.com/YOUR_USERNAME/est_extract_manager.git
git branch -M main
git push -u origin main
```

### Step 4: Streamlit Cloud 배포
1. https://share.streamlit.io/ 접속
2. "New app" 클릭
3. GitHub 저장소 선택
4. Branch: `main`
5. Main file: `app.py`
6. Deploy!

## ⚙️ Streamlit Cloud 설정

### 환경 변수 (Secrets)
Streamlit Cloud의 "Secrets" 섹션에서 설정:

```
SHAREPOINT_SITE_URL = ""
SHAREPOINT_LIST_NAME = "EST_Verification_Results"
```

### 파일 경로 설정
Streamlit Cloud에서는 상대 경로를 사용하므로:
- `Master_Config_List.xlsx`는 저장소에 포함하거나
- 파일 업로드 기능으로 사용자가 직접 업로드

## 🔍 배포 후 테스트

1. 앱 로드 확인
2. 파일 업로드 테스트
3. PDF 리포트 생성 확인
4. 결과 다운로드 확인

