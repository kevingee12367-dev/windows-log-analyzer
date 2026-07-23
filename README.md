# Windows Security Log Analyzer (Python Automation Project)

A Python-based automation tool that parses Windows Security XML logs and generates structured TXT and JSON reports. Includes cloud-ready export features such as metadata generation and S3-style folder structures.

## Features
- Parses Windows Event Logs (4624, 4625, 4740)
- Generates `report.txt` and `summary.json`
- Creates metadata JSON files for cloud ingestion
- Builds S3-style folder paths for cloud export
- Fully automated pipeline

## Project Structure
windows_log_analyzer/
│
├── analyzer.py
├── sample_logs/
│     └── sample_demo.xml
├── output/          (empty — generated at runtime)
└── cloud_export/    (empty — generated at runtime)


## How It Works
1. Parses XML logs in `sample_logs/`
2. Generates TXT and JSON reports in `output/`
3. Copies reports into `cloud_export/`
4. Creates metadata files
5. Builds S3-style folder structure inside `cloud_export/logs/`

## Technologies Used
- Python 3
- XML parsing
- JSON automation
- Cloud export simulation

## Author
Kevin Gee Jr
