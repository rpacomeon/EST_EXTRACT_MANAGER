"""
EST Log File Parser.
Parses EST log CSV files and extracts pump information.
"""
import pandas as pd
from pathlib import Path
from typing import Dict, Optional, List
import os
import tempfile
from utils import extract_serial_digits


class ESTLogParser:
    """Parser for EST log files."""
    
    def __init__(self, log_file_path: str):
        """
        Initialize parser with log file path.
        
        Args:
            log_file_path: Path to the EST log CSV file.
        """
        self.log_file_path = Path(log_file_path)
        self.raw_data: Optional[pd.DataFrame] = None
        self.metadata: Dict[str, str] = {}
        self.config_data: Optional[pd.DataFrame] = None
    
    def parse(self) -> bool:
        """
        Parse the EST log file.
        Supports multiple formats:
        1. INI-style format with sections and key-value pairs + CSV table
        2. Standard CSV table format
        3. Header + table format (key-value pairs + CSV table)
        4. Excel file format (.xlsx)
        
        Returns:
            True if parsing successful, False otherwise.
        """
        try:
            # Check if it's an Excel file
            if self.log_file_path.suffix.lower() in ['.xlsx', '.xls']:
                return self._parse_excel_format()
            
            # Read file content (CSV or text file)
            with open(self.log_file_path, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()
            
            # Check if it's INI-style format (starts with [SECTION])
            first_line = lines[0].strip() if lines else ""
            if first_line.startswith('['):
                return self._parse_ini_format(lines)
            
            # Try to read as standard CSV table first
            try:
                df = pd.read_csv(self.log_file_path, encoding='utf-8-sig')
                
                # Check if it's a table format (has standard columns)
                if 'Pump Serial No' in df.columns or 'Serial No' in df.columns or 'SerialNo' in df.columns:
                    # Table format - extract metadata from first row
                    first_row = df.iloc[0]
                    
                    # Extract serial number
                    serial_col = None
                    for col in ['Pump Serial No', 'Serial No', 'SerialNo', 'Serial Number', 'Serial_No']:
                        if col in df.columns:
                            serial_col = col
                            break
                    if serial_col:
                        serial_value = str(first_row[serial_col]).strip()
                        if serial_value and serial_value != 'nan':
                            self.metadata['serial_number'] = serial_value
                    
                    # Extract other metadata from first row
                    if 'Model' in df.columns:
                        self.metadata['model'] = str(first_row['Model'])
                    if 'Software Version' in df.columns:
                        self.metadata['software_version'] = str(first_row['Software Version'])
                    if 'Firmware Version' in df.columns:
                        self.metadata['firmware_version'] = str(first_row['Firmware Version'])
                    if 'Date' in df.columns:
                        self.metadata['date'] = str(first_row['Date'])
                    
                    # Store the full dataframe as config_data
                    self.config_data = df
                    return True
                    
            except Exception:
                # If standard CSV read fails, try header+table format
                pass
            
            # Fall back to header+table format parsing
            # Extract metadata (header section)
            for line in lines:
                line = line.strip()
                if not line or line.startswith('Section'):
                    break
                
                if ',' in line:
                    parts = line.split(',', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        
                        # Store metadata
                        if 'Serial No' in key or 'SerialNo' in key:
                            self.metadata['serial_number'] = value
                        elif 'Date' in key:
                            self.metadata['date'] = value
                        elif 'Software Version' in key or 'Software' in key:
                            self.metadata['software_version'] = value
                        elif 'Firmware Version' in key or 'Firmware' in key:
                            self.metadata['firmware_version'] = value
                        elif 'Model' in key:
                            self.metadata['model'] = value
            
            # Parse configuration data (after Section header)
            config_lines = []
            section_found = False
            
            for line in lines:
                line = line.strip()
                if line.startswith('Section'):
                    section_found = True
                    config_lines.append(line)
                    continue
                
                if section_found and line and ',' in line:
                    config_lines.append(line)
            
            if config_lines:
                # Create DataFrame from config data
                from io import StringIO
                config_text = '\n'.join(config_lines)
                self.config_data = pd.read_csv(StringIO(config_text))
            
            return True
            
        except Exception as e:
            print(f"Error parsing log file: {e}")
            return False
    
    def _parse_ini_format(self, lines: List[str]) -> bool:
        """
        Parse INI-style format with sections and key-value pairs.
        
        Args:
            lines: List of file lines.
            
        Returns:
            True if parsing successful, False otherwise.
        """
        try:
            current_section = None
            csv_table_start = None
            
            # First pass: Extract metadata and find CSV table start
            for i, line in enumerate(lines):
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    continue
                
                # Check for section header
                if line.startswith('[') and line.endswith(']'):
                    current_section = line[1:-1]
                    continue
                
                # Check if this looks like a CSV header (comma-separated column names)
                if ',' in line and not csv_table_start:
                    # Check if it looks like CSV headers (multiple columns, no numbers or symbols at start)
                    parts = line.split(',')
                    if len(parts) > 2 and not any(char.isdigit() for char in parts[0].strip()[:3]):
                        csv_table_start = i
                        break
                
                # Parse key-value pairs (supports both : and =)
                if ':' in line or '=' in line:
                    # Handle format: "Key: Value" or "Key = Value" or "Key: Value = Value2 (Unit)"
                    if ':' in line:
                        parts = line.split(':', 1)
                        key = parts[0].strip()
                        value_part = parts[1].strip() if len(parts) > 1 else ""
                        
                        # Extract value (before = if present, before ( if present)
                        value = value_part.split('=')[0].strip() if '=' in value_part else value_part
                        value = value.split('(')[0].strip() if '(' in value else value
                    elif '=' in line:
                        parts = line.split('=', 1)
                        key = parts[0].strip()
                        value_part = parts[1].strip() if len(parts) > 1 else ""
                        value = value_part.split('(')[0].strip() if '(' in value_part else value_part
                    else:
                        continue
                    
                    # Map keys to metadata fields
                    key_lower = key.lower()
                    if 'serial' in key_lower and 'no' in key_lower:
                        self.metadata['serial_number'] = value
                    elif 'model' in key_lower and 'type' in key_lower:
                        self.metadata['model'] = value
                    elif key_lower == 'model':
                        self.metadata['model'] = value
                    elif 'firmware' in key_lower:
                        self.metadata['firmware_version'] = value
                    elif 'version' in key_lower and current_section == 'SYSTEM_INFO':
                        self.metadata['software_version'] = value
                    elif key_lower == 'date':
                        self.metadata['date'] = value
                    elif key_lower == 'tool_name':
                        self.metadata['tool_name'] = value
            
            # Second pass: Parse CSV table if found
            if csv_table_start:
                csv_lines = [line.strip() for line in lines[csv_table_start:] if line.strip() and ',' in line]
                if csv_lines:
                    from io import StringIO
                    csv_text = '\n'.join(csv_lines)
                    self.config_data = pd.read_csv(StringIO(csv_text))
            
            return True
            
        except Exception as e:
            print(f"Error parsing INI format: {e}")
            return False
    
    def _parse_excel_format(self) -> bool:
        """
        Parse Excel file format (.xlsx, .xls).
        Excel files from EST toolkit are typically structured tables.
        
        Returns:
            True if parsing successful, False otherwise.
        """
        try:
            # Try to read Excel file as DataFrame
            try:
                df = pd.read_excel(self.log_file_path, sheet_name=0, header=None)
            except Exception as e:
                print(f"Error reading Excel file: {e}")
                return False
            
            if df.empty:
                return False
            
            # Check if first row looks like headers (table format)
            first_row_values = df.iloc[0].dropna().astype(str).tolist()
            
            if len(first_row_values) > 2:
                first_row_str = ' '.join(first_row_values).lower()
                if any(indicator in first_row_str for indicator in ['serial', 'pump', 'model', 'version']):
                    # Table format - use first row as header
                    df = pd.read_excel(self.log_file_path, sheet_name=0, header=0)
                    
                    if len(df) > 0:
                        first_row = df.iloc[0]
                        
                        # Extract serial number
                        serial_col = None
                        for col in df.columns:
                            col_str = str(col).lower()
                            if 'serial' in col_str and ('no' in col_str or 'number' in col_str):
                                serial_col = col
                                break
                        if serial_col is not None:
                            serial_value = str(first_row[serial_col]).strip()
                            if serial_value and serial_value != 'nan':
                                self.metadata['serial_number'] = serial_value
                        
                        # Extract other metadata
                        for col in df.columns:
                            col_str = str(col).lower()
                            if 'model' in col_str:
                                self.metadata['model'] = str(first_row[col])
                            elif 'software' in col_str and 'version' in col_str:
                                self.metadata['software_version'] = str(first_row[col])
                            elif 'firmware' in col_str and 'version' in col_str:
                                self.metadata['firmware_version'] = str(first_row[col])
                            elif 'date' in col_str:
                                self.metadata['date'] = str(first_row[col])
                        
                        self.config_data = df
                        return True
            
            # Convert Excel to CSV-like text and parse
            tmp_path = None
            try:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as tmp_file:
                    for idx, row in df.iterrows():
                        row_values = [str(val) if pd.notna(val) else '' for val in row]
                        if any(val.strip() for val in row_values):
                            tmp_file.write(','.join(row_values) + '\n')
                    tmp_path = tmp_file.name
                
                with open(tmp_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                if lines and lines[0].strip().startswith('['):
                    result = self._parse_ini_format(lines)
                else:
                    result = self._parse_csv_lines(lines)
                
                return result
            finally:
                if tmp_path and os.path.exists(tmp_path):
                    try:
                        os.unlink(tmp_path)
                    except Exception as e:
                        print(f"Warning: Failed to delete temp file {tmp_path}: {e}")
            
            return False
            
        except Exception as e:
            print(f"Error parsing Excel format: {e}")
            return False
    
    def _parse_csv_lines(self, lines: List[str]) -> bool:
        """
        Parse CSV lines (helper for Excel conversion).
        
        Args:
            lines: List of file lines.
            
        Returns:
            True if parsing successful, False otherwise.
        """
        try:
            from io import StringIO
            csv_text = '\n'.join(lines)
            df = pd.read_csv(StringIO(csv_text), encoding='utf-8-sig')
            
            if 'Pump Serial No' in df.columns or 'Serial No' in df.columns or 'SerialNo' in df.columns:
                first_row = df.iloc[0]
                
                serial_col = None
                for col in ['Pump Serial No', 'Serial No', 'SerialNo', 'Serial Number', 'Serial_No']:
                    if col in df.columns:
                        serial_col = col
                        break
                if serial_col:
                    serial_value = str(first_row[serial_col]).strip()
                    if serial_value and serial_value != 'nan':
                        self.metadata['serial_number'] = serial_value
                
                if 'Model' in df.columns:
                    self.metadata['model'] = str(first_row['Model'])
                if 'Software Version' in df.columns:
                    self.metadata['software_version'] = str(first_row['Software Version'])
                if 'Firmware Version' in df.columns:
                    self.metadata['firmware_version'] = str(first_row['Firmware Version'])
                if 'Date' in df.columns:
                    self.metadata['date'] = str(first_row['Date'])
                
                self.config_data = df
                return True
            
            return False
        except Exception:
            return False
    
    def get_serial_number(self) -> Optional[str]:
        """
        Get pump serial number from parsed log.
        
        Returns:
            Serial number string or None if not found.
        """
        return self.metadata.get('serial_number')
    
    def get_metadata(self) -> Dict[str, str]:
        """
        Get all metadata from the log file.
        
        Returns:
            Dictionary of metadata.
        """
        return self.metadata.copy()
    
    def get_config_data(self) -> Optional[pd.DataFrame]:
        """
        Get configuration data DataFrame.
        
        Returns:
            DataFrame with Section, Parameter, Current_Value, etc.
        """
        return self.config_data.copy() if self.config_data is not None else None
    
    def export_to_csv(self, output_path: str) -> bool:
        """
        Export parsed data to clean CSV format.
        
        Args:
            output_path: Path to save the CSV file.
            
        Returns:
            True if export successful, False otherwise.
        """
        try:
            if self.config_data is not None:
                self.config_data.to_csv(output_path, index=False, encoding='utf-8-sig')
                return True
            return False
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False

