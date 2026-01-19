import threading

from core.state import AssistantState
from luces import apagarLuces, encenderLuces
from musica import pausarMusica, reanudarMusica, reproducirCancionSpotify
from skills.skill_types import SkillResult
from utils.texto import contiene_frase


def match(comando: str, estado: AssistantState) -> bool:
    return contiene_frase(
        comando,
        (
            "repite la ultima accion",
            "repite la última acción",
            "repite",
            "repitelo",
            "repítelo",
            "deshaz eso",
        ),
    )


def handle(comando: str, estado: AssistantState) -> SkillResult:
    accion = estado.memory.get("last_action")
    if not accion:
        return SkillResult(True, "No tengo ninguna acción para repetir.", detected_intent="repetir")

    if contiene_frase(comando, ("deshaz", "deshacer")):
        return _deshacer(accion)

    return _repetir(accion)


def _deshacer(accion: dict) -> SkillResult:
    tipo = accion.get("type")
    payload = accion.get("payload", {})

    def reproducir_en_segundo_plano(cancion: str):
        threading.Thread(
            target=reproducirCancionSpotify,
            args=(cancion,),
            daemon=True,
        ).start()

    if tipo == "luces_apagar":
        encenderLuces()
        return SkillResult(True, "Listo, volví a encender las luces.")
    if tipo == "luces_encender":
        apagarLuces()
        return SkillResult(True, "Listo, volví a apagar las luces.")
    if tipo == "musica_pausar":
        reanudarMusica()
        return SkillResult(True, "Reanudé la música.")
    if tipo == "musica_reanudar":
        pausarMusica()
        return SkillResult(True, "Pausé la música.")
    if tipo == "musica_reproducir":
        cancion = payload.get("cancion")
        if cancion:
            reproducir_en_segundo_plano(cancion)
            return SkillResult(True, f"Reproduciendo {cancion}.")
    return SkillResult(True, "No puedo deshacer esa acción.")


def _repetir(accion: dict) -> SkillResult:
    tipo = accion.get("type")
    payload = accion.get("payload", {})

    def reproducir_en_segundo_plano(cancion: str):
        threading.Thread(
            target=reproducirCancionSpotify,
            args=(cancion,),
            daemon=True,
        ).start()

    if tipo == "luces_apagar":
        apagarLuces()
        return SkillResult(True, "Repetí el apagado de luces.")
    if tipo == "luces_encender":
        encenderLuces()
        return SkillResult(True, "Repetí el encendido de luces.")
    if tipo == "musica_pausar":
        pausarMusica()
        return SkillResult(True, "Volví a pausar la música.")
    if tipo == "musica_reanudar":
        reanudarMusica()
        return SkillResult(True, "Volví a reanudar la música.")
    if tipo == "musica_reproducir":
        cancion = payload.get("cancion")
        if cancion:
            reproducir_en_segundo_plano(cancion)
            return SkillResult(True, f"Reproduciendo {cancion}.")
    return SkillResult(True, "No puedo repetir esa acción.")
