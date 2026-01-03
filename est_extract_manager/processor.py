"""
Main Processing Logic.
Orchestrates log parsing, verification, report generation, and SharePoint update.
"""
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime
import pytz

from log_parser import ESTLogParser
from verifier import ConfigVerifier
from reporter import ReportGenerator
from sharepoint_utils import SharePointClient
from config import Config
from utils import truncate_serial_number


class ESTProcessor:
    """Main processor for EST log files."""
    
    def __init__(self, config_dict: dict):
        """
        Initialize processor with configuration.
        
        Args:
            config_dict: Configuration dictionary from Config.get_config().
        """
        self.config = config_dict
        self.verifier = ConfigVerifier(config_dict['master_list_path'])
        self.reporter = ReportGenerator(config_dict['output_folder'])
        self.sharepoint = None
        
        # Initialize SharePoint client if URL is provided
        if config_dict.get('sharepoint_site_url'):
            self.sharepoint = SharePointClient(
                config_dict['sharepoint_site_url'],
                config_dict['sharepoint_list_name']
            )
    
    def process_log_file(self, log_file_path: str) -> Tuple[bool, str]:
        """
        Process a single EST log file.
        
        Args:
            log_file_path: Path to EST log CSV file.
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Parse log file
            parser = ESTLogParser(log_file_path)
            if not parser.parse():
                return False, "Failed to parse log file"
            
            serial_number = parser.get_serial_number()
            if not serial_number:
                return False, "Serial number not found in log file"
            
            metadata = parser.get_metadata()
            config_data = parser.get_config_data()
            
            # Verify against master list
            is_pass, config_tag, config_info = self.verifier.verify(serial_number)
            
            # Handle UNPASS case (serial number not in master list)
            # Still generate PDF report for consistency
            if config_tag is None:
                config_tag = "N/A"  # Use placeholder for UNPASS cases
                is_pass = False
                if config_info is None:
                    config_info = {"error": f"Serial number {serial_number} not found in master list"}
            
            # Get current timestamp in KST
            timestamp = datetime.now(pytz.timezone('Asia/Seoul'))
            
            # Generate PDF report (always generate, even for UNPASS)
            pdf_path = self.reporter.generate_report(
                serial_number=serial_number,
                config_tag=config_tag,
                is_pass=is_pass,
                config_info=config_info or {},
                metadata=metadata,
                timestamp=timestamp
            )
            
            if not pdf_path:
                return False, "Failed to generate report"
            
            # Export parsed CSV
            result_folder = Path(pdf_path).parent
            time_str = self.reporter.format_datetime_kst(timestamp)
            sn_short = truncate_serial_number(serial_number, max_length=20)
            parsed_csv_path = result_folder / f"{sn_short}_{time_str}_parsed.csv"
            if not parser.export_to_csv(str(parsed_csv_path)):
                return False, "Failed to export parsed CSV"
            
            # Copy files to result folder
            result_folder_path = self.reporter.copy_files_to_result_folder(
                serial_number=serial_number,
                is_pass=is_pass,
                log_file_path=log_file_path,
                parsed_csv_path=str(parsed_csv_path),
                timestamp=timestamp
            )
            
            # Update SharePoint if connected (optional, errors don't fail the process)
            if self.sharepoint:
                result_str = "PASS" if is_pass else "FAIL"
                try:
                    self.sharepoint.add_verification_result(
                        serial_number=serial_number,
                        config_tag=config_tag,
                        result=result_str,
                        result_folder_path=str(result_folder_path),
                        verification_date=timestamp
                    )
                except Exception as e:
                    # SharePoint update failure doesn't fail the entire process
                    print(f"Warning: SharePoint update failed: {e}")
                    # Continue processing - local files are already saved
            
            result_str = "PASS" if is_pass else "FAIL"
            message = f"Processing completed: {serial_number} - {result_str}"
            return True, message
            
        except Exception as e:
            return False, f"Error processing file: {str(e)}"

