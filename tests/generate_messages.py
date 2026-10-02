import json
import random
from datetime import date, timedelta
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

ROSTER_FILE = DATA_DIR / "escala.json"
OUTPUT_FILE = DATA_DIR / "test_messages_1000.json"


def load_roster():
    with open(ROSTER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def add_hours(time_str, hours=12):
    hour, minute = map(int, time_str.split(":"))
    total = hour * 60 + minute + hours * 60

    return f"{(total // 60) % 24:02d}:{total % 60:02d}"


def format_time(time_str):
    hour, minute = time_str.split(":")
    return f"{int(hour):02d}h{int(minute):02d}"


def shift_for_date(item, message_date):
    parity = "pares" if message_date.day % 2 == 0 else "impares"

    return (
        item.get("dias") == parity
        and item.get("active", True)
    )


def choose_person(roster, plantao, message_date):
    candidates = [
        item
        for item in roster
        if item.get("plantao") == plantao
        and shift_for_date(item, message_date)
    ]

    if not candidates:
        return None

    return random.choice(candidates)


def make_message(person, status, message_date):
    nome = person["employee"]
    posto = person["post"]
    inicio = person["expected_time"]
    fim = add_hours(inicio)

    inicio_formatado = format_time(inicio)
    fim_formatado = format_time(fim)

    if status == "correta":
        nome_msg = nome
        posto_msg = posto
        inicio_msg = inicio_formatado
        fim_msg = fim_formatado

    elif status == "horario":
        nome_msg = nome
        posto_msg = posto

        if inicio == "06:00":
            inicio_msg = "06h30"
            fim_msg = "18h30"
        else:
            inicio_msg = "18h30"
            fim_msg = "06h30"

    elif status == "nome":
        nome_msg = "Colaborador Teste"
        posto_msg = posto
        inicio_msg = inicio_formatado
        fim_msg = fim_formatado

    elif status == "posto":
        nome_msg = nome
        posto_msg = "OR-XX-OPS-999"
        inicio_msg = inicio_formatado
        fim_msg = fim_formatado

    elif status == "inexistente":
        nome_msg = "Colaborador Inexistente"
        posto_msg = posto
        inicio_msg = inicio_formatado
        fim_msg = fim_formatado

    elif status == "incompleta":
        return (
            f"Orion Telecom\n"
            f"Posto: {posto}\n"
            f"Data: {message_date.isoformat()}"
        )

    return (
        f"Orion Telecom\n"
        f"Posto: {posto_msg}\n"
        f"Data: {message_date.strftime('%d/%m/%Y')}\n"
        f"Assunção de serviço: {nome_msg} assumindo\n"
        f"Assumindo serviço {inicio_msg} às {fim_msg}"
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

    plantao_options = [
        "diurno_a",
        "noturno_a",
        "diurno_b",
        "noturno_b",
    ]

    start_date = date(2026, 9, 1)

    messages = []

    for i in range(1000):
        message_date = start_date + timedelta(days=random.randint(0, 29))
        plantao = random.choice(plantao_options)

        person = choose_person(
            roster,
            plantao,
            message_date,
        )

        if person is None:
            continue

        status = random.choice(statuses)

        message = make_message(
            person,
            status,
            message_date,
        )

        messages.append({
            "id": i + 1,
            "status_teste": status,
            "plantao": plantao,
            "date": message_date.isoformat(),
            "message": message,
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(
            messages,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print("=" * 50)
    print("       CONTROLops - GERADOR DE TESTES")
    print("=" * 50)
    print(f"Mensagens geradas: {len(messages)}")
    print(f"Arquivo: {OUTPUT_FILE}")
    print("=" * 50)


if __name__ == "__main__":
    main()