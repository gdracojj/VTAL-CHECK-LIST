# VTAL CCOR - V1

Primeira versao do sistema de conferencia de assuncoes.

Rodar:
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --reload

Abra http://127.0.0.1:8000
Teste em http://127.0.0.1:8000/teste

Nesta V1 o WhatsApp Web ainda nao esta conectado. A API POST /api/messages
ja esta pronta para receber mensagens do capturador.
