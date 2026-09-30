import json
from pathlib import Path

from .parser import norm, similarity


BASE_DIR = Path(__file__).resolve().parent.parent
ESCALA_FILE = BASE_DIR / "data" / "escala.json"


def load_roster():
    with open(ESCALA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def compare(parsed):
    roster = load_roster()

    incoming = parsed.get("incoming")
    post = parsed.get("post_raw")
    assumption_time = parsed.get("assumption_time")
    date = parsed.get("date")

    if not incoming:
        return {
            "status": "PENDENTE",
            "reason": "Colaborador não identificado",
            "employee": None,
            "post": post,
            "expected_time": None,
            "received_time": assumption_time,
        }

    candidates = []

    for employee in roster:
        if not employee.get("active", True):
            continue

        name_score = similarity(
            incoming,
            employee.get("employee", "")
        )

        if name_score >= 70:
            candidates.append((name_score, employee))

    if not candidates:
        return {
            "status": "DIVERGÊNCIA",
            "reason": "Colaborador não encontrado na escala",
            "employee": incoming,
            "post": post,
            "expected_time": None,
            "received_time": assumption_time,
        }

    candidates.sort(key=lambda x: x[0], reverse=True)
    score, employee = candidates[0]

    post_ok = norm(post) == norm(employee.get("post", ""))

    time_ok = (
        assumption_time == employee.get("expected_time")
    )

    if post_ok and time_ok:
        status = "OK"
        reason = "Assunção conforme escala"
    elif not post_ok and not time_ok:
        status = "DIVERGÊNCIA"
        reason = "Posto e horário divergentes"
    elif not post_ok:
        status = "DIVERGÊNCIA"
        reason = "Posto divergente"
    else:
        status = "DIVERGÊNCIA"
        reason = "Horário divergente"

    return {
        "status": status,
        "reason": reason,
        "employee": employee.get("employee"),
        "post": post,
        "expected_post": employee.get("post"),
        "expected_time": employee.get("expected_time"),
        "received_time": assumption_time,
        "score": score,
        "date": date,
    }