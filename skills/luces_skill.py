from luces import apagarLuces, encenderLuces
from utils.texto import contiene_frase
from skills.skill_types import SkillResult
from core.state import AssistantState


def match(comando: str, estado: AssistantState) -> bool:
    return contiene_frase(
        comando,
        (
            "apaga la luz",
            "apaga las luces",
            "apaga luces",
            "apagar luces",
            "enciende la luz",
            "enciende las luces",
            "enciende luces",
            "encender luces",
        ),
    )


def handle(comando: str, estado: AssistantState) -> SkillResult:
    if contiene_frase(comando, ("apaga",)):
        apagarLuces()
        estado.set_last_action("luces_apagar")
        return SkillResult(True, "Apagando las luces", detected_intent="luces")

    encenderLuces()
    estado.set_last_action("luces_encender")
    return SkillResult(True, "Encendiendo las luces", detected_intent="luces")
