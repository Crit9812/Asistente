import pyautogui
import pywhatkit
import unicodedata
import webbrowser


ventana_youtube_abierta = False


def reproducirCancionSpotify(nombre_cancion: str):
    global ventana_youtube_abierta
    video_url = pywhatkit.playonyt(nombre_cancion, open_video=False)
    if not ventana_youtube_abierta:
        webbrowser.open(video_url, new=0)
        ventana_youtube_abierta = True
        return

    pyautogui.hotkey("ctrl", "l")
    pyautogui.typewrite(video_url)
    pyautogui.press("enter")


def pausarMusica():
    pyautogui.press("k")


def reanudarMusica():
    pyautogui.press("k")


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


def esSolicitudPausa(texto: str) -> bool:
    texto_normalizado = normalizarTexto(texto)
    palabras_clave = ("cancion", "musica")
    verbos = ("pausa", "pausar", "para", "parar", "deten", "detener")
    return (any(verbo in texto_normalizado for verbo in verbos) and any(
        palabra in texto_normalizado for palabra in palabras_clave
    )) or "pausa" in texto_normalizado


def esSolicitudReanudar(texto: str) -> bool:
    texto_normalizado = normalizarTexto(texto)
    palabras_clave = ("cancion", "musica")
    verbos = (
        "continua",
        "continuar",
        "reanuda",
        "reanudar",
        "sigue",
        "seguir",
        "reproduce",
        "reproducir",
    )
    return (any(verbo in texto_normalizado for verbo in verbos) and any(
        palabra in texto_normalizado for palabra in palabras_clave
    )) or "continue" in texto_normalizado
