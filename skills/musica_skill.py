from musica import (
    esSolicitudCancion,
    esSolicitudPausa,
    esSolicitudReanudar,
    pausarMusica,
    reanudarMusica,
    reproducirCancionSpotify,
)
from core.state import AssistantState, STATE_WAIT_SONG, STATE_IDLE
from skills.skill_types import SkillResult
from utils.texto import contiene_frase, extraer_regex


def match(comando: str, estado: AssistantState) -> bool:
    if estado.current_state == STATE_WAIT_SONG:
        return True

    return (
        esSolicitudPausa(comando)
        or esSolicitudReanudar(comando)
        or esSolicitudCancion(comando)
        or contiene_frase(
            comando,
            (
                "pon musica",
                "reproduce musica",
                "quiero escuchar",
                "pon la misma cancion",
                "pon la misma canción",
                "repite la cancion",
                "repite la canción",
            ),
        )
        or extraer_regex(r"(pon|reproduce)\s+(.+)", comando) is not None
    )


def handle(comando: str, estado: AssistantState) -> SkillResult:
    if estado.current_state == STATE_WAIT_SONG:
        estado.current_state = STATE_IDLE
        estado.memory["last_song"] = comando
        reproducirCancionSpotify(comando)
        estado.set_last_action("musica_reproducir", {"cancion": comando})
        return SkillResult(True, f"Claro aquí está la canción {comando}", detected_intent="musica")

    if esSolicitudPausa(comando):
        pausarMusica()
        estado.set_last_action("musica_pausar")
        return SkillResult(True, "Pausando la música", detected_intent="musica")

    if esSolicitudReanudar(comando):
        reanudarMusica()
        estado.set_last_action("musica_reanudar")
        return SkillResult(True, "Reanudando la música", detected_intent="musica")

    if contiene_frase(
        comando,
        (
            "pon la misma cancion",
            "pon la misma canción",
            "repite la cancion",
            "repite la canción",
        ),
    ):
        cancion = estado.memory.get("last_song", "")
        if not cancion:
            return SkillResult(True, "No tengo una canción anterior para repetir.", detected_intent="musica")
        reproducirCancionSpotify(cancion)
        estado.set_last_action("musica_reproducir", {"cancion": cancion})
        return SkillResult(True, f"Reproduciendo la misma canción: {cancion}", detected_intent="musica")

    match_cancion = extraer_regex(r"(pon|reproduce)\s+(.+)", comando)
    if match_cancion:
        cancion = match_cancion.group(2).strip()
        reproducirCancionSpotify(cancion)
        estado.memory["last_song"] = cancion
        estado.set_last_action("musica_reproducir", {"cancion": cancion})
        return SkillResult(True, f"Reproduciendo {cancion}", detected_intent="musica")

    estado.current_state = STATE_WAIT_SONG
    return SkillResult(True, "¿Qué canción quieres?", detected_intent="musica")
