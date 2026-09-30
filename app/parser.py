import re
import unicodedata
from datetime import datetime
from rapidfuzz.fuzz import token_set_ratio


# ============================================================
# REGEX
# ============================================================

POST_RE = re.compile(
    r"\b[A-Z]{2}-[A-Z0-9]{2,5}-[A-Z0-9]{2,6}\b",
    re.I
)

TIME_RE = re.compile(
    r"\b([01]?\d|2[0-3])(?:h|:)([0-5]\d)?\b",
    re.I
)


# ============================================================
# NORMALIZAÇÃO
# ============================================================

def norm(text):
    """
    Remove acentos, normaliza espaços e transforma em maiúsculas.
    """
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(
        char for char in text
        if not unicodedata.combining(char)
    )

    return re.sub(r"\s+", " ", text).strip().upper()


def clean_person(text):
    """
    Limpa informações extras depois do nome.
    """
    if not text:
        return None

    text = re.split(
        r"\b(?:matr[ií]cula|assumindo|assumo|com turno|"
        r"com tudo|das?\s+\d|às?\s+\d|as\s+\d)\b",
        text,
        flags=re.I
    )[0]

    text = re.sub(
        r"^[\s:=\-]+|[\s.,;:-]+$",
        "",
        text
    )

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# POSTO
# ============================================================

def extract_post(text, group=None):
    """
    Identifica o código completo do posto.

    Exemplo:
    RO-JIP-EJIP
    AC-RBO-RBCE
    AM-MNS-CE
    """

    text = text or ""

    posts = POST_RE.findall(text)

    if posts:
        return posts[0].upper().replace("P0STO-", "")

    # Formatos alternativos
    patterns = [
        r"(?:estação|unidade)\s*[:\-]?\s*([A-Z]{2,5}-[A-Z0-9]{2,6})",
        r"(?:posto)\s*[:\-]?\s*([A-Z]{2,5}-[A-Z0-9]{2,6})",
        r"\b([A-Z]{3}-[A-Z]{2,4})\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.I)

        if match:
            return match.group(1).upper()

    # Se não encontrou o posto na mensagem,
    # utiliza o identificador do grupo.
    if group:
        return group.upper()

    return None


# ============================================================
# HORÁRIOS
# ============================================================

def extract_times(text):
    """
    Extrai horários no formato:

    07h
    07h00
    07:00
    19h00
    """

    found = []

    for match in TIME_RE.finditer(text or ""):

        hour = int(match.group(1))
        minute = int(match.group(2) or 0)

        found.append({
            "time": f"{hour:02d}:{minute:02d}",
            "pos": match.start(),
            "end": match.end()
        })

    return found


def extract_assumption_time(text):
    """
    Identifica o horário relacionado à assunção.

    Dá preferência a horários próximos de palavras como:
    assunção
    assumindo
    assumo
    recebendo
    recebido
    """

    patterns = [

        r"(?:assunção|assumindo|assumo|recebi|recebendo)"
        r".{0,100}?"
        r"\b([01]?\d|2[0-3])(?:h|:)([0-5]\d)?\b",

        r"\b(?:horário)\s*[:=]\s*"
        r"([01]?\d|2[0-3])(?:h|:)([0-5]\d)?\b",

        r"\b([01]?\d|2[0-3])"
        r"(?:h|:)([0-5]\d)?"
        r"\s*(?:às|as|a|até|-)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text or "",
            re.I | re.S
        )

        if match:

            hour = int(match.group(1))
            minute = int(match.group(2) or 0)

            return f"{hour:02d}:{minute:02d}"

    # Fallback:
    # pega o primeiro horário encontrado.
    times = extract_times(text)

    if times:
        return times[0]["time"]

    return None


# ============================================================
# PESSOA QUE ESTÁ ASSUMINDO
# ============================================================

def extract_incoming(text):
    text = text or ""

    patterns = [
        r"(?:vigia|vigilante)\s*[:=]\s*([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ .'-]{2,80})",
        r"assumindo\s+serviço[^\n]*\n\s*([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ .'-]{2,80})",
        r"assumindo\s+serviço[^\n]*\n\s*([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ .'-]{2,80})\s*$",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            return clean_person(match.group(1))

    return None


# ============================================================
# PESSOA QUE ESTÁ SAINDO
# ============================================================

def extract_outgoing(text):

    text = text or ""

    patterns = [

        # Exemplo:
        # do vigia João da Silva
        r"(?:do|da|de)\s+"
        r"(?:vigia|vigilante)"
        r"\s*[:=]?\s*"
        r"([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ .'-]{2,80})",

        # Exemplos:
        # saindo João da Silva
        # rendendo João da Silva
        # recebi o serviço de João da Silva

        r"(?:saindo|rendendo|"
        r"recebi\s+(?:o\s+serviço|o\s+posto|o\s+plantão)"
        r"\s*(?:do|de)?|"
        r"recebendo\s+(?:o\s+plantão)\s+do)"
        r"\s*[:=]?\s*"
        r"([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ .'-]{2,80})",

        # Exemplo:
        # para o Vigia João da Silva

        r"(?:para\s+o\s+(?:Porteiro|Vigia)"
        r"|do\s+Vigia)"
        r"\s+"
        r"([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ .'-]{2,80})",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.I
        )

        if match:
            return clean_person(match.group(1))

    return None


# ============================================================
# DATA
# ============================================================

def extract_date(text, received_at=None):

    text = text or ""

    patterns = [

        # 29/09/2026
        r"\b(\d{1,2})[\/:\-](\d{1,2})[\/:\-](20\d{2})\b",

        # 29/09/26
        r"\b(\d{1,2})[\/:\-](\d{1,2})[\/:\-](\d{2})\b",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text
        )

        if match:

            year = int(match.group(3))

            if year < 100:
                year += 2000

            day = int(match.group(1))
            month = int(match.group(2))

            return (
                f"{year:04d}-"
                f"{month:02d}-"
                f"{day:02d}"
            )

    # Se a mensagem não tiver data,
    # utiliza a data em que foi recebida.

    if received_at:

        try:
            return datetime.fromisoformat(
                received_at
            ).date().isoformat()

        except Exception:
            pass

    return None


# ============================================================
# PARSER PRINCIPAL
# ============================================================

def parse_message(
    group,
    text,
    received_at=None
):

    return {

        "group": group,

        "raw": text,

        "post_raw": extract_post(
            text,
            group
        ),

        "incoming": extract_incoming(
            text
        ),

        "outgoing": extract_outgoing(
            text
        ),

        "assumption_time": extract_assumption_time(
            text
        ),

        "date": extract_date(
            text,
            received_at
        ),

        "received_at": received_at,
    }


# ============================================================
# COMPARAÇÃO DE NOMES
# ============================================================

def similarity(a, b):

    if not a or not b:
        return 0

    return token_set_ratio(
        norm(a),
        norm(b)
    )