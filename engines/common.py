
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]

def load_json(path: str):
    p = ROOT / path
    if not p.exists():
        return {}
    return json.loads(p.read_text())

def save_json(path: str, data):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
