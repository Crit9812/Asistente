import json
from datetime import datetime
from pathlib import Path


LOG_PATH = Path("logs/telemetry.jsonl")


def log_event(event: dict):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "ts": datetime.utcnow().isoformat() + "Z",
        **event,
    }
    with LOG_PATH.open("a", encoding="utf-8") as archivo:
        archivo.write(json.dumps(payload, ensure_ascii=False) + "\n")
