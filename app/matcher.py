import json, re
from pathlib import Path
from datetime import datetime
from .parser import norm, similarity

BASE = Path(__file__).resolve().parent.parent
SCALE = json.loads((BASE / "data" / "escala.json").read_text(encoding="utf-8"))
ALIASES = json.loads((BASE / "data" / "aliases.json").read_text(encoding="utf-8"))


def canonical_post(post):
    if not post:
        return None

    p = post.upper().strip()
    p = p.replace("P0STO-", "POSTO-")
    p = re.sub(r"^POSTO[-\s]+", "", p)

    return ALIASES.get(p, p)


def get_expected(plantao):
    return [
        x for x in SCALE
        if x.get("plantao") == plantao
        and x.get("active", True)
    ]


def best_employee(name, expected):
    if not name:
        return None, 0

    best = max(
        expected,
        key=lambda x: similarity(name, x["employee"]),
        default=None
    )

    score = similarity(name, best["employee"]) if best else 0

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
    date = parsed.get("date")

    if not date:
        date = expected[0]["date"] if expected else None

    same_post = [
        x for x in expected
        if canonical_post(x.get("posto", x.get("post"))) == post
    ]

    # Posto não localizado na escala ativa
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
        }

    # Posto localizado
    exp = same_post[0]

    score = similarity(
        incoming,
        exp["employee"]
    ) if incoming else 0

    employee_match = score >= 70

    delta = time_delta(
        parsed.get("assumption_time"),
        exp["expected_time"]
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
        and msgpost == canonical_post(exp["post"])
    )

    return {
        "status": "ASSUNÇÃO_IDENTIFICADA",
        "post": exp["post"],
        "incoming": incoming,
        "assumption_time": parsed.get("assumption_time"),
        "expected_employee": exp["employee"],
        "expected_time": exp["expected_time"],
        "time_status": tstatus,
        "delta_minutes": delta,
        "employee_divergence": bool(incoming) and not employee_match,
        "employee_similarity": round(score, 1),
        "possible_wrong_group": wrong_group,
        "confidence": round(score, 1),
    }


def build_report(messages, plantao):
    expected = get_expected(plantao)

    results = []
    seen_posts = set()

    expected_posts = {
        canonical_post(x.get("posto", x.get("post")))
        for x in expected
    }

    for parsed in messages:
        r = classify(parsed, expected)

        r["raw"] = parsed.get("raw", "")
        r["group"] = parsed.get("group")
        r["plantao"] = plantao
        r["date"] = parsed.get("date")

        results.append(r)

        if r.get("post") in expected_posts:
            seen_posts.add(r["post"])

    missing = [
        x for x in expected
        if canonical_post(x.get("posto", x.get("post"))) not in seen_posts
    ]

    return {
        "plantao": plantao,
        "expected_total": len(expected),
        "identified_total": len(seen_posts),
        "missing": missing,
        "results": results,
    }