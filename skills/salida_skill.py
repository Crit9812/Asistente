from core.state import AssistantState
from skills.skill_types import SkillResult
from utils.texto import contiene_frase


def match(comando: str, estado: AssistantState) -> bool:
    return contiene_frase(comando, ("salir", "adios", "adiós"))


def handle(comando: str, estado: AssistantState) -> SkillResult:
    return SkillResult(True, "Hasta luego", end_session=True, detected_intent="salir")
