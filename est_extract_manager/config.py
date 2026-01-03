"""
Configuration management for EST Config Verification Tool.
All file paths are configurable.
"""
import os
from pathlib import Path
from typing import Dict, Any
import streamlit as st


class Config:
    """Configuration class for EST Config Verification Tool."""
    
    # Default paths (configurable via UI)
    # Using relative paths from project root as defaults
    _PROJECT_ROOT = Path(__file__).parent.absolute()
    DEFAULT_MASTER_LIST_PATH = str(_PROJECT_ROOT / "Master_Config_List.xlsx")
    DEFAULT_WATCH_FOLDER = str(_PROJECT_ROOT / "Logs")
    DEFAULT_OUTPUT_FOLDER = str(_PROJECT_ROOT / "Results")
    
    # SharePoint configuration
    SHAREPOINT_SITE_URL = os.getenv("SHAREPOINT_SITE_URL", "")
    SHAREPOINT_LIST_NAME = os.getenv("SHAREPOINT_LIST_NAME", "EST_Verification_Results")
    
    # Report settings
    REPORT_FONT = "Calibri"
    TIMEZONE = "Asia/Seoul"  # KST (Korea Standard Time)
    
    @staticmethod
    def get_config() -> Dict[str, Any]:
        """
        Get configuration from Streamlit session state or defaults.
        
        Returns:
            Dictionary containing all configuration values.
        """
        return {
            "master_list_path": st.session_state.get(
                "master_list_path", Config.DEFAULT_MASTER_LIST_PATH
            ),
            "watch_folder": st.session_state.get(
                "watch_folder", Config.DEFAULT_WATCH_FOLDER
            ),
            "output_folder": st.session_state.get(
                "output_folder", Config.DEFAULT_OUTPUT_FOLDER
            ),
            "sharepoint_site_url": st.session_state.get(
                "sharepoint_site_url", Config.SHAREPOINT_SITE_URL
            ),
            "sharepoint_list_name": st.session_state.get(
                "sharepoint_list_name", Config.SHAREPOINT_LIST_NAME
            ),
        }
    
    @staticmethod
    def validate_path(path: str) -> bool:
        """
        Validate if a path exists or can be created.
        
        Args:
            path: Path to validate.
            
        Returns:
            True if path is valid, False otherwise.
        """
        try:
            path_obj = Path(path)
            if path_obj.exists():
                return True
            # Try to create parent directory
            if path_obj.parent:
                path_obj.parent.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Path validation failed for {path}: {e}")
            return False

