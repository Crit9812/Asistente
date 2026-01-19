import threading
import time

from core.state import AssistantState, STATE_IDLE
from core.telemetry import log_event
from escuchar import reconocerVoz
from hablar import hablar
from skills import (
    hora_skill,
    luces_skill,
    modos_skill,
    musica_skill,
    recordatorios,
    repetir_deshacer,
    salida_skill,
    sistema_skill,
    tareas_notas,
    volumen_skill,
    whatsapp_skill,
)
from utils.texto import contiene_frase, normalizar_texto


estado = AssistantState()

# Comandos disponibles y acciones:
# - "Luna": activa escucha temporal (30s) para comandos sin repetir "Luna".
# - "apaga/enciende las luces": controla luces.
# - "pon música / reproduce música": pide canción o reproduce si se da el título.
# - "pausa / reanuda": controla reproducción.
# - "manda a <contacto>: <mensaje>": prepara WhatsApp y pide confirmación con código.
# - "cambia contacto": reinicia flujo de WhatsApp.
# - "recuérdame <texto> en X minutos/horas/mañana a las HH:MM": crea recordatorio.
# - "pon alarma en X minutos/horas/a las HH:MM": crea alarma.
# - "lista recordatorios / cancela recordatorio": gestiona recordatorios.
# - "agrega tarea: <texto> / qué tareas tengo / marca <tarea> como hecha": tareas.
# - "guarda nota: <texto>": notas rápidas.
# - "qué hora es / dame la hora": dice la hora.
# - "sube/baja volumen <n> / volumen a <n>": ajusta volumen.
# - "repite la última acción / deshaz eso": repite o revierte la acción previa.
# - "modo silencioso / modo público": controla lectura de mensajes.
# - "modo seguro / modo niño": bloquea acciones peligrosas.
# - "código de voz <palabra>": cambia palabra de confirmación.
#   Código actual por defecto: "codigo seguro".
# - "salir": finaliza la sesión.

def decir(texto: str):
    estado.memory["last_response"] = texto
    hablar(texto)


def registrar_debug(mensaje: str):
    if estado.debug_mode:
        print(f"[DEBUG] {mensaje}")


def manejar_recordatorios(stop_event: threading.Event):
    while not stop_event.is_set():
        vencidos = recordatorios.obtener_recordatorios_vencidos()
        for recordatorio in vencidos:
            hablar(f"Recordatorio: {recordatorio['texto']}")
        stop_event.wait(5)


def activar_si_es_necesario(texto_normalizado: str) -> tuple[bool, str]:
    ahora = time.time()
    if (
        estado.is_active
        and estado.current_state == STATE_IDLE
        and (ahora - estado.last_activation_ts) > estado.activation_timeout
    ):
        estado.is_active = False
        if "luna" not in texto_normalizado:
            decir("Me duermo")
            return False, ""

    if "luna" in texto_normalizado:
        estado.is_active = True
        estado.last_activation_ts = ahora
        comando = texto_normalizado.replace("luna", "", 1).strip()
        if not comando:
            decir("Te escucho")
            return False, ""
        return True, comando

    if not estado.is_active:
        return False, ""

    estado.last_activation_ts = ahora
    return True, texto_normalizado


def sugerir_fallback(comando: str) -> str:
    opciones = []
    if contiene_frase(comando, ("luz", "luces")):
        opciones.append("luces")
    if contiene_frase(comando, ("musica", "cancion", "canción")):
        opciones.append("música")
    if contiene_frase(comando, ("whatsapp", "mensaje")):
        opciones.append("whatsapp")

    if not opciones:
        return "No entendí. ¿Quieres luces, música o mensajes?"
    if len(opciones) == 1:
        return f"¿Quieres que haga algo con {opciones[0]}?"
    return "¿Cuál quieres? " + " o ".join(opciones)


def desicion(texto: str) -> bool:
    original = texto.strip()
    if not original:
        return True

    texto_normalizado = normalizar_texto(original)
    activo, comando = activar_si_es_necesario(texto_normalizado)
    if not activo:
        return True

    registrar_debug(f"Comando: {comando}")

    skills = [
        modos_skill,
        repetir_deshacer,
        salida_skill,
        recordatorios,
        tareas_notas,
        hora_skill,
        volumen_skill,
        musica_skill,
        luces_skill,
        whatsapp_skill,
        sistema_skill,
    ]

    resultado = None
    for skill in skills:
        if skill.match(comando, estado):
            resultado = skill.handle(comando, estado)
            if resultado.handled:
                break

    if resultado and resultado.handled:
        if resultado.response:
            decir(resultado.response)
        log_event({
            "texto_original": original,
            "texto_normalizado": comando,
            "intent": resultado.detected_intent,
            "estado": estado.current_state,
            "handled": True,
        })
        return not resultado.end_session

    respuesta = sugerir_fallback(comando)
    decir(respuesta)
    log_event({
        "texto_original": original,
        "texto_normalizado": comando,
        "intent": None,
        "estado": estado.current_state,
        "handled": False,
    })
    return True


stop_event = threading.Event()
thread_recordatorios = threading.Thread(target=manejar_recordatorios, args=(stop_event,), daemon=True)
thread_recordatorios.start()

reconocerVoz(desicion)
