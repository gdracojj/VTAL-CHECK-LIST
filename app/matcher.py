import json
import re
from pathlib import Path
from datetime import datetime, date

from .parser import norm, similarity

BASE = Path(__file__).resolve().parent.parent
SCALE = json.loads(
    (BASE / "data" / "escala.json").read_text(encoding="utf-8")
)
ALIASES = json.loads(
    (BASE / "data" / "aliases.json").read_text(encoding="utf-8")
)


def canonical_post(post):
    if not post:
        return None

    p = post.upper().strip()
    p = p.replace("P0STO-", "POSTO-")
    p = re.sub(r"^POSTO[-\s]+", "", p)

    return ALIASES.get(p, p)


def parse_date(value):
    """Converte datas comuns do parser para datetime.date."""
    if not value:
        return None

    if isinstance(value, date):
        return value

    value = str(value).strip()

    # ISO: 2026-09-04 / 2026-09-04T06:30:00
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        pass

    # BR: 04/09/2026 / 04/09/2026 06:30
    for fmt in ("%d/%m/%Y", "%d/%m/%Y %H:%M", "%d/%m/%Y %H:%M:%S"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue

    return None


def day_parity(value):
    """Retorna 'pares' ou 'impares' a partir do dia do mês."""
    parsed = parse_date(value)

    if not parsed:
        return None

    return "pares" if parsed.day % 2 == 0 else "impares"


def get_expected(plantao, message_date=None):
    """
    Retorna somente os colaboradores efetivamente escalados para o dia.

    A escala usa:
      - plantao: diurno_a / noturno_a / diurno_b / noturno_b
      - dias: pares / impares

    Assim, em uma determinada data, cada posto deve ter o colaborador
    correspondente à paridade daquele dia.
    """
    parity = day_parity(message_date)

    expected = [
        x
        for x in SCALE
        if x.get("plantao") == plantao
        and x.get("active", True)
        and (
            parity is None
            or x.get("dias") == parity
        )
    ]

    return expected


def best_employee(name, expected):
    if not name:
        return None, 0

    best = max(
        expected,
        key=lambda x: similarity(name, x.get("employee", "")),
        default=None,
    )

    score = similarity(name, best.get("employee", "")) if best else 0

    return best, score


def time_delta(actual, expected):
    if not actual or not expected:
        return None

    ah, am = map(int, actual.split(":"))
    eh, em = map(int, expected.split(":"))

    return (ah * 60 + am) - (eh * 60 + em)


def classify(parsed, expected):
    post = canonical_post(parsed.get("post_raw"))
    incoming = parsed.get("incoming")
    message_date = parsed.get("date")

    if not post:
        return {
            "status": "POSTO_NAO_LOCALIZADO",
            "post": None,
            "incoming": incoming,
            "assumption_time": parsed.get("assumption_time"),
            "expected_employee": None,
            "expected_time": None,
            "time_status": None,
            "delta_minutes": None,
            "employee_divergence": False,
            "possible_wrong_group": False,
            "employee_similarity": 0,
            "confidence": 0,
            "date": message_date,
        }

    same_post = [
        x
        for x in expected
        if canonical_post(x.get("posto", x.get("post"))) == post
    ]

    if not same_post:
        return {
            "status": "POSTO_NAO_LOCALIZADO",
            "post": post,
            "incoming": incoming,
            "assumption_time": parsed.get("assumption_time"),
            "expected_employee": None,
            "expected_time": None,
            "time_status": None,
            "delta_minutes": None,
            "employee_divergence": False,
            "possible_wrong_group": False,
            "employee_similarity": 0,
            "confidence": 0,
            "date": message_date,
        }

    # Se houver mais de um registro para o mesmo posto/paridade,
    # escolhe o colaborador mais parecido com o nome recebido.
    # Sem nome, mantém o primeiro registro da escala.
    exp, score = best_employee(incoming, same_post)

    if exp is None:
        return {
            "status": "POSTO_NAO_LOCALIZADO",
            "post": post,
            "incoming": incoming,
            "assumption_time": parsed.get("assumption_time"),
            "expected_employee": None,
            "expected_time": None,
            "time_status": None,
            "delta_minutes": None,
            "employee_divergence": False,
            "possible_wrong_group": False,
            "employee_similarity": 0,
            "confidence": 0,
            "date": message_date,
        }

    employee_match = score >= 70

    delta = time_delta(
        parsed.get("assumption_time"),
        exp.get("expected_time"),
    )

    if delta is None:
        tstatus = "HORÁRIO NÃO IDENTIFICADO"
    elif delta == 0:
        tstatus = "REGULAR"
    elif delta < 0:
        tstatus = f"ADIANTADO {abs(delta)} min"
    else:
        tstatus = f"ATRASADO {delta} min"

    msgpost = canonical_post(parsed.get("post_raw"))
    group = canonical_post(parsed.get("group"))

    wrong_group = bool(
        msgpost
        and group
        and msgpost != group
        and msgpost == canonical_post(exp.get("post"))
    )

    return {
        "status": "ASSUNÇÃO_IDENTIFICADA",
        "post": exp.get("post"),
        "incoming": incoming,
        "assumption_time": parsed.get("assumption_time"),
        "expected_employee": exp.get("employee"),
        "expected_time": exp.get("expected_time"),
        "time_status": tstatus,
        "delta_minutes": delta,
        "employee_divergence": bool(incoming) and not employee_match,
        "employee_similarity": round(score, 1),
        "possible_wrong_group": wrong_group,
        "confidence": round(score, 1),
        "date": message_date,
        "dias": exp.get("dias"),
    }


def build_report(messages, plantao):
    """
    Gera o relatório considerando a paridade do dia de cada mensagem.

    Quando existem mensagens de uma única data, essa data define a escala
    exibida no relatório. Quando existem várias datas, o matcher continua
    classificando cada mensagem com sua própria paridade e consolida os
    postos encontrados.
    """
    parsed_messages = list(messages)

    # Datas disponíveis nas mensagens.
    dates = [
        parse_date(message.get("date"))
        for message in parsed_messages
        if message.get("date")
    ]
    dates = [value for value in dates if value is not None]

    # Para o roster exibido no dashboard, usa a data das mensagens quando
    # houver uma única data. Se houver várias, usa a data mais recente.
    reference_date = max(dates) if dates else None

    expected = get_expected(plantao, reference_date)

    results = []
    seen_posts = set()

    expected_posts = {
        canonical_post(x.get("posto", x.get("post")))
        for x in expected
    }

    for parsed in parsed_messages:
        message_date = parse_date(parsed.get("date"))

        # Cada mensagem deve ser comparada contra a escala válida
        # especificamente para a data daquela mensagem.
        message_expected = get_expected(
            plantao,
            message_date or reference_date,
        )

        r = classify(parsed, message_expected)
        r["raw"] = parsed.get("raw", "")
        r["group"] = parsed.get("group")
        r["plantao"] = plantao
        r["date"] = parsed.get("date")

        results.append(r)

        if r.get("status") == "ASSUNÇÃO_IDENTIFICADA":
            post = canonical_post(r.get("post"))
            if post in expected_posts:
                seen_posts.add(post)

    # Um posto aparece uma única vez no roster do plantão.
    # Isso evita contar colaboradores alternados como se estivessem
    # trabalhando simultaneamente no mesmo posto.
    missing = []
    seen_missing_posts = set()

    for item in expected:
        post = canonical_post(item.get("posto", item.get("post")))

        if post in seen_posts or post in seen_missing_posts:
            continue

        missing.append(item)
        seen_missing_posts.add(post)

    return {
        "plantao": plantao,
        "expected_total": len({
            canonical_post(x.get("posto", x.get("post")))
            for x in expected
        }),
        "identified_total": len(seen_posts),
        "missing": missing,
        "results": results,
        "reference_date": reference_date.isoformat() if reference_date else None,
    }
