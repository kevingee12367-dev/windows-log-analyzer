import xml.etree.ElementTree as ET
import json
import os
from datetime import datetime

# Paths
LOGS_FOLDER = "sample_logs"
OUTPUT_FOLDER = "output"

def generate_s3_object_name(filename: str) -> str:
    """Return an S3-style object name for a given file."""
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")

    prefix = "windows/security/logs"
    return f"{prefix}/{year}/{month}/{day}/{filename}"


def parse_logs():
    failed_logins = []
    account_lockouts = []
    successful_logins = []

    for file in os.listdir(LOGS_FOLDER):
        if file.endswith(".xml"):
            path = os.path.join(LOGS_FOLDER, file)
            tree = ET.parse(path)
            root = tree.getroot()

            for event in root.findall(".//Event"):
                event_id = event.find(".//EventID").text

                if event_id == "4625":  # Failed login
                    failed_logins.append(event_id)

                elif event_id == "4740":  # Account lockout
                    account_lockouts.append(event_id)

                elif event_id == "4624":  # Successful login
                    successful_logins.append(event_id)

    return failed_logins, account_lockouts, successful_logins


def generate_report(failed, lockouts, success):
    # -----------------------------
    # Build report text
    # -----------------------------
    report_text = (
        f"Failed Logins: {len(failed)}\n"
        f"Account Lockouts: {len(lockouts)}\n"
        f"Successful Logins: {len(success)}\n"
    )

    # -----------------------------
    # Generate S3-style object names
    # -----------------------------
    s3_report_name = generate_s3_object_name("report.txt")
    s3_summary_name = generate_s3_object_name("summary.json")

    print("S3 Object Name (TXT):", s3_report_name)
    print("S3 Object Name (JSON):", s3_summary_name)

    # -----------------------------
    # Step 1: Write TXT + JSON output
    # -----------------------------
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    report_path = os.path.join(OUTPUT_FOLDER, "report.txt")
    summary_path = os.path.join(OUTPUT_FOLDER, "summary.json")

    with open(report_path, "w") as f:
        f.write(report_text)

    summary = {
        "failed_logins": len(failed),
        "account_lockouts": len(lockouts),
        "successful_logins": len(success)
    }

    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=4)

    print("Step 1 complete: TXT and JSON written to output/")

    # -----------------------------
    # Step 2: Copy files into cloud_export/
    # -----------------------------
    cloud_folder = "cloud_export"
    os.makedirs(cloud_folder, exist_ok=True)

    txt_dest = os.path.join(cloud_folder, "report.txt")
    json_dest = os.path.join(cloud_folder, "summary.json")

    with open(report_path, "r") as src, open(txt_dest, "w") as dst:
        dst.write(src.read())

    with open(summary_path, "r") as src, open(json_dest, "w") as dst:
        dst.write(src.read())

    print("Step 2 complete: Files copied to cloud_export/")

    # -----------------------------
    # Step 3: Create metadata folder + metadata files
    # -----------------------------
    metadata_folder = os.path.join(cloud_folder, "metadata")
    os.makedirs(metadata_folder, exist_ok=True)

    report_metadata = {
        "object_name": s3_report_name,
        "content_type": "text/plain",
        "size_bytes": os.path.getsize(txt_dest),
        "created_at": datetime.now().isoformat()
    }

    summary_metadata = {
        "object_name": s3_summary_name,
        "content_type": "application/json",
        "size_bytes": os.path.getsize(json_dest),
        "created_at": datetime.now().isoformat()
    }

    with open(os.path.join(metadata_folder, "report_metadata.json"), "w") as f:
        json.dump(report_metadata, f, indent=4)

    with open(os.path.join(metadata_folder, "summary_metadata.json"), "w") as f:
        json.dump(summary_metadata, f, indent=4)

    print("Step 3 complete: Metadata generated in cloud_export/metadata/")

    # -----------------------------
    # Step 4: Create logs/ folder with S3-style paths
    # -----------------------------
    logs_root = os.path.join(cloud_folder, "logs")
    os.makedirs(logs_root, exist_ok=True)

    # Build full S3-style folder path inside cloud_export/logs/
    s3_folder_path = os.path.join(logs_root, s3_report_name.rsplit("/", 1)[0])
    os.makedirs(s3_folder_path, exist_ok=True)

    # Copy files into S3-style folder structure
    s3_report_dest = os.path.join(s3_folder_path, "report.txt")
    s3_summary_dest = os.path.join(s3_folder_path, "summary.json")

    with open(txt_dest, "r") as src, open(s3_report_dest, "w") as dst:
        dst.write(src.read())

    with open(json_dest, "r") as src, open(s3_summary_dest, "w") as dst:
        dst.write(src.read())

    print("Step 4 complete: Logs exported into S3-style folder structure.")


def main():
    failed, lockouts, success = parse_logs()
    generate_report(failed, lockouts, success)
    print("Analysis complete. Check the cloud_export folder.")


if __name__ == "__main__":
    main()
