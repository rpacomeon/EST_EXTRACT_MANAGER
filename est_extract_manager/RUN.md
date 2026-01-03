# 애플리케이션 실행 방법

## Cursor에서 Streamlit 앱 실행하기

### 방법 1: 터미널에서 실행 (권장)

1. **Cursor 하단의 터미널 탭 열기**
   - `Ctrl + `` (백틱) 또는 `View` → `Terminal`

2. **Streamlit 실행 명령어 입력**:
   ```bash
   streamlit run app.py
   ```

3. **브라우저 자동 열림**
   - 일반적으로 `http://localhost:8501`에서 실행됩니다
   - 터미널에 표시된 URL을 클릭하세요

### 방법 2: Python 명령어로 직접 실행

```bash
python -m streamlit run app.py
```

### 방법 3: 특정 포트 지정 (포트 충돌 시)

```bash
streamlit run app.py --server.port 8502
```

## 앱 중지하기

- 터미널에서 `Ctrl + C`를 누르면 앱이 중지됩니다

## 기본 경로 설정

기본적으로 다음 경로들이 사용됩니다 (프로젝트 폴더 기준):
- **Master Config List**: `./Master_Config_List.xlsx`
- **Watch Folder**: `./Logs`
- **Output Folder**: `./Results`

이 경로들은 Streamlit UI의 사이드바에서 변경할 수 있습니다.

## SharePoint 설정 (선택사항)

⚠️ **중요**: SharePoint는 **선택사항**입니다!

- **로컬 테스트 시**: SharePoint Site URL을 **비워두면** SharePoint 없이 작동합니다
- 로컬 PC에서는 SharePoint 연결 없이도 모든 검증 기능이 정상 작동합니다
- PDF 리포트, CSV 파싱, 파일 저장 등 모든 기능은 SharePoint 없이도 사용 가능합니다
- SharePoint 연결 오류가 발생해도 전체 프로세스는 중단되지 않습니다 (로컬 파일 저장은 계속됩니다)

SharePoint를 사용하려면:
- 실제 SharePoint 환경이 필요합니다
- 환경 변수에 인증 정보를 설정해야 합니다
- 또는 UI에서 URL을 입력하고 환경 변수 설정이 필요합니다

## 폴더 생성

처음 실행 시 필요한 폴더들이 자동으로 생성됩니다:
- `Logs/` - EST 로그 파일을 모니터링할 폴더
- `Results/` - 검증 결과를 저장할 폴더

