import pyautogui

from core.state import AssistantState
from skills.skill_types import SkillResult
from utils.texto import extraer_regex, contiene_frase


def match(comando: str, estado: AssistantState) -> bool:
    return contiene_frase(comando, ("sube volumen", "baja volumen", "volumen"))


def _ajustar_volumen(pasos: int, subir: bool):
    tecla = "volumeup" if subir else "volumedown"
    for _ in range(pasos):
        pyautogui.press(tecla)


def handle(comando: str, estado: AssistantState) -> SkillResult:
    match_subir = extraer_regex(r"sube\s+volumen\s+(\d+)", comando)
    match_bajar = extraer_regex(r"baja\s+volumen\s+(\d+)", comando)
    match_set = extraer_regex(r"volumen\s+a\s+(\d+)", comando)

    if match_set:
        nivel = int(match_set.group(1))
        _ajustar_volumen(50, subir=False)
        pasos = max(0, min(50, nivel))
        _ajustar_volumen(pasos, subir=True)
        estado.set_last_action("volumen_ajustar", {"nivel": nivel})
        return SkillResult(True, f"Ajustando el volumen a {nivel}.", detected_intent="volumen")

    if match_subir:
        pasos = int(match_subir.group(1))
        _ajustar_volumen(pasos, subir=True)
        estado.set_last_action("volumen_subir", {"pasos": pasos})
        return SkillResult(True, f"Subiendo el volumen {pasos}.", detected_intent="volumen")

    if match_bajar:
        pasos = int(match_bajar.group(1))
        _ajustar_volumen(pasos, subir=False)
        estado.set_last_action("volumen_bajar", {"pasos": pasos})
        return SkillResult(True, f"Bajando el volumen {pasos}.", detected_intent="volumen")

    return SkillResult(True, "Dime cuánto quieres subir o bajar el volumen.", detected_intent="volumen")
