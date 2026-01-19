from datetime import datetime

from core.state import AssistantState
from skills.skill_types import SkillResult
from utils.texto import contiene_frase


def match(comando: str, estado: AssistantState) -> bool:
    return contiene_frase(comando, ("que hora es", "qué hora es", "dame la hora", "hora"))


def handle(comando: str, estado: AssistantState) -> SkillResult:
    hora_actual = datetime.now().strftime("%H:%M")
    return SkillResult(True, f"Son las {hora_actual}.", detected_intent="hora")
