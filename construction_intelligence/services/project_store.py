import json
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
STORE_PATH = DATA_DIR / "projects.json"


def load_projects() -> list[dict]:
    try:
        if not STORE_PATH.exists():
            return []
        data = json.loads(STORE_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def save_project(record: dict) -> bool:
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        records = load_projects()
        record["created_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        records.append(record)
        STORE_PATH.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
        return True
    except OSError:
        return False
