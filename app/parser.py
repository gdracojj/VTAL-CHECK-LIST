
import re
import unicodedata
from datetime import datetime
from rapidfuzz.fuzz import token_set_ratio

POST_RE = re.compile(r"\b[A-Z]{2}-[A-Z0-9]{2,5}-[A-Z0-9]{2,6}\b", re.I)
TIME_RE = re.compile(r"\b([01]?\d|2[0-3])(?:h|:)([0-5]\d)?\b", re.I)

INCOMING_PATTERNS = [
    r"(?:vigia|vigilante)\s*[:=]\s*([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ .'-]{2,80})",
    r"(?:assumindo(?:\s+o)?\s+(?:serviço|plantão|posto|posto de serviço))\s*(?:do|de|as|às|das)?\s*([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ .'-]{2,80})",
]
OUTGOING_PATTERNS = [
    r"(?:saindo|rendendo|recebi\s+(?:o|do)\s+(?:posto|serviço|plantão)\s*(?:de|do)?|assumindo\s+(?:o\s+serviço|o\s+plantão)\s+do)\s*[:=]?\s*([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ .'-]{2,80})",
    r"(?:recebendo\s+o\s+plantão\s+do|recebi\s+o\s+serviço\s+do|recebi\s+o\s+posto\s+de|do\s+vigia)\s*[:=]?\s*([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ .'-]{2,80})",
]

STOP_WORDS = {
    "assumindo","serviço","servico","plantão","plantao","posto","vigia","vigilante",
    "horário","horario","horas","hora","as","às","ate","até","recebi","recebendo",
    "o","a","do","da","de","com","sem","tudo","em","ordem","turno","matrícula","matricula"
}

def norm(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s).strip().upper()

def clean_person(s):
    s = re.split(r"\b(?:matr[ií]cula|assumindo|assumo|com turno|com tudo|das?\s+\d|às?\s+\d|as\s+\d)\b", s, flags=re.I)[0]
    s = re.sub(r"^[\s:=\-]+|[\s.,;:-]+$", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()

def extract_post(text, group=None):
    posts = POST_RE.findall(text or "")
    if posts:
        return posts[0].upper().replace("P0STO-", "")
    # Common labels without the full UF prefix
    patterns = [
        r"(?:esta[cç][aã]o|unidade)\s*[:\-]?\s*([A-Z]{2,5}-[A-Z0-9]{2,6})",
        r"(?:posto)\s*[:\-]?\s*([A-Z]{2,5}-[A-Z0-9]{2,6})",
        r"\b([A-Z]{3}-[A-Z]{2,4})\b",
    ]
    for p in patterns:
        m = re.search(p, text or "", re.I)
        if m:
            return m.group(1).upper()
    if group:
        return group.upper()
    return None

def extract_times(text):
    found = []
    for m in TIME_RE.finditer(text or ""):
        hh = int(m.group(1)); mm = int(m.group(2) or 0)
        found.append({"time": f"{hh:02d}:{mm:02d}", "pos": m.start(), "end": m.end()})
    return found

def extract_assumption_time(text):
    # Prefer times near explicit assumption language.
    patterns = [
        r"(?:assun[cç][aã]o|assumindo|assumo|receb[ií]|recebendo).{0,100}?\b([01]?\d|2[0-3])(?:h|:)([0-5]\d)?\b",
        r"\b(?:hor[aá]rio)\s*[:=]\s*([01]?\d|2[0-3])(?::|h)([0-5]\d)?\b",
        r"\b([01]?\d|2[0-3])(?:h|:)([0-5]\d)?\s*(?:às|as|a|até|-)",
    ]
    for p in patterns:
        m = re.search(p, text or "", re.I | re.S)
        if m:
            return f"{int(m.group(1)):02d}:{int(m.group(2) or 0):02d}"
    times = extract_times(text)
    return times[0]["time"] if times else None

def extract_incoming(text):
    # Explicit "Vigia:" or "Vigia=" is normally the incoming person.
    for p in INCOMING_PATTERNS[:1]:
        m = re.search(p, text or "", re.I)
        if m:
            return clean_person(m.group(1))
    # "Eu / Vigia X" and "Vigia X estou recebendo..." forms
    m = re.search(r"\bVigia\s+([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ .'-]{2,80}?)(?:\s+estou\s+recebendo|\s+assumindo|\s*,|\s+com turno|\s*$)", text or "", re.I | re.S)
    if m:
        return clean_person(m.group(1))
    # "Assunção ... Cláudio Roberto Assumiu"
    m = re.search(r"\b([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ .'-]{2,60})\s+assumiu\b", text or "", re.I)
    if m:
        return clean_person(m.group(1))
    # "Assunção ... NOME assumindo"
    m = re.search(r"(?:assunção(?:\s+de\s+serviço)?|assun[cç][aã]o\s+de\s+plant[aã]o).{0,80}?\b([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ .'-]{2,70}?)\s+assum(?:indo|iu)\b", text or "", re.I | re.S)
    if m:
        return clean_person(m.group(1))
    return None

def extract_outgoing(text):
    patterns = [
        r"(?:do|da|de)\s+(?:vigia|vigilante)\s*[:=]?\s*([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ .'-]{2,80})",
        r"(?:saindo|rendendo|recebi\s+(?:o\s+serviço|o\s+posto|o\s+plantão)\s*(?:do|de)?|recebendo\s+(?:o\s+plantão)\s+do)\s*[:=]?\s*([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ .'-]{2,80})",
        r"(?:para\s+o\s+(?:Porteiro|Vigia)|do\s+Vigia)\s+([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ .'-]{2,80})",
    ]
    for p in patterns:
        m = re.search(p, text or "", re.I)
        if m:
            return clean_person(m.group(1))
    return None

def extract_date(text, received_at=None):
    patterns = [
        r"\b(\d{1,2})[\/:\-](\d{1,2})[\/:\-](20\d{2})\b",
        r"\b(\d{1,2})[\/:\-](\d{1,2})[\/:\-](\d{2})\b",
    ]
    for p in patterns:
        m = re.search(p, text or "")
        if m:
            y = int(m.group(3)); y += 2000 if y < 100 else 0
            return f"{y:04d}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    if received_at:
        try:
            return datetime.fromisoformat(received_at).date().isoformat()
        except Exception:
            pass
    return None

def parse_message(group, text, received_at=None):
    return {
        "group": group,
        "raw": text,
        "post_raw": extract_post(text, group),
        "incoming": extract_incoming(text),
        "outgoing": extract_outgoing(text),
        "assumption_time": extract_assumption_time(text),
        "date": extract_date(text, received_at),
        "received_at": received_at,
    }

def similarity(a,b):
    if not a or not b: return 0
    return token_set_ratio(norm(a), norm(b))
