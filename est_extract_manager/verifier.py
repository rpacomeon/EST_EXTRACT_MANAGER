"""
Configuration Verification Logic.
Verifies EST log configuration against master list.
"""
import pandas as pd
from typing import Dict, Optional, Tuple
from pathlib import Path
from utils import extract_serial_digits


class ConfigVerifier:
    """Verifies pump configuration against master list."""
    
    def __init__(self, master_list_path: str):
        """
        Initialize verifier with master list path.
        
        Args:
            master_list_path: Path to Master_Config_List.xlsx file.
        """
        # Convert to absolute path for consistency
        path_obj = Path(master_list_path)
        if not path_obj.is_absolute():
            # If relative, resolve relative to current working directory
            path_obj = Path.cwd() / path_obj
        self.master_list_path = path_obj.resolve()
        self.master_list: Optional[pd.DataFrame] = None
    
    def load_master_list(self) -> bool:
        """
        Load master configuration list from Excel file.
        
        Returns:
            True if loading successful, False otherwise.
        """
        try:
            print(f"DEBUG: Loading master list from: {self.master_list_path}")
            print(f"DEBUG: Path exists: {self.master_list_path.exists()}")
            print(f"DEBUG: Path absolute: {self.master_list_path.absolute()}")
            
            if not self.master_list_path.exists():
                print(f"Error: Master list file not found: {self.master_list_path}")
                print(f"Error: Absolute path: {self.master_list_path.absolute()}")
                return False
            self.master_list = pd.read_excel(self.master_list_path)
            print(f"DEBUG: Master list loaded, rows: {len(self.master_list)}")
            print(f"DEBUG: Columns: {self.master_list.columns.tolist()}")
            
            if self.master_list.empty:
                print("Error: Master list is empty")
                return False
            if 'Pump_Serial_No' not in self.master_list.columns:
                print("Error: Master list missing required column 'Pump_Serial_No'")
                return False
            return True
        except Exception as e:
            print(f"Error loading master list: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def verify(self, serial_number: str, config_tag: Optional[str] = None) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Verify if serial number and config tag match master list.
        PASS if serial number exists in master list AND config tag matches (if provided).
        
        Args:
            serial_number: Pump serial number to verify.
            config_tag: Optional config tag to verify (if provided, must match).
            
        Returns:
            Tuple of (is_pass, config_tag, config_info)
            - is_pass: True if PASS, False if FAIL
            - config_tag: Target_Config_Tag from master list
            - config_info: Dictionary with configuration details
        """
        if self.master_list is None:
            if not self.load_master_list():
                return False, None, {"error": "Failed to load master list"}
        
        # Extract numeric part from serial number for comparison
        serial_digits = extract_serial_digits(serial_number)
        if not serial_digits:
            return False, None, {"error": f"Invalid serial number format: {serial_number}"}
        
        # Extract numeric part from master list serial numbers and compare
        master_digits = self.master_list['Pump_Serial_No'].apply(extract_serial_digits)
        print(f"DEBUG: Looking for serial digits: {serial_digits}")
        print(f"DEBUG: Master list digits: {master_digits.tolist()}")
        
        match = self.master_list[master_digits == serial_digits]
        
        if match.empty:
            print(f"DEBUG: No match found for serial {serial_number} (digits: {serial_digits})")
            print(f"DEBUG: Available serials in master list: {self.master_list['Pump_Serial_No'].tolist()}")
            return False, None, {
                "error": f"Serial number {serial_number} not found in master list."
            }
        
        print(f"DEBUG: Match found! Serial: {match.iloc[0]['Pump_Serial_No']}")
        
        # Get first match (if multiple, take first)
        row = match.iloc[0]
        master_config_tag = str(row.get('Target_Config_Tag', '')).strip()
        
        # If config_tag is provided, verify it matches
        if config_tag is not None and config_tag.strip():
            if master_config_tag.upper() != config_tag.upper():
                return False, master_config_tag, {
                    "error": f"Config tag mismatch: Expected {master_config_tag}, but found {config_tag}."
                }
        
        config_info = {
            "serial_number": serial_number,
            "target_config_tag": master_config_tag,
            "parameter_match": row.get('Parameter_Match', ''),
            "section_match": row.get('Section_Match', ''),
            "target_value": row.get('Target_Value', ''),
            "original_value": row.get('Original_Value', ''),
            "section": row.get('Section', ''),
        }
        
        # PASS if serial number exists in master list (and config tag matches if provided)
        return True, master_config_tag, config_info

