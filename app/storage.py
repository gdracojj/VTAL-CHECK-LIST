from pathlib import Path
import json

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
MESSAGES = DATA / "messages.json"

def load_roster():
    return json.loads((DATA / "escala.json").read_text(encoding="utf-8"))

def load_messages():
    if not MESSAGES.exists():
        return []
    return json.loads(MESSAGES.read_text(encoding="utf-8"))

def save_message(item):
    items = load_messages()
    items.append(item)
    MESSAGES.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

def clear_messages():
    MESSAGES.write_text("[]", encoding="utf-8")
