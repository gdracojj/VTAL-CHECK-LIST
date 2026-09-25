
import json
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
MESSAGES = DATA / "messages.json"

def load_messages():
    if not MESSAGES.exists():
        return []
    try:
        return json.loads(MESSAGES.read_text(encoding="utf-8"))
    except Exception:
        return []

def save_messages(items):
    MESSAGES.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

def add_message(item):
    items = load_messages()
    item = dict(item)
    item.setdefault("id", f"{datetime.now().timestamp():.6f}")
    items.append(item)
    save_messages(items)
    return item

def clear_messages():
    save_messages([])
