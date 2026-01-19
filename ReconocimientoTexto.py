from escuchar import reconocerVoz
from hablar import hablar
from luces import apagarLuces, encenderLuces
from musica import (
    esSolicitudCancion,
    esSolicitudPausa,
    esSolicitudReanudar,
    pausarMusica,
    reanudarMusica,
    reproducirCancionSpotify,
)
from sistema import apagarComputadora
from whatsapp import mensajeWhatsAPP


esperando_cancion = False


def desicion(texto: str) -> bool:
    """
    Procesa lo escrito y decide si el modo debe continuar.
    Retorna True para seguir, False para salir del modo.
    """
    global esperando_cancion

    if esperando_cancion:
        esperando_cancion = False
        reproducirCancionSpotify(texto)
        hablar(f"Claro aquí está la canción {texto}")
        return True

    if not texto:
        return True

    if not texto.startswith("luna"):
        return True

    texto = texto.replace("luna", "", 1).strip()
    if not texto:
        return True

    if texto == "salir":
        hablar("Hasta luego")
        return False

    elif texto == "ayudame":
        hablar("¿En qué puedo ayudarte?")

    elif texto == "apaga las luces":
        apagarLuces()

    elif texto == "enciende las luces":
        encenderLuces()

    elif esSolicitudPausa(texto):
        hablar("Pausando la música")
        pausarMusica()

    elif esSolicitudReanudar(texto):
        hablar("Reanudando la música")
        reanudarMusica()

    elif esSolicitudCancion(texto):
        hablar("Si cual quieres")
        esperando_cancion = True

    elif texto == "apaga la computadora":
        hablar("Apagando la computadora")
        apagarComputadora()

    elif texto.startswith("manda un mensaje por whatsapp"):
        mensaje = texto.replace("dile a octavio en whatsapp que", "", 1).strip()
        if mensaje:
            mensajeWhatsAPP("+525615824330", mensaje)

    else:
        hablar(texto)

    return True


reconocerVoz(desicion)
