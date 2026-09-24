import re
import unicodedata

POST_RE = re.compile(r"\b[A-Z]{2}-[A-Z0-9]{2,4}-[A-Z0-9]{2,5}\b")
TIME_RE = re.compile(r"\b([01]?\d|2[0-3])\s*(?::|h)\s*(\d{0,2})\b", re.I)

def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return " ".join(s.lower().split())

def extract_post(text):
    m = POST_RE.search(text.upper())
    return m.group(0) if m else None

def extract_times(text):
    return [f"{int(h):02d}:{int(m or 0):02d}" for h,m in TIME_RE.findall(text)]

def extract_incoming(text):
    patterns = [
        r"(?im)^\s*(?:vigia|vigilante|colaborador|nome)\s*:\s*(.+?)(?:\s*[-–—]\s*matr[ií]cula.*)?$",
        r"(?im)^\s*entrando\s*:\s*(.+)$",
        r"(?im)assumindo\s+(?:o\s+servi[cç]o|o\s+plant[aã]o)\s+(.+?)(?:\s+as\s+|\s+às\s+|\s+das\s+)",
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(1).strip(" -–—:")
    return None

def extract_outgoing(text):
    patterns = [
        r"(?im)^\s*saindo\s*:\s*(.+)$",
        r"(?im)rendendo\s+(?:o\s+vigia\s+)?(.+?)(?:\n|$)",
        r"(?im)recebi\s+o\s+posto\s+de\s+(.+?)(?:\n|$)",
        r"(?im)assumindo\s+o\s+servi[cç]o\s+do\s+vigia\s+(.+?)(?:\s+com\s+|\n|$)",
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(1).strip(" -–—:")
    return None

def parse_message(text, message_date=None):
    times = extract_times(text)
    return {
        "post": extract_post(text),
        "incoming": extract_incoming(text),
        "outgoing": extract_outgoing(text),
        "time": times[0] if times else None,
        "date": message_date,
        "raw": text
    }
