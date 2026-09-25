# VTAL CCOR V2 — frontend integrado

O `dashboard.html` foi substituído pelo frontend original fornecido pelo usuário.

## O que foi integrado
- Frontend original em `app/templates/dashboard.html`.
- Backend adaptado para fornecer `counts`, `total_roster` e `results` esperados pelo Jinja.
- Servimento de `/static` para a logo.
- A lógica V2 de escala por data/turno continua no backend.

## Rodar
```bat
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
playwright install chromium
python -m uvicorn app.main:app --reload
```

Abra `http://127.0.0.1:8000`.

> A logo SVG incluída é um placeholder textual porque o arquivo da logo oficial não veio junto com o HTML. Se você tiver a logo oficial, basta substituir `app/static/pd7_logo_branca.svg` mantendo o mesmo nome.
