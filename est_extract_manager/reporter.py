"""
Report Generator for EST Config Verification.
Generates clean PDF reports for pump EST configuration verification.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
import pytz
from pathlib import Path
from typing import Dict, Optional
import shutil
from utils import truncate_serial_number, ensure_directory


class ReportGenerator:
    """Generates PDF reports for verification results."""
    
    def __init__(self, output_folder: str):
        """
        Initialize report generator.
        
        Args:
            output_folder: Base output folder path.
        """
        self.output_folder = Path(output_folder)
        self.timezone = pytz.timezone('Asia/Seoul')  # KST
    
    def get_kst_time(self) -> datetime:
        """
        Get current time in KST (Korea Standard Time).
        
        Returns:
            datetime object in KST timezone.
        """
        return datetime.now(self.timezone)
    
    def format_datetime_kst(self, dt: Optional[datetime] = None) -> str:
        """
        Format datetime to YYYYMMDD_HHMMSS in KST.
        
        Args:
            dt: datetime object (defaults to current time).
            
        Returns:
            Formatted datetime string.
        """
        if dt is None:
            dt = self.get_kst_time()
        elif dt.tzinfo is None:
            dt = self.timezone.localize(dt)
        else:
            dt = dt.astimezone(self.timezone)
        
        return dt.strftime('%Y%m%d_%H%M%S')
    
    def generate_report(
        self,
        serial_number: str,
        config_tag: str,
        is_pass: bool,
        config_info: Dict,
        metadata: Dict,
        timestamp: Optional[datetime] = None
    ) -> Optional[str]:
        """
        Generate PDF report for verification result.
        
        Args:
            serial_number: Pump serial number.
            config_tag: Target configuration tag.
            is_pass: True if PASS, False if FAIL.
            config_info: Configuration information dictionary.
            metadata: EST log metadata.
            timestamp: Timestamp for report (defaults to current KST time).
            
        Returns:
            Path to generated PDF file or None if failed.
        """
        try:
            if timestamp is None:
                timestamp = self.get_kst_time()
            
            # Create folder structure: SerialNo_PASS or SerialNo_FAIL
            result_str = "PASS" if is_pass else "FAIL"
            folder_name = f"{serial_number}_{result_str}"
            result_folder = self.output_folder / folder_name
            
            # Create folder if it doesn't exist
            if not ensure_directory(result_folder):
                print(f"Error: Failed to create result folder: {result_folder}")
                return None
            
            # Generate filename (shortened to avoid path length issues)
            time_str = self.format_datetime_kst(timestamp)
            sn_short = truncate_serial_number(serial_number, max_length=20)
            pdf_filename = f"{sn_short}_{time_str}_{result_str}.pdf"
            pdf_path = result_folder / pdf_filename
            
            # Create PDF document
            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=A4,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch
            )
            
            # Container for the 'Flowable' objects
            elements = []
            
            # Define styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=22,
                textColor=colors.HexColor('#C62229'),
                spaceAfter=20,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#333333'),
                spaceAfter=12,
                fontName='Helvetica-Bold'
            )
            
            # Title
            title_text = "Pump EST Configuration Verification Report"
            elements.append(Paragraph(title_text, title_style))
            elements.append(Spacer(1, 0.1*inch))
            
            # Personal Project Notice
            notice_style = ParagraphStyle(
                'NoticeStyle',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#666666'),
                alignment=TA_CENTER,
                fontName='Helvetica'
            )
            elements.append(Paragraph("Personal Project", notice_style))
            elements.append(Spacer(1, 0.3*inch))
            
            # Result Status (Large and prominent)
            result_color = colors.HexColor('#00AA00') if is_pass else colors.HexColor('#CC0000')
            result_style = ParagraphStyle(
                'ResultStyle',
                parent=styles['Heading1'],
                fontSize=48,
                textColor=result_color,
                spaceAfter=30,
                spaceBefore=20,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
            elements.append(Paragraph(result_str, result_style))
            elements.append(Spacer(1, 0.4*inch))
            
            # Software Information (simplified - only essential software info)
            elements.append(Paragraph("Software Information", heading_style))
            
            software_data = [
                ['Serial Number:', serial_number],
                ['Model:', metadata.get('model', 'N/A')],
                ['Software Version:', metadata.get('software_version', 'N/A')],
                ['Firmware Version:', metadata.get('firmware_version', 'N/A')],
                ['Verification Date:', timestamp.strftime('%Y-%m-%d %H:%M:%S KST')],
            ]
            
            software_table = Table(software_data, colWidths=[2*inch, 4*inch])
            software_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F0F0')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            elements.append(software_table)
            
            # Build PDF
            doc.build(elements)
            
            return str(pdf_path)
            
        except Exception as e:
            print(f"Error generating report: {e}")
            return None
    
    def copy_files_to_result_folder(
        self,
        serial_number: str,
        is_pass: bool,
        log_file_path: str,
        parsed_csv_path: str,
        timestamp: Optional[datetime] = None
    ) -> Optional[str]:
        """
        Copy log file and parsed CSV to result folder.
        
        Args:
            serial_number: Pump serial number.
            is_pass: True if PASS, False if FAIL.
            log_file_path: Path to original log file.
            parsed_csv_path: Path to parsed CSV file.
            timestamp: Timestamp for naming (defaults to current KST time).
            
        Returns:
            Path to result folder or None if failed.
        """
        try:
            if timestamp is None:
                timestamp = self.get_kst_time()
            
            result_str = "PASS" if is_pass else "FAIL"
            folder_name = f"{serial_number}_{result_str}"
            result_folder = self.output_folder / folder_name
            
            if not ensure_directory(result_folder):
                print(f"Error: Failed to create result folder: {result_folder}")
                return None
            
            time_str = self.format_datetime_kst(timestamp)
            sn_short = truncate_serial_number(serial_number, max_length=20)
            
            # Copy log file
            log_path = Path(log_file_path)
            if log_path.exists() and log_path.is_file():
                log_dest = result_folder / f"{sn_short}_{time_str}_log{log_path.suffix}"
                try:
                    shutil.copy2(log_path, log_dest)
                except Exception as e:
                    print(f"Warning: Failed to copy log file: {e}")
            
            # Copy parsed CSV (only if different from log file and not already in result folder)
            csv_path = Path(parsed_csv_path)
            if csv_path.exists() and csv_path.is_file() and csv_path != log_path:
                csv_dest = result_folder / f"{sn_short}_{time_str}_parsed.csv"
                # Only copy if destination is different from source
                if csv_path.resolve() != csv_dest.resolve():
                    try:
                        shutil.copy2(csv_path, csv_dest)
                    except Exception as e:
                        print(f"Warning: Failed to copy parsed CSV: {e}")
            
            return str(result_folder)
            
        except Exception as e:
            print(f"Error copying files: {e}")
            return None

