from core.state import AssistantState, STATE_WAIT_PC_CONFIRM, STATE_IDLE
from skills.skill_types import SkillResult
from utils.texto import contiene_frase, normalizar_texto
from sistema import apagarComputadora


def match(comando: str, estado: AssistantState) -> bool:
    if estado.current_state == STATE_WAIT_PC_CONFIRM:
        return True
    return contiene_frase(comando, ("apaga la computadora", "apagar la computadora"))


def _confirmado(comando: str, estado: AssistantState) -> bool:
    comando_normalizado = normalizar_texto(comando)
    if "no" in comando_normalizado:
        return False
    if estado.confirmation_code and estado.confirmation_code not in comando_normalizado:
        return False
    return contiene_frase(comando_normalizado, ("si", "sí", "confirmo", "adelante"))


def handle(comando: str, estado: AssistantState) -> SkillResult:
    if estado.safe_mode:
        return SkillResult(True, "Modo seguro activo: no puedo apagar la computadora.", detected_intent="sistema")

    if estado.current_state == STATE_WAIT_PC_CONFIRM:
        estado.current_state = STATE_IDLE
        if _confirmado(comando, estado):
            apagarComputadora()
            estado.set_last_action("pc_apagar")
            return SkillResult(True, "Apagando la computadora", detected_intent="sistema")
        return SkillResult(True, "Entendido, cancelé el apagado.", detected_intent="sistema")

    estado.current_state = STATE_WAIT_PC_CONFIRM
    return SkillResult(True, "¿Seguro? di 'sí' y el código de voz para confirmar.", detected_intent="sistema")
