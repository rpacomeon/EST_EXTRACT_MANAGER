"""
Main Streamlit Application.
Pump EST Config Verification Tool - Personal Project
"""
import streamlit as st
from pathlib import Path
import threading
import time

from config import Config
from monitor import FolderMonitor
from processor import ESTProcessor

# Page configuration
st.set_page_config(
    page_title="EST Config Verification Tool",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'monitor' not in st.session_state:
    st.session_state.monitor = None
if 'monitoring' not in st.session_state:
    st.session_state.monitoring = False
if 'processing_history' not in st.session_state:
    st.session_state.processing_history = []


def initialize_defaults():
    """Initialize default configuration values."""
    # Use explicit local path for master file
    local_master_path = r"C:\Users\dhaud\Desktop\est_extract_manager\Master_Config_List.xlsx"
    
    if 'master_list_path' not in st.session_state:
        # Check if local path exists, otherwise use default
        if Path(local_master_path).exists():
            st.session_state.master_list_path = local_master_path
        else:
            st.session_state.master_list_path = Config.DEFAULT_MASTER_LIST_PATH
    if 'watch_folder' not in st.session_state:
        st.session_state.watch_folder = Config.DEFAULT_WATCH_FOLDER
    if 'output_folder' not in st.session_state:
        st.session_state.output_folder = Config.DEFAULT_OUTPUT_FOLDER
    if 'sharepoint_site_url' not in st.session_state:
        st.session_state.sharepoint_site_url = Config.SHAREPOINT_SITE_URL
    if 'sharepoint_list_name' not in st.session_state:
        st.session_state.sharepoint_list_name = Config.SHAREPOINT_LIST_NAME


def process_file_callback(file_path: str):
    """
    Callback function for file monitoring.
    Note: This runs in a background thread, so session_state access may be limited.
    For thread-safe operation, consider using a queue or file-based logging.
    
    Args:
        file_path: Path to newly detected file.
    """
    try:
        # Get config from session state if available, otherwise use defaults
        try:
            config_dict = Config.get_config()
        except Exception:
            # Fallback to defaults if session_state not available (background thread)
            config_dict = {
                "master_list_path": Config.DEFAULT_MASTER_LIST_PATH,
                "watch_folder": Config.DEFAULT_WATCH_FOLDER,
                "output_folder": Config.DEFAULT_OUTPUT_FOLDER,
                "sharepoint_site_url": Config.SHAREPOINT_SITE_URL,
                "sharepoint_list_name": Config.SHAREPOINT_LIST_NAME,
            }
        
        processor = ESTProcessor(config_dict)
        success, message = processor.process_log_file(file_path)
        
        # Try to add to history (may fail in background thread)
        try:
            if 'processing_history' not in st.session_state:
                st.session_state.processing_history = []
            st.session_state.processing_history.append({
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'file': Path(file_path).name,
                'success': success,
                'message': message
            })
            # Keep only last 100 entries
            if len(st.session_state.processing_history) > 100:
                st.session_state.processing_history = st.session_state.processing_history[-100:]
        except Exception:
            # Session state not available in background thread - log to console instead
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}")
            
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {error_msg}")
        try:
            if 'processing_history' not in st.session_state:
                st.session_state.processing_history = []
            st.session_state.processing_history.append({
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'file': Path(file_path).name,
                'success': False,
                'message': error_msg
            })
        except Exception:
            pass  # Session state not available


def main():
    """Main application function."""
    initialize_defaults()
    
    # Custom CSS for cleaner design
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #C62229;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        color: #666666;
        text-align: center;
        margin-bottom: 2rem;
        font-size: 0.9rem;
    }
    .personal-project {
        background-color: #FFF5F5;
        padding: 0.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #C62229;
        margin-bottom: 1rem;
        font-size: 0.85rem;
        color: #333333;
    }
    .big-button {
        font-size: 1.2rem;
        padding: 0.75rem;
    }
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<div class="main-header">⚙️ EST Config 검증 도구</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Pump EST Configuration Verification Tool</div>', unsafe_allow_html=True)
    
    # Personal Project Notice
    st.markdown("""
    <div class="personal-project">
        <strong>📌 개인 프로젝트 (Personal Project)</strong><br>
        This tool is a personal project for field workers to easily verify EST log configurations.
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar - Configuration (Simplified for field workers)
    with st.sidebar:
        st.markdown("### ⚙️ 설정")
        st.markdown("---")
        
        # File Paths Section
        st.markdown("**📁 파일 경로**")
        master_list_path = st.text_input(
            "마스터 설정 파일",
            value=st.session_state.master_list_path,
            help="Master_Config_List.xlsx 파일 경로 (비워두면 기본 경로 사용)"
        )
        # If input is empty, reset to default
        if not master_list_path or not master_list_path.strip():
            # Use local path if exists, otherwise use default
            local_master_path = r"C:\Users\dhaud\Desktop\est_extract_manager\Master_Config_List.xlsx"
            if Path(local_master_path).exists():
                st.session_state.master_list_path = local_master_path
            else:
                st.session_state.master_list_path = Config.DEFAULT_MASTER_LIST_PATH
        else:
            st.session_state.master_list_path = master_list_path.strip()
        
        # Validate master list path
        if master_list_path:
            master_path = Path(master_list_path)
            # Try to resolve relative paths
            if not master_path.is_absolute():
                master_path = Path.cwd() / master_path
            master_path = master_path.resolve()
            
            if master_path.exists() and master_path.is_file():
                st.success("✅ 마스터 파일 확인됨")
            else:
                st.warning(f"⚠️ 파일을 찾을 수 없습니다: {master_path}")
                st.info(f"💡 현재 작업 디렉토리: {Path.cwd()}")
                
                # Suggest local path
                local_path = Path(r"C:\Users\dhaud\Desktop\est_extract_manager\Master_Config_List.xlsx")
                if local_path.exists():
                    st.info(f"💡 로컬 경로에 파일이 있습니다: {local_path}")
                    if st.button("로컬 경로 사용", key="use_local_master"):
                        st.session_state.master_list_path = str(local_path)
                        st.rerun()
                
                # Suggest default path
                default_path = Path(Config.DEFAULT_MASTER_LIST_PATH)
                if default_path.exists() and default_path != local_path:
                    st.info(f"💡 기본 경로에 파일이 있습니다: {default_path}")
                    if st.button("기본 경로 사용", key="use_default_master"):
                        st.session_state.master_list_path = str(default_path)
                        st.rerun()
        
        watch_folder = st.text_input(
            "감시 폴더",
            value=st.session_state.watch_folder,
            help="새 로그 파일을 감시할 폴더 (비워두면 기본 경로 사용)"
        )
        # If input is empty, reset to default
        if not watch_folder or not watch_folder.strip():
            st.session_state.watch_folder = Config.DEFAULT_WATCH_FOLDER
        else:
            st.session_state.watch_folder = watch_folder.strip()
        
        # Validate watch folder
        if watch_folder:
            watch_path = Path(watch_folder)
            if watch_path.exists() and watch_path.is_dir():
                st.success("✅ 감시 폴더 확인됨")
            else:
                st.info(f"ℹ️ 폴더가 없으면 자동 생성됩니다: {watch_folder}")
        
        output_folder = st.text_input(
            "결과 저장 폴더",
            value=st.session_state.output_folder,
            help="검증 결과를 저장할 폴더 (비워두면 기본 경로 사용)"
        )
        # If input is empty, reset to default
        if not output_folder or not output_folder.strip():
            st.session_state.output_folder = Config.DEFAULT_OUTPUT_FOLDER
        else:
            st.session_state.output_folder = output_folder.strip()
        
        # Validate output folder
        if output_folder:
            output_path = Path(output_folder)
            if output_path.exists() and output_path.is_dir():
                st.success("✅ 결과 폴더 확인됨")
            else:
                st.info(f"ℹ️ 폴더가 없으면 자동 생성됩니다: {output_folder}")
        
        st.markdown("---")
        
        # SharePoint (Optional - Collapsed by default)
        with st.expander("🔗 SharePoint 설정 (선택사항)"):
            st.info("⚠️ SharePoint는 선택사항입니다. 비워두면 로컬 모드로 동작합니다.")
            sharepoint_site_url = st.text_input(
                "SharePoint 사이트 URL",
                value=st.session_state.sharepoint_site_url,
                help="SharePoint 사이트 URL (선택사항)"
            )
            st.session_state.sharepoint_site_url = sharepoint_site_url
            
            sharepoint_list_name = st.text_input(
                "SharePoint 목록 이름",
                value=st.session_state.sharepoint_list_name,
                help="SharePoint 목록 이름 (선택사항)"
            )
            st.session_state.sharepoint_list_name = sharepoint_list_name
        
        st.markdown("---")
        
        # Monitor Control (Large, Clear Buttons)
        st.markdown("### 🎮 자동 감시 제어")
        if st.session_state.monitoring:
            if st.button("🛑 감시 중지", use_container_width=True, type="primary"):
                if st.session_state.monitor:
                    st.session_state.monitor.stop()
                st.session_state.monitoring = False
                st.session_state.monitor = None
                st.rerun()
            st.success("✅ **감시 활성화됨**")
            st.caption(f"감시 폴더: {st.session_state.watch_folder}")
        else:
            if st.button("▶️ 감시 시작", use_container_width=True, type="primary"):
                try:
                    monitor = FolderMonitor(
                        st.session_state.watch_folder,
                        process_file_callback
                    )
                    monitor.start()
                    st.session_state.monitor = monitor
                    st.session_state.monitoring = True
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 오류: {e}")
            st.info("⏸️ **감시 비활성화됨**")
    
    # Main content area - Simplified for field workers
    st.markdown("---")
    
    # Step 1: File Upload (Large, Clear)
    st.markdown("### 📤 1단계: 파일 업로드")
    col_upload, col_info = st.columns([2, 1])
    
    with col_upload:
        uploaded_file = st.file_uploader(
            "EST 로그 파일 선택 (CSV 또는 Excel)",
            type=['csv', 'xlsx', 'xls'],
            help="검증할 EST 로그 파일을 선택하세요"
        )
        
        if uploaded_file is not None:
            st.info(f"✅ 선택된 파일: **{uploaded_file.name}**")
            
            if st.button("🔍 검증 실행", use_container_width=True, type="primary", key="process_btn"):
                # Save uploaded file temporarily
                temp_path = Path("temp") / uploaded_file.name
                temp_path.parent.mkdir(exist_ok=True)
                
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Process file
                with st.spinner("⏳ 파일 검증 중..."):
                    config_dict = Config.get_config()
                    
                    # Debug: Show configuration being used
                    with st.expander("🔍 디버그 정보", expanded=False):
                        st.write(f"**마스터 파일 경로:** {config_dict['master_list_path']}")
                        st.write(f"**마스터 파일 존재:** {Path(config_dict['master_list_path']).exists()}")
                        st.write(f"**처리할 파일:** {temp_path}")
                        st.write(f"**파일 존재:** {temp_path.exists()}")
                    
                    processor = ESTProcessor(config_dict)
                    success, message = processor.process_log_file(str(temp_path))
                
                if success:
                    # Extract result from message
                    if "PASS" in message:
                        st.success(f"✅ {message}")
                        st.balloons()
                    elif "FAIL" in message:
                        st.warning(f"⚠️ {message}")
                        # Show detailed error info if available
                        st.info("💡 시리얼 넘버가 마스터 리스트에 없거나 검증에 실패했습니다. PDF 리포트는 생성되었습니다.")
                    else:
                        st.success(f"✅ {message}")
                else:
                    st.error(f"❌ {message}")
                    st.info("💡 파일 형식을 확인하거나 마스터 설정 파일 경로를 확인해주세요.")
                
                # Clean up temp file
                try:
                    temp_path.unlink()
                except:
                    pass
    
    with col_info:
        st.markdown("**💡 사용 방법**")
        st.markdown("""
        1. 파일 선택 버튼 클릭
        2. EST 로그 파일 선택
        3. "검증 실행" 버튼 클릭
        4. 결과 확인
        """)
        st.markdown("---")
        st.markdown("**📋 지원 형식**")
        st.markdown("- CSV 파일")
        st.markdown("- Excel 파일")
        st.markdown("- INI 형식")
    
    # Step 2: Processing Status
    st.markdown("---")
    st.markdown("### 📊 2단계: 처리 상태")
    
    if st.session_state.processing_history:
        # Show last 5 entries in a cleaner format
        recent = st.session_state.processing_history[-5:]
        for entry in reversed(recent):
            status_color = "🟢" if entry['success'] else "🔴"
            with st.container():
                col_time, col_file, col_msg = st.columns([2, 3, 5])
                with col_time:
                    st.text(f"{status_color} {entry['timestamp']}")
                with col_file:
                    st.text(entry['file'])
                with col_msg:
                    st.text(entry['message'])
                st.markdown("---")
    else:
        st.info("📭 아직 처리된 파일이 없습니다. 파일을 업로드하여 검증을 시작하세요.")
    
    # Full History (Collapsible)
    if st.session_state.processing_history:
        with st.expander("📋 전체 처리 이력 보기"):
            import pandas as pd
            df = pd.DataFrame(st.session_state.processing_history)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            if st.button("🗑️ 이력 삭제"):
                st.session_state.processing_history = []
                st.rerun()


if __name__ == "__main__":
    main()

