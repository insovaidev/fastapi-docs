from __future__ import annotations

import csv
import json
from datetime import datetime, timedelta
from pathlib import Path

from app.core.config import settings


BASE_DIR = settings.base_dir
STORAGE_DIR = settings.storage_dir
DOCS_DIR = settings.docs_dir
UPLOADS_DIR = settings.uploads_dir
TEMP_DIR = settings.temp_dir
IMAGES_DIR = settings.images_dir


def files():
    """Run all file-system learning examples."""
    ensure_storage_dirs()

    print("1. text file write/read")
    print(write_and_read_text_file())

    # print("\n2. append log file")
    # print(append_log_entry("User opened the file lesson"))

    # print("\n3. save uploaded file")
    # print(save_uploaded_file("resume.txt", "This came from a fake upload form (Update)."))

    # print("\n4. export CSV")
    # print(export_users_to_csv())

    # print("\n5. generate report")
    # print(generate_sales_report())

    # print("\n6. cache JSON")
    # print(cache_api_response())

    # print("\n7. temp file lifecycle")
    # print(temp_file_example())

    # print("\n8. list storage files")
    # for item in list_storage_files():
    #     print(item)


def ensure_storage_dirs():
    """Create the folders we use for file examples."""
    for folder in (DOCS_DIR, UPLOADS_DIR, TEMP_DIR, IMAGES_DIR):
        folder.mkdir(parents=True, exist_ok=True)


def write_and_read_text_file() -> str:
    """Create a text document and read it back."""
    file_path = DOCS_DIR / "notes.txt"
    content = "Python file handling basics\n- write\n- read\n- append\n- last line\n- end"

    file_path.write_text(content, encoding="utf-8")

    return file_path.read_text(encoding="utf-8")


def append_log_entry(message: str) -> str:
    """Append one log line with a timestamp."""
    log_dir = TEMP_DIR / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_path = log_dir / "app.log"
    timestamp = datetime.now().isoformat(timespec="seconds")

    with log_path.open("a", encoding="utf-8") as file:
        file.write(f"[{timestamp}] {message}\n")

    return str(log_path)


def save_uploaded_file(filename: str, content: str) -> str:
    """Simulate storing an uploaded text file."""
    file_path = UPLOADS_DIR / filename
    file_path.write_text(content, encoding="utf-8")
    return str(file_path)


def save_uploaded_image(filename: str, content: bytes) -> str:
    """Simulate storing uploaded image bytes."""
    file_path = IMAGES_DIR / filename
    file_path.write_bytes(content)
    return str(file_path)


def export_users_to_csv() -> str:
    """Export structured data to CSV."""
    export_path = DOCS_DIR / "users_export.csv"
    users = [
        {"id": 1, "name": "Dara", "role": "Backend Developer"},
        {"id": 2, "name": "Sokun", "role": "QA Engineer"},
    ]

    with export_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["id", "name", "role"])
        writer.writeheader()
        writer.writerows(users)

    return str(export_path)


def generate_sales_report() -> str:
    """Create a simple report file like a backend export/report task."""
    report_path = DOCS_DIR / "sales_report.txt"
    report_lines = [
        "Monthly Sales Report",
        "====================",
        "Total Orders: 24",
        "Total Revenue: 4800 USD",
        "Top Product: Python API Course",
    ]

    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    return str(report_path)


def cache_api_response() -> dict:
    """Cache JSON data to avoid repeating an expensive operation."""
    cache_dir = TEMP_DIR / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    cache_path = cache_dir / "user_1.json"
    user_data = {"id": 1, "name": "Dara", "skills": ["python", "django", "sql"]}

    cache_path.write_text(json.dumps(user_data, indent=2), encoding="utf-8")
    return json.loads(cache_path.read_text(encoding="utf-8"))


def temp_file_example() -> str:
    """Keep a temp file for 1 day, then delete it if expired."""
    temp_file = TEMP_DIR / "session.tmp"
    now = datetime.now()
    expires_after = timedelta(minutes=1)

    if not temp_file.exists():
        temp_file.write_text("Temporary session data", encoding="utf-8")
        return f"{temp_file} | created now | expires after 1 day"

    modified_at = datetime.fromtimestamp(temp_file.stat().st_mtime)
    age = now - modified_at

    if age >= expires_after:
        temp_file.unlink(missing_ok=True)
        return f"{temp_file} | expired after 1 day | deleted"

    remaining = expires_after - age
    hours_left = int(remaining.total_seconds() // 3600)
    minutes_left = int((remaining.total_seconds() % 3600) // 60)

    return (
        f"{temp_file} | still valid | "
        f"time left: {hours_left}h {minutes_left}m"
    )


def list_storage_files() -> list[str]:
    """List files created inside storage for inspection."""
    ensure_storage_dirs()

    items = []
    for path in STORAGE_DIR.rglob("*"):
        if path.is_file():
            items.append(str(path.relative_to(BASE_DIR)))

    return sorted(items)