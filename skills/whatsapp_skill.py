import threading

from core.state import (
    AssistantState,
    STATE_WAIT_WHATSAPP_CONTACT,
    STATE_WAIT_WHATSAPP_MESSAGE,
    STATE_WAIT_WHATSAPP_CONFIRM,
    STATE_IDLE,
)
from hablar import hablar
from skills.skill_types import SkillResult
from utils.texto import contiene_frase, extraer_regex, normalizar_texto
from whatsapp import mensajeWhatsAPP


CONTACTOS_WHATSAPP = {
    "octavio": "+525615824330",
    "mama": "+520000000000",
    "trabajo": "+520000000001",
}


def match(comando: str, estado: AssistantState) -> bool:
    if estado.current_state in (
        STATE_WAIT_WHATSAPP_CONTACT,
        STATE_WAIT_WHATSAPP_MESSAGE,
        STATE_WAIT_WHATSAPP_CONFIRM,
    ):
        return True

    return contiene_frase(
        comando,
        (
            "manda un mensaje por whatsapp",
            "manda un mensaje",
            "manda mensaje por whatsapp",
            "manda mensaje",
            "manda whatsapp",
            "envia mensaje por whatsapp",
            "envia un mensaje",
            "envía un mensaje",
            "manda a",
        ),
    )


def _obtener_contacto(comando: str) -> str:
    comando_normalizado = normalizar_texto(comando)
    for contacto in CONTACTOS_WHATSAPP:
        if contacto in comando_normalizado:
            return contacto
    return ""


def _confirmado(comando: str, estado: AssistantState) -> bool:
    comando_normalizado = normalizar_texto(comando)
    if "no" in comando_normalizado:
        return False
    return contiene_frase(comando_normalizado, ("si", "sí", "confirmo", "adelante"))


def handle(comando: str, estado: AssistantState) -> SkillResult:
    def enviar_en_segundo_plano(numero: str, mensaje: str):
        threading.Thread(
            target=_enviar_y_confirmar,
            args=(numero, mensaje),
            daemon=True,
        ).start()

    def _enviar_y_confirmar(numero: str, mensaje: str):
        mensajeWhatsAPP(numero, mensaje)
        hablar("Mensaje enviado.")

    if estado.safe_mode:
        return SkillResult(True, "Modo seguro activo: no puedo enviar mensajes.", detected_intent="whatsapp")

    if contiene_frase(comando, ("cambia contacto",)):
        estado.current_state = STATE_WAIT_WHATSAPP_CONTACT
        return SkillResult(True, "¿A quién quieres enviar el mensaje?", detected_intent="whatsapp")

    if estado.current_state == STATE_WAIT_WHATSAPP_CONTACT:
        contacto = _obtener_contacto(comando)
        if not contacto:
            return SkillResult(True, "No encontré ese contacto. Di un contacto permitido.", detected_intent="whatsapp")
        estado.memory["last_contact"] = contacto
        estado.current_state = STATE_WAIT_WHATSAPP_MESSAGE
        return SkillResult(True, f"¿Qué mensaje quieres enviar a {contacto}?", detected_intent="whatsapp")

    if estado.current_state == STATE_WAIT_WHATSAPP_MESSAGE:
        estado.memory["last_message"] = comando
        estado.current_state = STATE_WAIT_WHATSAPP_CONFIRM
        if estado.silent_mode:
            return SkillResult(True, "Listo, tengo el mensaje. ¿Confirmas el envío?", detected_intent="whatsapp")
        return SkillResult(True, f"Vas a enviar: {comando}. ¿Confirmas el envío?", detected_intent="whatsapp")

    if estado.current_state == STATE_WAIT_WHATSAPP_CONFIRM:
        if _confirmado(comando, estado):
            numero = CONTACTOS_WHATSAPP.get(estado.memory.get("last_contact", ""))
            mensaje = estado.memory.get("last_message", "")
            if numero and mensaje:
                enviar_en_segundo_plano(numero, mensaje)
                estado.set_last_action("whatsapp_enviar", {
                    "contacto": estado.memory.get("last_contact", ""),
                    "mensaje": mensaje,
                })
                estado.current_state = STATE_IDLE
                return SkillResult(True, "Enviando mensaje...", detected_intent="whatsapp")
            estado.current_state = STATE_IDLE
            return SkillResult(True, "No pude enviar el mensaje. Intenta de nuevo.", detected_intent="whatsapp")

        estado.current_state = STATE_IDLE
        return SkillResult(True, "De acuerdo, cancelé el envío.", detected_intent="whatsapp")

    match_directo = extraer_regex(r"manda\s+a\s+([\w\s]+)[:]?\s+(.+)", comando)
    if match_directo:
        contacto = _obtener_contacto(match_directo.group(1))
        mensaje = match_directo.group(2).strip()
        if not contacto:
            return SkillResult(True, "Solo puedo enviar a contactos permitidos. Di un nombre válido.", detected_intent="whatsapp")
        estado.memory["last_contact"] = contacto
        estado.memory["last_message"] = mensaje
        estado.current_state = STATE_WAIT_WHATSAPP_CONFIRM
        resumen = "Listo, tengo el mensaje. ¿Confirmas el envío?" if estado.silent_mode else f"Vas a enviar: {mensaje}. ¿Confirmas el envío?"
        return SkillResult(True, resumen, detected_intent="whatsapp")

    estado.current_state = STATE_WAIT_WHATSAPP_CONTACT
    return SkillResult(True, "¿A quién quieres enviar el mensaje?", detected_intent="whatsapp")
