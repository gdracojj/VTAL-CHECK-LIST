import json
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

ROSTER_FILE = DATA_DIR / "escala.json"
OUTPUT_FILE = DATA_DIR / "test_messages_1000.json"


def load_roster():
    with open(ROSTER_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [
        x for x in data
        if x.get("plantao") == "diurno_b"
        and x.get("active", True)
    ]


def add_hours(time_str, hours=12):
    hour, minute = map(int, time_str.split(":"))
    total = hour * 60 + minute + hours * 60

    return f"{(total // 60) % 24:02d}:{total % 60:02d}"


def format_time(time_str):
    hour, minute = time_str.split(":")
    return f"{int(hour):02d}h{int(minute):02d}"


def make_message(person, status):
    nome = person["employee"]
    posto = person["post"]
    inicio = person["expected_time"]
    fim = add_hours(inicio)

    if status == "correta":
        nome_msg = nome
        posto_msg = posto
        inicio_msg = format_time(inicio)
        fim_msg = format_time(fim)

    elif status == "horario":
        nome_msg = nome
        posto_msg = posto
        inicio_msg = "08h30"
        fim_msg = "20h30"

    elif status == "nome":
        nome_msg = "COLABORADOR TESTE"
        posto_msg = posto
        inicio_msg = format_time(inicio)
        fim_msg = format_time(fim)

    elif status == "posto":
        nome_msg = nome
        posto_msg = "XX-POSTO-999"
        inicio_msg = format_time(inicio)
        fim_msg = format_time(fim)

    elif status == "inexistente":
        nome_msg = "COLABORADOR INEXISTENTE"
        posto_msg = posto
        inicio_msg = format_time(inicio)
        fim_msg = format_time(fim)

    elif status == "incompleta":
        return (
            f"Empresa: PD7 Tech Ltda\n"
            f"Base V.tal: {posto}"
        )

    return (
        f"Empresa: PD7 Tech Ltda\n"
        f"Base V.tal: {posto_msg}\n"
        f"Assunção de serviço: {nome_msg} assumindo\n"
        f"Assumindo serviço {inicio_msg}-{fim_msg}\n"
        f"Data: {person['date']}"
    )


def main():
    roster = load_roster()

    statuses = [
        "correta",
        "correta",
        "correta",
        "correta",
        "horario",
        "nome",
        "posto",
        "inexistente",
        "incompleta",
    ]

    messages = []

    for i in range(1000):
        person = random.choice(roster)
        status = random.choice(statuses)

        messages.append({
            "id": i + 1,
            "status_teste": status,
            "message": make_message(person, status)
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

    print("========================================")
    print("   TESTE VTAL CCOR - 1000 MENSAGENS")
    print("========================================")
    print(f"Plantão testado: diurno_b")
    print(f"Colaboradores: {len(roster)}")
    print(f"Mensagens geradas: {len(messages)}")
    print(f"Arquivo: {OUTPUT_FILE}")
    print("========================================")


if __name__ == "__main__":
    main()