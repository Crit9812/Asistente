import json
from datetime import datetime, timedelta
from pathlib import Path

from core.state import AssistantState, STATE_WAIT_REMINDER_TIME, STATE_IDLE
from skills.skill_types import SkillResult
from utils.texto import contiene_frase, extraer_regex, normalizar_texto


DATA_PATH = Path("data/recordatorios.json")


def _cargar_recordatorios() -> list[dict]:
    if not DATA_PATH.exists():
        return []
    with DATA_PATH.open("r", encoding="utf-8") as archivo:
        return json.load(archivo)


def _guardar_recordatorios(recordatorios: list[dict]):
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DATA_PATH.open("w", encoding="utf-8") as archivo:
        json.dump(recordatorios, archivo, ensure_ascii=False, indent=2)


def _parsear_fecha(comando: str) -> datetime | None:
    comando_normalizado = normalizar_texto(comando)
    match_minutos = extraer_regex(r"en\s+(\d+)\s+minutos", comando_normalizado)
    if match_minutos:
        minutos = int(match_minutos.group(1))
        return datetime.now() + timedelta(minutes=minutos)

    match_horas = extraer_regex(r"en\s+(\d+)\s+horas", comando_normalizado)
    if match_horas:
        horas = int(match_horas.group(1))
        return datetime.now() + timedelta(hours=horas)

    match_manana = extraer_regex(r"manana\s+a\s+las\s+(\d{1,2})(?::(\d{2}))?", comando_normalizado)
    if match_manana:
        hora = int(match_manana.group(1))
        minuto = int(match_manana.group(2) or 0)
        ahora = datetime.now()
        objetivo = ahora.replace(hour=hora, minute=minuto, second=0, microsecond=0) + timedelta(days=1)
        return objetivo

    match_hoy = extraer_regex(r"a\s+las\s+(\d{1,2})(?::(\d{2}))?", comando_normalizado)
    if match_hoy:
        hora = int(match_hoy.group(1))
        minuto = int(match_hoy.group(2) or 0)
        ahora = datetime.now()
        objetivo = ahora.replace(hour=hora, minute=minuto, second=0, microsecond=0)
        if objetivo < ahora:
            objetivo = objetivo + timedelta(days=1)
        return objetivo

    return None


def match(comando: str, estado: AssistantState) -> bool:
    if estado.current_state == STATE_WAIT_REMINDER_TIME:
        return True
    return contiene_frase(
        comando,
        (
            "recuerdame",
            "recuérdame",
            "lista recordatorios",
            "cancela recordatorio",
            "cancela recordatorios",
        ),
    ) or contiene_frase(comando, ("pon alarma", "alarma"))


def handle(comando: str, estado: AssistantState) -> SkillResult:
    if estado.current_state == STATE_WAIT_REMINDER_TIME:
        fecha = _parsear_fecha(comando)
        texto = estado.pending.get("reminder_text", "")
        if not fecha or not texto:
            estado.current_state = STATE_IDLE
            estado.pending.pop("reminder_text", None)
            return SkillResult(True, "No entendí el tiempo del recordatorio.", detected_intent="recordatorios")
        recordatorios = _cargar_recordatorios()
        recordatorios.append({"texto": texto, "fecha": fecha.isoformat(), "pendiente": True})
        _guardar_recordatorios(recordatorios)
        estado.current_state = STATE_IDLE
        estado.pending.pop("reminder_text", None)
        estado.set_last_action("recordatorio_crear", {"texto": texto, "fecha": fecha.isoformat()})
        return SkillResult(True, "Listo, recordatorio guardado.", detected_intent="recordatorios")

    comando_normalizado = normalizar_texto(comando)

    if contiene_frase(comando_normalizado, ("lista recordatorios",)):
        recordatorios = _cargar_recordatorios()
        pendientes = [r for r in recordatorios if r.get("pendiente", True)]
        if not pendientes:
            return SkillResult(True, "No tienes recordatorios pendientes.", detected_intent="recordatorios")
        detalles = ", ".join(r["texto"] for r in pendientes)
        return SkillResult(True, f"Tienes estos recordatorios: {detalles}", detected_intent="recordatorios")

    if contiene_frase(comando_normalizado, ("cancela recordatorio", "cancela recordatorios")):
        _guardar_recordatorios([])
        estado.set_last_action("recordatorio_cancelar")
        return SkillResult(True, "Listo, cancelé todos los recordatorios.", detected_intent="recordatorios")

    if contiene_frase(comando_normalizado, ("pon alarma", "alarma")):
        fecha = _parsear_fecha(comando_normalizado)
        if not fecha:
            estado.current_state = STATE_WAIT_REMINDER_TIME
            estado.pending["reminder_text"] = "alarma"
            return SkillResult(True, "¿Para cuándo pongo la alarma?", detected_intent="recordatorios")
        recordatorios = _cargar_recordatorios()
        recordatorios.append({"texto": "alarma", "fecha": fecha.isoformat(), "pendiente": True})
        _guardar_recordatorios(recordatorios)
        estado.set_last_action("recordatorio_crear", {"texto": "alarma", "fecha": fecha.isoformat()})
        return SkillResult(True, "Alarma configurada.", detected_intent="recordatorios")

    match_recordatorio = extraer_regex(r"recuerdame\s+(.+)", comando_normalizado)
    if match_recordatorio:
        texto_recordatorio = match_recordatorio.group(1).strip()
        fecha = _parsear_fecha(comando_normalizado)
        if not fecha:
            estado.current_state = STATE_WAIT_REMINDER_TIME
            estado.pending["reminder_text"] = texto_recordatorio
            return SkillResult(True, "¿Para cuándo quieres el recordatorio?", detected_intent="recordatorios")
        recordatorios = _cargar_recordatorios()
        recordatorios.append({"texto": texto_recordatorio, "fecha": fecha.isoformat(), "pendiente": True})
        _guardar_recordatorios(recordatorios)
        estado.set_last_action("recordatorio_crear", {"texto": texto_recordatorio, "fecha": fecha.isoformat()})
        return SkillResult(True, "Listo, recordatorio guardado.", detected_intent="recordatorios")

    return SkillResult(False)


def obtener_recordatorios_vencidos() -> list[dict]:
    recordatorios = _cargar_recordatorios()
    ahora = datetime.now()
    vencidos = []
    for recordatorio in recordatorios:
        if recordatorio.get("pendiente", True):
            fecha = datetime.fromisoformat(recordatorio["fecha"])
            if fecha <= ahora:
                vencidos.append(recordatorio)
                recordatorio["pendiente"] = False
    if vencidos:
        _guardar_recordatorios(recordatorios)
    return vencidos
