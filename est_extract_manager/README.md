# Pump EST Config Verification Tool

**📌 Personal Project**

Automated tool for verifying pump EST log files against a master configuration list, generating professional reports, and updating SharePoint lists. Designed for easy use by field workers.

## Features

- **Automated File Detection**: Monitors a watch folder for new EST log files using Watchdog
- **Configuration Verification**: Verifies pump serial numbers against master configuration list
- **Professional Reports**: Generates clean PDF reports with essential information
- **SharePoint Integration**: Automatically updates SharePoint lists with verification results
- **Time-based Sorting**: Results are sorted by time (ascending) for easy duplicate detection
- **Configurable Paths**: All file paths are configurable via Streamlit UI

## Requirements

See `requirements.txt` for required Python packages.

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Configure SharePoint credentials (for corporate environments):
   - Option 1: Set environment variables for App Credentials (recommended):
     - `SHAREPOINT_CLIENT_ID`: Azure AD App Registration Client ID
     - `SHAREPOINT_CLIENT_SECRET`: Azure AD App Registration Client Secret
   - Option 2: Set environment variables for User Credentials:
     - `SHAREPOINT_USERNAME`: SharePoint username
     - `SHAREPOINT_PASSWORD`: SharePoint password

## Usage

1. Run the Streamlit application:
```bash
streamlit run app.py
```

2. Configure paths in the sidebar:
   - Master Config List Path: Path to `Master_Config_List.xlsx`
   - Watch Folder Path: Folder to monitor for new EST log files
   - Output Folder Path: Folder to save verification results
   - SharePoint Site URL: SharePoint site URL (optional)
   - SharePoint List Name: Name of SharePoint list (optional)

3. Start monitoring:
   - Click "Start Monitoring" to begin automatic file processing
   - Or upload files manually for processing

## File Structure

- `app.py`: Main Streamlit application
- `config.py`: Configuration management
- `log_parser.py`: EST log file parser (supports CSV, Excel, INI formats)
- `verifier.py`: Configuration verification logic
- `reporter.py`: PDF report generator
- `sharepoint_utils.py`: SharePoint integration (optional)
- `monitor.py`: Folder monitoring with Watchdog
- `processor.py`: Main processing orchestration
- `utils.py`: Common utility functions

## Output Format

Results are saved in folders named `{SerialNumber}_{PASS|FAIL}` containing:
- PDF report: `{SerialNumber}_{YYYYMMDD_HHMMSS}_{PASS|FAIL}.pdf`
- Original log: `{SerialNumber}_{YYYYMMDD_HHMMSS}_log.csv`
- Parsed CSV: `{SerialNumber}_{YYYYMMDD_HHMMSS}_parsed.csv`

All timestamps are in KST (Korea Standard Time, Asia/Seoul).

## Master Config List Format

The `Master_Config_List.xlsx` file should contain the following columns:
- `Pump_Serial_No`: Pump serial number
- `Target_Config_Tag`: Configuration tag identifier
- `Parameter_Match`: Parameter name to match in EST log
- `Section_Match`: Section name to match in EST log
- `Target_Value`: Target configuration value
- `Original_Value`: Original configuration value
- `Section`: Section category

## Supported File Formats

The tool supports multiple EST log file formats:
- **CSV files** (.csv): Standard table format, header+table format, INI-style format
- **Excel files** (.xlsx, .xls): Automatically converted and parsed

## About This Project

**This is a personal project** designed to help field workers easily verify EST log configurations. The tool is built with simplicity and ease of use in mind.

## Notes

- All UI text, logs, and reports are in English (with Korean labels for field workers)
- Reports use Calibri font
- Code follows PEP8 standards
- File paths are configurable
- Results are sorted by time (ascending) for duplicate detection
- SharePoint integration is optional and won't stop processing if it fails
- Serial numbers are compared using only numeric digits for robust matching
- Clean, simple UI designed for field workers

