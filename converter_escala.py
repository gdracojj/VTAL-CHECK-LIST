import json
from pathlib import Path

ARQUIVO = Path("data/escala.json")

with open(ARQUIVO, "r", encoding="utf-8") as f:
    escala = json.load(f)

for item in escala:

    if item.get("date") == "2026-09-25":
        item["plantao"] = "diurno_a"

    elif item.get("date") == "2026-09-26":
        item["plantao"] = "diurno_b"

with open(ARQUIVO, "w", encoding="utf-8") as f:
    json.dump(
        escala,
        f,
        ensure_ascii=False,
        indent=2
    )

print("Escala convertida com sucesso.")
print("2026-09-25 -> DIURNO A")
print("2026-09-26 -> DIURNO B")