import json
from pathlib import Path

from core.state import AssistantState
from skills.skill_types import SkillResult
from utils.texto import contiene_frase, extraer_regex, normalizar_texto


DATA_PATH = Path("data/tareas_notas.json")


def _cargar_datos() -> dict:
    if not DATA_PATH.exists():
        return {"tareas": [], "notas": []}
    with DATA_PATH.open("r", encoding="utf-8") as archivo:
        return json.load(archivo)


def _guardar_datos(datos: dict):
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DATA_PATH.open("w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)


def match(comando: str, estado: AssistantState) -> bool:
    return contiene_frase(
        comando,
        (
            "agrega tarea",
            "agrega tarea:",
            "que tareas tengo",
            "qué tareas tengo",
            "marca",
            "guarda nota",
            "guarda nota:",
        ),
    )


def handle(comando: str, estado: AssistantState) -> SkillResult:
    comando_normalizado = normalizar_texto(comando)

    if contiene_frase(comando_normalizado, ("que tareas tengo", "qué tareas tengo")):
        datos = _cargar_datos()
        pendientes = [t["texto"] for t in datos["tareas"] if not t.get("hecha", False)]
        if not pendientes:
            return SkillResult(True, "No tienes tareas pendientes.", detected_intent="tareas")
        return SkillResult(True, "Tareas pendientes: " + ", ".join(pendientes), detected_intent="tareas")

    match_tarea = extraer_regex(r"agrega\s+tarea[:]?\s+(.+)", comando_normalizado)
    if match_tarea:
        texto = match_tarea.group(1).strip()
        datos = _cargar_datos()
        datos["tareas"].append({"texto": texto, "hecha": False})
        _guardar_datos(datos)
        estado.set_last_action("tarea_agregar", {"texto": texto})
        return SkillResult(True, f"Agregué la tarea: {texto}", detected_intent="tareas")

    match_marcar = extraer_regex(r"marca\s+(.+)\s+como\s+hecha", comando_normalizado)
    if match_marcar:
        texto = match_marcar.group(1).strip()
        datos = _cargar_datos()
        encontrada = False
        for tarea in datos["tareas"]:
            if tarea["texto"].lower() == texto:
                tarea["hecha"] = True
                encontrada = True
                break
        if encontrada:
            _guardar_datos(datos)
            estado.set_last_action("tarea_marcar", {"texto": texto})
            return SkillResult(True, f"Listo, marqué {texto} como hecha.", detected_intent="tareas")
        return SkillResult(True, "No encontré esa tarea.", detected_intent="tareas")

    match_nota = extraer_regex(r"guarda\s+nota[:]?\s+(.+)", comando_normalizado)
    if match_nota:
        texto = match_nota.group(1).strip()
        datos = _cargar_datos()
        datos["notas"].append({"texto": texto})
        _guardar_datos(datos)
        estado.set_last_action("nota_guardar", {"texto": texto})
        return SkillResult(True, "Nota guardada.", detected_intent="notas")

    return SkillResult(False)
