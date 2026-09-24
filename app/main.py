from datetime import datetime, timedelta
import json
import pathlib

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from .matcher import compare, dashboard
from .parser import parse_message
from .storage import clear_messages, load_messages, load_roster, save_message

# 1. Caminhos absolutos dinâmicos para evitar erros de diretório
BASE_DIR = pathlib.Path(__file__).resolve().parent

app = FastAPI(title="VTAL CCOR - V1")

# 2. Configura a pasta de arquivos estáticos (app/static)
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# 3. Configura a pasta de templates (app/templates)
TEMPLATES_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

TIMEZONE_OFFSETS = {
    "DF": 0,
    "SP": 0,
    "RJ": 0,
    "BA": 0,
    "AM": -1,
    "RR": -1,
    "RO": -1,
    "AC": -2,
}


def convert_to_local_time(whatsapp_time, state):
    if not whatsapp_time:
        return None

    try:
        dt = datetime.fromisoformat(whatsapp_time)
    except ValueError:
        return whatsapp_time

    offset = TIMEZONE_OFFSETS.get((state or "").upper(), 0)
    local = dt + timedelta(hours=offset)
    return local.strftime("%Y-%m-%d %H:%M:%S")


class MessageIn(BaseModel):
    text: str
    date: str | None = None
    group: str | None = None
    whatsapp_time: str | None = None
    state: str | None = None


# Rota principal para carregar o Dashboard
@app.get("/", response_class=HTMLResponse)
def get_dashboard(request: Request):
    messages = load_messages()
    roster = load_roster()

    # Executa a regra de comparação/métrica do dashboard
    results, counts = dashboard(messages, roster)

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "results": results,
            "counts": counts,
            "total_roster": len(roster),
        },
    )


@app.post("/api/messages")
def receive_message(body: MessageIn):
    parsed = parse_message(body.text, body.date)

    item = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "received_at": datetime.now().isoformat(timespec="seconds"),
        "whatsapp_time": body.whatsapp_time,
        "state": body.state,
        "group": body.group,
        "parsed": parsed,
    }

    save_message(item)

    return {
        "ok": True,
        "parsed": parsed,
        "result": compare(parsed, load_roster()),
    }


@app.post("/api/clear")
def clear():
    clear_messages()
    return {"ok": True}


@app.get("/teste", response_class=HTMLResponse)
def test_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="test.html", context={}
    )


@app.post("/teste/exemplos")
def examples():
    clear_messages()
    samples_path = BASE_DIR.parent / "data" / "exemplos.json"
    if samples_path.exists():
        samples = json.loads(samples_path.read_text(encoding="utf-8"))
        for s in samples:
            parsed = parse_message(s["text"], "24/09/2026")
            save_message({
                "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                "received_at": datetime.now().isoformat(timespec="seconds"),
                "group": s.get("group"),
                "parsed": parsed,
            })
    return RedirectResponse("/", status_code=303)