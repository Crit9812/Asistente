from core.state import AssistantState
from skills.skill_types import SkillResult
from utils.texto import contiene_frase, normalizar_texto


def match(comando: str, estado: AssistantState) -> bool:
    return contiene_frase(
        comando,
        (
            "modo silencioso",
            "modo publico",
            "modo público",
            "modo debug",
            "modo normal",
            "modo seguro",
            "modo nino",
            "modo niño",
            "ayuda",
            "ayudame",
            "que puedes hacer",
            "qué puedes hacer",
            "lee el mensaje antes de enviar",
        ),
    )


def handle(comando: str, estado: AssistantState) -> SkillResult:
    comando_normalizado = normalizar_texto(comando)

    if contiene_frase(comando_normalizado, ("ayuda", "ayudame", "que puedes hacer")):
        comandos = [
            "apaga/enciende las luces",
            "pon música / reproduce música",
            "pausa / reanuda",
            "manda mensaje por whatsapp",
            "apaga la computadora",
            "recuérdame / alarma",
            "agrega tarea / notas",
            "hora",
            "repite o deshaz",
            "modo silencioso / modo público",
            "modo seguro / modo niño",
        ]
        return SkillResult(True, "Puedo hacer lo siguiente: " + ", ".join(comandos), detected_intent="ayuda")

    if contiene_frase(comando_normalizado, ("lee el mensaje antes de enviar",)):
        estado.silent_mode = False
        return SkillResult(True, "De acuerdo, leeré el mensaje antes de enviarlo.", detected_intent="modos")

    if contiene_frase(comando_normalizado, ("modo silencioso",)):
        estado.silent_mode = True
        return SkillResult(True, "Modo silencioso activado.", detected_intent="modos")

    if contiene_frase(comando_normalizado, ("modo publico", "modo público")):
        estado.silent_mode = False
        return SkillResult(True, "Modo público activado.", detected_intent="modos")

    if contiene_frase(comando_normalizado, ("modo debug",)):
        estado.debug_mode = True
        return SkillResult(True, "Modo debug activado.", detected_intent="modos")

    if contiene_frase(comando_normalizado, ("modo normal",)):
        estado.debug_mode = False
        estado.safe_mode = False
        return SkillResult(True, "Modo normal activado.", detected_intent="modos")

    if contiene_frase(comando_normalizado, ("modo seguro", "modo nino", "modo niño")):
        estado.safe_mode = True
        return SkillResult(True, "Modo seguro activado.", detected_intent="modos")

    return SkillResult(False)
