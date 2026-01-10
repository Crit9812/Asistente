import win32com.client
import speech_recognition as sr
import urllib.request
import pywhatkit
import time
import pyautogui  # <-- ÚNICO IMPORT NUEVO
import os
import unicodedata


speaker = win32com.client.Dispatch("SAPI.SpVoice")

# === Luces (ya tenías esto) ===
ESP_IP = "192.168.1.50"
NUM_STRIPS = 3
esperando_cancion = False


def hablar(texto: str):
    """Pronuncia el texto recibido usando la voz de Windows."""
    speaker.Speak(texto)


def encenderLuces():
    for i in range(NUM_STRIPS):
        url = f"http://{ESP_IP}/power?strip={i}&state=1"
        urllib.request.urlopen(url, timeout=2).read()


def apagarLuces():
    for i in range(NUM_STRIPS):
        url = f"http://{ESP_IP}/power?strip={i}&state=0"
        urllib.request.urlopen(url, timeout=2).read()


# === NUEVO: WhatsApp ===
def mensajeWhatsAPP(numero: str, mensaje: str):
    # Abre WhatsApp Web y envía el mensaje al contacto/numero
    # wait_time: segundos para que cargue WhatsApp Web antes de enviar
    pywhatkit.sendwhatmsg_instantly(numero, mensaje, wait_time=15, tab_close=True, close_time=3)

    # <-- ÚNICA MODIFICACIÓN REAL: presionar Enter para enviarlo
    time.sleep(2)
    pyautogui.press("enter")

    time.sleep(1)


def reproducirCancionSpotify(nombre_cancion: str):
    pywhatkit.playonyt(nombre_cancion)


def normalizarTexto(texto: str) -> str:
    return "".join(
        caracter
        for caracter in unicodedata.normalize("NFD", texto)
        if unicodedata.category(caracter) != "Mn"
    )


def esSolicitudCancion(texto: str) -> bool:
    texto_normalizado = normalizarTexto(texto)
    palabras_clave = ("cancion", "musica")
    verbos = ("quiero", "pon", "ponme", "reproduce", "reproducir", "toca", "escuchar")
    return any(palabra in texto_normalizado for palabra in palabras_clave) and any(
        verbo in texto_normalizado for verbo in verbos
    )


def desicion(texto: str) -> bool:
    """
    Procesa lo escrito y decide si el modo debe continuar.
    Retorna True para seguir, False para salir del modo.
    """
    global esperando_cancion

    if not texto:
        return True

    if not texto.startswith("nova"):
        return True

    texto = texto.replace("nova", "", 1).strip()
    if not texto:
        return True

    if esperando_cancion:
        esperando_cancion = False
        reproducirCancionSpotify(texto)
        hablar(f"Claro aquí está la canción {texto}")
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


def textoAVoz():
    while True:
        text = input("> ").strip().lower()
        if not desicion(text):
            break
        
        


def reconocerVoz():
    r = sr.Recognizer()
    try:
        mic = sr.Microphone()
    except OSError:
        print("No se detectó un micrófono. Conecta uno e intenta de nuevo.")
        return

    with mic as source:
        r.adjust_for_ambient_noise(source, duration=0.8)

        while True:
            print("🎤 Escuchando...")
            audio = r.listen(source)

            try:
                texto = r.recognize_google(audio, language="es-MX").strip().lower()
                print(f"📝 Tú dijiste: {texto}")

                if not desicion(texto):
                    break

            except sr.UnknownValueError:
                print("No entendí lo que dijiste. Intenta de nuevo.")
            except sr.RequestError as e:
                print("Error con el servicio de reconocimiento (¿internet?).")
                print(f"Detalle: {e}")
                break

def apagarComputadora():
    os.system("shutdown /s /t 0")



reconocerVoz()
