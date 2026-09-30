from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
import json
from pathlib import Path

from .parser import parse_message
from .compare import compare
from .matcher import build_report
from .storage import load_messages, add_message, clear_messages, replace_messages

# ============================================================
# CONFIGURAÇÃO
# ============================================================

BASE = Path(__file__).resolve().parent.parent

SCALE = json.loads(
    (BASE / "data" / "escala.json").read_text(
        encoding="utf-8"
    )
)

app = FastAPI(
    title="VTAL CCOR V2"
)


# ============================================================
# TEMPLATES
# ============================================================

templates = Jinja2Templates(
    directory=str(BASE / "app" / "templates")
)


# ============================================================
# ARQUIVOS ESTÁTICOS
# ============================================================

app.mount(
    "/static",
    StaticFiles(
        directory=Path(__file__).resolve().parent / "static"
    ),
    name="static"
)


# ============================================================
# MODELOS
# ============================================================

class MessageIn(BaseModel):
    group: str = ""
    message: str
    received_at: str | None = None


# ============================================================
# DASHBOARD
# ============================================================

def dashboard_context(
    request: Request,
    plantao: str
):

    msgs = load_messages()

    plantao_validos = (
        "diurno_a",
        "noturno_a",
        "diurno_b",
        "noturno_b",
    )

    if plantao not in plantao_validos:
        plantao = "diurno_a"

    # --------------------------------------------------------
    # GERA RELATÓRIO
    # --------------------------------------------------------

    report = build_report(
        msgs,
        plantao
    )

    # --------------------------------------------------------
    # CONTADORES
    # --------------------------------------------------------

    counts = {
        "REGULAR": 0,
        "ADIANTADO": 0,
        "ATRASADO": 0,
        "SEM ASSUNÇÃO": len(report["missing"]),
        "DIVERGÊNCIA": 0,
        "IDENTIFICADA": 0,
    }

    results = []

    # --------------------------------------------------------
    # PROCESSA ASSUNÇÕES IDENTIFICADAS
    # --------------------------------------------------------

    for r in report["results"]:

        if r.get("status") != "ASSUNÇÃO_IDENTIFICADA":
            continue

        timing = (
            r.get("time_status")
            or "HORÁRIO NÃO IDENTIFICADO"
        )

        # ----------------------------------------------------
        # STATUS PRINCIPAL
        # ----------------------------------------------------

        if r.get("employee_divergence"):

            counts["DIVERGÊNCIA"] += 1
            status = "DIVERGÊNCIA"

        elif timing == "REGULAR":

            counts["REGULAR"] += 1
            status = "REGULAR"

        elif timing.startswith("ADIANTADO"):

            counts["ADIANTADO"] += 1
            status = "ADIANTADO"

        elif timing.startswith("ATRASADO"):

            counts["ATRASADO"] += 1
            status = "ATRASADO"

        else:

            counts["IDENTIFICADA"] += 1
            status = "IDENTIFICADA"

        # ----------------------------------------------------
        # MOTIVOS / ALERTAS
        # ----------------------------------------------------

        reason_parts = []

        if r.get("employee_divergence"):

           reason_parts.append(
           "Colaborador informado diferente da escala (informativo)."
     )

        if r.get("possible_wrong_group"):

            reason_parts.append(
                "Possível grupo/posto incorreto."
            )

        if not reason_parts:

            reason_parts.append(
                "Assunção identificada."
            )

        # ----------------------------------------------------
        # RESULTADO
        # ----------------------------------------------------

        results.append({
            "status": status,

            "post": r.get(
                "post"
            ),

            "expected_name": r.get(
                "expected_employee"
            ),

            "incoming": r.get(
                "incoming"
            ),

            "actual_time": (
                r.get("actual_time")
                or r.get("assumption_time")
            ),

            "expected_time": r.get(
                "expected_time"
            ),

            "reason": " ".join(
                reason_parts
            ),

            # ALERTA DE DIVERGÊNCIA
            "employee_divergence": r.get(
                "employee_divergence",
                False
            ),

            # PERCENTUAL DE SIMILARIDADE
            "employee_similarity": r.get(
                "employee_similarity"
            ),

            # ALERTA DE GRUPO/POSTO
            "possible_wrong_group": r.get(
                "possible_wrong_group",
                False
            ),
        })

    # --------------------------------------------------------
    # POSTOS SEM ASSUNÇÃO
    # --------------------------------------------------------

    for item in report["missing"]:

        results.append({
            "status": "SEM ASSUNÇÃO",

            "post": item.get(
                "post"
            ),

            "expected_name": item.get(
                "employee"
            ),

            "incoming": None,

            "actual_time": None,

            "expected_time": item.get(
                "expected_time"
            ),

            "reason": (
                "Nenhuma assunção válida "
                "identificada para o posto."
            ),

            "employee_divergence": False,

            "employee_similarity": None,

            "possible_wrong_group": False,
        })

    # --------------------------------------------------------
    # CONTEXTO DO DASHBOARD
    # --------------------------------------------------------

    return {
        "request": request,

        "counts": counts,

        "total_roster": report[
            "expected_total"
        ],

        "results": results,

        "plantao": plantao,
    }


# ============================================================
# ROTA PRINCIPAL
# ============================================================

@app.get(
    "/",
    response_class=HTMLResponse
)
def dashboard(
    request: Request,
    plantao: str = "diurno_a"
):

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context=dashboard_context(
            request,
            plantao
        )
    )


# ============================================================
# API - RELATÓRIO
# ============================================================

@app.get("/api/report")
def api_report(
    plantao: str = "diurno_a"
):
    plantao_validos = (
        "diurno_a",
        "noturno_a",
        "diurno_b",
        "noturno_b",
    )

    if plantao not in plantao_validos:
        plantao = "diurno_a"

    report = build_report(
        load_messages(),
        plantao
    )

    counts = {
        "REGULAR": 0,
        "ADIANTADO": 0,
        "ATRASADO": 0,
        "SEM ASSUNÇÃO": len(report["missing"]),
        "DIVERGÊNCIA": 0,
        "IDENTIFICADA": 0,
    }

    results = []

    for r in report["results"]:

        if r.get("status") != "ASSUNÇÃO_IDENTIFICADA":
            continue

        timing = (
            r.get("time_status")
            or "HORÁRIO NÃO IDENTIFICADO"
        )

        if r.get("employee_divergence"):

            counts["DIVERGÊNCIA"] += 1

            status = "DIVERGÊNCIA"

        elif timing == "REGULAR":

            counts["REGULAR"] += 1

            status = "REGULAR"

        elif timing.startswith("ADIANTADO"):

            counts["ADIANTADO"] += 1

            status = "ADIANTADO"

        elif timing.startswith("ATRASADO"):

            counts["ATRASADO"] += 1

            status = "ATRASADO"

        else:

            counts["IDENTIFICADA"] += 1

            status = "IDENTIFICADA"


        reason_parts = []


        if r.get("employee_divergence"):

            reason_parts.append(
                "Colaborador informado diferente da escala (informativo)."
            )


        if r.get("possible_wrong_group"):

            reason_parts.append(
                "Possível grupo/posto incorreto."
            )


        if not reason_parts:

            reason_parts.append(
                "Assunção identificada."
            )


        results.append({

            "status": status,

            "post": r.get("post"),

            "expected_name":
                r.get("expected_employee"),

            "incoming":
                r.get("incoming"),

            "actual_time":
                r.get("assumption_time"),

            "expected_time":
                r.get("expected_time"),

            "reason":
                " ".join(reason_parts),

            "employee_divergence":
                r.get(
                    "employee_divergence",
                    False
                ),

            "employee_similarity":
                r.get(
                    "employee_similarity"
                ),

            "possible_wrong_group":
                r.get(
                    "possible_wrong_group",
                    False
                ),

        })


    for item in report["missing"]:

        results.append({

            "status": "SEM ASSUNÇÃO",

            "post":
                item.get(
                    "post",
                    item.get("posto")
                ),

            "expected_name":
                item.get("employee"),

            "incoming":
                None,

            "actual_time":
                None,

            "expected_time":
                item.get("expected_time"),

            "reason":
                "Nenhuma assunção válida identificada para o posto.",

            "employee_divergence":
                False,

            "employee_similarity":
                None,

            "possible_wrong_group":
                False,

        })


    return {
        "ok": True,

        "plantao": plantao,

        "total_roster":
            report["expected_total"],

        "identified_total":
            report["identified_total"],

        "counts":
            counts,

        "results":
            results,
    }

# ============================================================
# API - RECEBER MENSAGEM
# ============================================================

@app.post("/api/messages")
def receive_message(
    payload: MessageIn
):

    received_at = (
        payload.received_at
        or datetime.now().isoformat(
            timespec="seconds"
        )
    )

    parsed = parse_message(
        payload.group,
        payload.message,
        received_at
    )

    result = compare(parsed)

    parsed["validation"] = result

    add_message(
        parsed
    )

    return parsed

# ============================================================
# API - ATUALIZAR ASSUNÇÕES
# ============================================================

@app.post("/api/refresh")
def api_refresh(
    messages: list[MessageIn]
):

    processed = []

    for payload in messages:

        received_at = (
            payload.received_at
            or datetime.now().isoformat(
                timespec="seconds"
            )
        )

        parsed = parse_message(
            payload.group,
            payload.message,
            received_at
        )

        result = compare(parsed)

        parsed["validation"] = result

        processed.append(parsed)

    # Substitui completamente os dados anteriores
    replace_messages(processed)

    return {
        "ok": True,
        "total": len(processed),
        "messages": processed
    }


# ============================================================
# API - LIMPAR MENSAGENS
# ============================================================

@app.post("/api/clear")
def api_clear():

    clear_messages()

    return {
        "ok": True
    }


# ============================================================
# PÁGINA DE TESTES
# ============================================================

@app.get(
    "/teste",
    response_class=HTMLResponse
)
def test_page(
    request: Request
):

    return templates.TemplateResponse(
        request=request,
        name="test.html",
        context={
            "request": request
        }
    )