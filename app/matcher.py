from datetime import datetime
from rapidfuzz import fuzz
from .parser import norm

def compare(parsed, roster):
    expected = next((x for x in roster if x["post"] == parsed.get("post")), None)
    if not expected:
        return {"status":"DIVERGÊNCIA","reason":"posto não encontrado na escala"}

    incoming = parsed.get("incoming")
    score = fuzz.token_set_ratio(norm(incoming), norm(expected["name"])) if incoming else 0

    if score < 70:
        return {"status":"DIVERGÊNCIA","reason":"colaborador divergente",
                "expected_name":expected["name"],"incoming":incoming,"score":round(score)}

    actual = parsed.get("time")
    if not actual:
        return {"status":"IDENTIFICADA","reason":"colaborador conferido; horário não identificado",
                "expected_name":expected["name"]}

    exp = datetime.strptime(expected["time"], "%H:%M")
    act = datetime.strptime(actual, "%H:%M")
    delta = int((act-exp).total_seconds()/60)

    if delta == 0:
        status, reason = "REGULAR", "horário conforme escala"
    elif delta < 0:
        status, reason = "ADIANTADO", f"{abs(delta)} min antes do horário"
    else:
        status, reason = "ATRASADO", f"{delta} min após o horário"

    return {"status":status,"reason":reason,"expected_name":expected["name"],
            "incoming":incoming,"expected_time":expected["time"],"actual_time":actual,
            "delta_minutes":delta,"score":round(score)}

def dashboard(messages, roster):
    results=[]
    used=set()
    for msg in messages:
        parsed=msg["parsed"]
        result=compare(parsed, roster)
        result.update({"post":parsed.get("post"),"date":parsed.get("date"),"raw":parsed.get("raw")})
        results.append(result)
        if parsed.get("post"):
            used.add(parsed["post"])

    for item in roster:
        if item["post"] not in used:
            results.append({"status":"SEM ASSUNÇÃO","post":item["post"],
                            "expected_name":item["name"],"expected_time":item["time"],
                            "reason":"nenhuma mensagem reconhecida para o posto","raw":None})

    counts={}
    for r in results:
        counts[r["status"]]=counts.get(r["status"],0)+1
    return results, counts
