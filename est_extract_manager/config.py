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
    # Handle both script execution and Streamlit execution
    try:
        _PROJECT_ROOT = Path(__file__).parent.absolute()
    except:
        # Fallback to current working directory if __file__ is not available
        import os
        _PROJECT_ROOT = Path(os.getcwd()).absolute()
    
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
        Normalizes paths to absolute paths for consistency.
        
        Returns:
            Dictionary containing all configuration values.
        """
        def normalize_path(path_str: str) -> str:
            """Convert path to absolute path."""
            if not path_str:
                return path_str
            path_obj = Path(path_str)
            # If relative path, resolve relative to project root
            if not path_obj.is_absolute():
                path_obj = Config._PROJECT_ROOT / path_obj
            return str(path_obj.resolve())
        
        master_path = st.session_state.get(
            "master_list_path", Config.DEFAULT_MASTER_LIST_PATH
        )
        watch_path = st.session_state.get(
            "watch_folder", Config.DEFAULT_WATCH_FOLDER
        )
        output_path = st.session_state.get(
            "output_folder", Config.DEFAULT_OUTPUT_FOLDER
        )
        
        return {
            "master_list_path": normalize_path(master_path),
            "watch_folder": normalize_path(watch_path),
            "output_folder": normalize_path(output_path),
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
            if not path or not path.strip():
                return False
            
            # Normalize path (handle Windows path separators)
            path = path.strip().replace('\\', '/')
            path_obj = Path(path)
            
            # For files, check if parent directory exists or can be created
            if path_obj.suffix:  # Has extension, likely a file
                if path_obj.exists() and path_obj.is_file():
                    return True
                # Try to create parent directory
                if path_obj.parent:
                    path_obj.parent.mkdir(parents=True, exist_ok=True)
                return True
            else:  # Likely a directory
                if path_obj.exists() and path_obj.is_dir():
                    return True
                # Try to create directory
                path_obj.mkdir(parents=True, exist_ok=True)
                return True
        except Exception as e:
            print(f"Path validation failed for {path}: {e}")
            return False
    
    @staticmethod
    def normalize_path(path: str) -> str:
        """
        Normalize path string for cross-platform compatibility.
        
        Args:
            path: Path string to normalize.
            
        Returns:
            Normalized path string.
        """
        if not path:
            return path
        # Convert to Path object and back to string for normalization
        return str(Path(path).resolve())

