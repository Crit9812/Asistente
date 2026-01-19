import random
import unicodedata

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


ESTADO_NINGUNO = "ninguno"
ESTADO_ESPERANDO_CANCION = "esperando_cancion"
ESTADO_ESPERANDO_CONTACTO_WHATSAPP = "esperando_contacto_whatsapp"
ESTADO_ESPERANDO_MENSAJE_WHATSAPP = "esperando_mensaje_whatsapp"
ESTADO_ESPERANDO_CONFIRMACION_APAGAR_PC = "esperando_confirmacion_apagar_pc"
ESTADO_ESPERANDO_CONFIRMACION_WHATSAPP = "esperando_confirmacion_whatsapp"


estado_actual = ESTADO_NINGUNO
modo_silencioso = False
modo_debug = False
ultima_cancion = ""
ultimo_contacto = ""
ultimo_mensaje = ""
ultima_accion = ""
ultima_respuesta = ""

CONTACTOS_WHATSAPP = {
    "octavio": "+525615824330",
    "mama": "+520000000000",
    "trabajo": "+520000000001",
}

respuestas_hola = [
    "Hola, ¿cómo estás?",
    "Hola, ¿en qué te ayudo?",
    "¡Hola! ¿Qué tal?",
    "Hola, aquí estoy.",
    "Hola, dime.",
    "¡Hola! ¿Cómo va todo?",
    "Hola, ¿qué necesitas?",
    "Hola, listo para ayudar.",
    "Hola, ¿qué tal tu día?",
    "¡Hola! Te escucho.",
    "Hola, ¿qué quieres hacer?",
    "Hola, ¿en qué te puedo apoyar?",
    "Hola, aquí estoy para ayudarte.",
    "Hola, ¿qué onda?",
    "¡Hola! ¿Cómo te sientes?",
    "Hola, ¿qué pasa?",
    "Hola, ¿todo bien?",
    "¡Hola! ¿Qué hay de nuevo?",
    "Hola, ¿qué cuentas?",
    "Hola, ¿cómo te va?",
    "¡Hola! ¿Qué necesitas hoy?",
    "Hola, listo.",
    "Hola, ¿con qué empezamos?",
    "Hola, ¿cómo puedo ayudarte?",
    "Hola, ¿alguna canción?",
    "Hola, ¿quieres música?",
    "¡Hola! Aquí estoy.",
    "Hola, ¿qué se ofrece?",
    "Hola, ¿qué hacemos?",
    "Hola, ¿qué tal todo?",
]


def normalizar_texto(texto: str) -> str:
    texto = texto.strip().lower()
    return "".join(
        caracter
        for caracter in unicodedata.normalize("NFD", texto)
        if unicodedata.category(caracter) != "Mn"
    )


def contiene_frase(texto: str, frases: tuple[str, ...]) -> bool:
    return any(frase in texto for frase in frases)


def registrar_log(mensaje: str):
    if modo_debug:
        print(f"[DEBUG] {mensaje}")


def decir(texto: str):
    global ultima_respuesta
    ultima_respuesta = texto
    hablar(texto)


def es_confirmacion(texto: str) -> bool:
    texto_normalizado = normalizar_texto(texto)
    if "no" in texto_normalizado:
        return False
    return contiene_frase(texto_normalizado, ("si", "sí", "confirmo", "adelante"))


def obtener_contacto_permitido(texto: str) -> str:
    texto_normalizado = normalizar_texto(texto)
    for contacto in CONTACTOS_WHATSAPP:
        if contacto in texto_normalizado:
            return contacto
    return ""


def listar_comandos():
    comandos = [
        "apaga/enciende las luces",
        "pon música / reproduce música",
        "pausa / reanuda",
        "manda mensaje por whatsapp",
        "apaga la computadora",
        "salir",
        "modo silencioso / modo público",
    ]
    decir("Puedo hacer lo siguiente: " + ", ".join(comandos))


def manejar_estado(texto: str) -> bool:
    global estado_actual
    global ultima_cancion
    global ultimo_contacto
    global ultimo_mensaje
    global ultima_accion

    if estado_actual == ESTADO_ESPERANDO_CANCION:
        estado_actual = ESTADO_NINGUNO
        ultima_cancion = texto
        reproducirCancionSpotify(texto)
        decir(f"Claro aquí está la canción {texto}")
        ultima_accion = "reproducir_cancion"
        return True

    if estado_actual == ESTADO_ESPERANDO_CONTACTO_WHATSAPP:
        contacto = obtener_contacto_permitido(texto)
        if not contacto:
            decir("No encontré ese contacto. Di el nombre de un contacto permitido.")
            return True
        ultimo_contacto = contacto
        estado_actual = ESTADO_ESPERANDO_MENSAJE_WHATSAPP
        decir(f"¿Qué mensaje quieres enviar a {contacto}?")
        return True

    if estado_actual == ESTADO_ESPERANDO_MENSAJE_WHATSAPP:
        ultimo_mensaje = texto
        estado_actual = ESTADO_ESPERANDO_CONFIRMACION_WHATSAPP
        if modo_silencioso:
            decir("Listo, tengo el mensaje. ¿Confirmas el envío?")
        else:
            decir(f"Vas a enviar: {texto}. ¿Confirmas el envío?")
        return True

    if estado_actual == ESTADO_ESPERANDO_CONFIRMACION_WHATSAPP:
        if es_confirmacion(texto):
            numero = CONTACTOS_WHATSAPP.get(ultimo_contacto)
            if numero and ultimo_mensaje:
                mensajeWhatsAPP(numero, ultimo_mensaje)
                decir("Mensaje enviado.")
                ultima_accion = "enviar_whatsapp"
            else:
                decir("No pude enviar el mensaje. Intenta de nuevo.")
        else:
            decir("De acuerdo, cancelé el envío.")
        estado_actual = ESTADO_NINGUNO
        return True

    if estado_actual == ESTADO_ESPERANDO_CONFIRMACION_APAGAR_PC:
        if es_confirmacion(texto):
            decir("Apagando la computadora")
            apagarComputadora()
            ultima_accion = "apagar_computadora"
        else:
            decir("Entendido, cancelé el apagado.")
        estado_actual = ESTADO_NINGUNO
        return True

    return False


def desicion(texto: str) -> bool:
    """
    Procesa lo escrito y decide si el modo debe continuar.
    Retorna True para seguir, False para salir del modo.
    """
    global estado_actual
    global modo_silencioso
    global modo_debug
    global ultima_cancion
    global ultimo_contacto
    global ultima_accion
    global ultima_respuesta

    registrar_log(f"Texto recibido: {texto}")

    if estado_actual != ESTADO_NINGUNO:
        return manejar_estado(texto)

    if not texto:
        return True

    texto_normalizado = normalizar_texto(texto)

    if not texto_normalizado.startswith("luna"):
        return True

    comando = texto_normalizado.replace("luna", "", 1).strip()
    if not comando:
        return True

    registrar_log(f"Comando normalizado: {comando}")

    def accion_salir() -> bool:
        decir("Hasta luego")
        return False

    def accion_hola() -> bool:
        decir(random.choice(respuestas_hola))
        return True

    def accion_ayuda() -> bool:
        listar_comandos()
        return True

    def accion_apagar_luces() -> bool:
        global ultima_accion
        apagarLuces()
        decir("Apagando las luces")
        ultima_accion = "apagar_luces"
        registrar_log("Acción: apagar luces")
        return True

    def accion_encender_luces() -> bool:
        global ultima_accion
        encenderLuces()
        decir("Encendiendo las luces")
        ultima_accion = "encender_luces"
        registrar_log("Acción: encender luces")
        return True

    def accion_pausa() -> bool:
        global ultima_accion
        decir("Pausando la música")
        pausarMusica()
        ultima_accion = "pausar_musica"
        return True

    def accion_reanudar() -> bool:
        global ultima_accion
        decir("Reanudando la música")
        reanudarMusica()
        ultima_accion = "reanudar_musica"
        return True

    def accion_pedir_cancion() -> bool:
        global estado_actual
        decir("¿Qué canción quieres?")
        estado_actual = ESTADO_ESPERANDO_CANCION
        return True

    def accion_repetir_cancion() -> bool:
        global ultima_accion
        if ultima_cancion:
            reproducirCancionSpotify(ultima_cancion)
            decir(f"Reproduciendo la misma canción: {ultima_cancion}")
            ultima_accion = "reproducir_cancion"
        else:
            decir("No tengo una canción anterior para repetir.")
        return True

    def accion_apagar_computadora() -> bool:
        global estado_actual
        estado_actual = ESTADO_ESPERANDO_CONFIRMACION_APAGAR_PC
        decir("¿Seguro? di 'sí' para confirmar")
        return True

    def accion_whatsapp() -> bool:
        global estado_actual
        estado_actual = ESTADO_ESPERANDO_CONTACTO_WHATSAPP
        decir("¿A quién quieres enviar el mensaje?")
        return True

    def accion_repetir_respuesta() -> bool:
        if ultima_respuesta:
            hablar(ultima_respuesta)
        else:
            decir("No tengo nada que repetir.")
        return True

    def accion_modo_silencioso() -> bool:
        global modo_silencioso
        modo_silencioso = True
        decir("Modo silencioso activado.")
        return True

    def accion_modo_publico() -> bool:
        global modo_silencioso
        modo_silencioso = False
        decir("Modo público activado.")
        return True

    def accion_modo_debug() -> bool:
        global modo_debug
        modo_debug = True
        decir("Modo debug activado.")
        return True

    def accion_modo_normal() -> bool:
        global modo_debug
        modo_debug = False
        decir("Modo debug desactivado.")
        return True

    def accion_repetir_luces() -> bool:
        if ultima_accion == "encender_luces":
            encenderLuces()
            decir("Volviendo a encender las luces")
        elif ultima_accion == "apagar_luces":
            apagarLuces()
            decir("Volviendo a apagar las luces")
        else:
            decir("No tengo una acción de luces para repetir.")
        return True

    comandos = [
        (lambda: comando == "salir", accion_salir),
        (lambda: comando in ("hola", "hoa"), accion_hola),
        (
            lambda: contiene_frase(
                comando, ("ayuda", "ayudame", "que puedes hacer")
            ),
            accion_ayuda,
        ),
        (
            lambda: contiene_frase(
                comando, ("apaga la luz", "apaga las luces", "apaga luces", "apagar luces")
            ),
            accion_apagar_luces,
        ),
        (
            lambda: contiene_frase(
                comando,
                (
                    "enciende la luz",
                    "enciende las luces",
                    "enciende luces",
                    "encender luces",
                ),
            ),
            accion_encender_luces,
        ),
        (lambda: esSolicitudPausa(comando), accion_pausa),
        (lambda: esSolicitudReanudar(comando), accion_reanudar),
        (
            lambda: esSolicitudCancion(comando)
            or contiene_frase(
                comando,
                (
                    "pon musica",
                    "reproduce musica",
                    "quiero escuchar",
                    "pon musica",
                ),
            ),
            accion_pedir_cancion,
        ),
        (
            lambda: contiene_frase(
                comando,
                (
                    "pon la misma cancion",
                    "pon la misma canción",
                    "repite la cancion",
                    "repite la canción",
                ),
            ),
            accion_repetir_cancion,
        ),
        (
            lambda: contiene_frase(
                comando,
                (
                    "manda un mensaje por whatsapp",
                    "manda mensaje por whatsapp",
                    "manda whatsapp",
                    "envia mensaje por whatsapp",
                ),
            ),
            accion_whatsapp,
        ),
        (
            lambda: contiene_frase(
                comando, ("apaga la computadora", "apagar la computadora")
            ),
            accion_apagar_computadora,
        ),
        (
            lambda: contiene_frase(
                comando, ("repite", "repitelo", "repítelo")
            ),
            accion_repetir_respuesta,
        ),
        (
            lambda: contiene_frase(
                comando, ("vuelve a encenderlas", "vuelve a apagarlas")
            ),
            accion_repetir_luces,
        ),
        (
            lambda: contiene_frase(comando, ("modo silencioso",)),
            accion_modo_silencioso,
        ),
        (
            lambda: contiene_frase(comando, ("modo publico", "modo público")),
            accion_modo_publico,
        ),
        (lambda: contiene_frase(comando, ("modo debug",)), accion_modo_debug),
        (lambda: contiene_frase(comando, ("modo normal",)), accion_modo_normal),
    ]

    for condicion, accion in comandos:
        if condicion():
            return accion()

    decir("No entendí. ¿Quieres luces, música o mensajes?")
    return True


reconocerVoz(desicion)
