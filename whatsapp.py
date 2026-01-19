import time
import webbrowser
from urllib.parse import quote

import pyautogui


def mensajeWhatsAPP(numero: str, mensaje: str) -> bool:
    url = _construir_url_whatsapp(numero, mensaje)
    webbrowser.open(url, new=0)

    inicio = time.time()
    if not _esperar_y_enfocar_whatsapp():
        return False

    if not _esperar_whatsapp_listo(inicio=inicio):
        return False

    pyautogui.press("enter")

    time.sleep(1)
    return True


def _activar_ventana_whatsapp(reintentos: int = 5, pausa: float = 0.3) -> bool:
    try:
        ventanas = pyautogui.getWindowsWithTitle("WhatsApp")
    except AttributeError:
        return False

    for _ in range(reintentos):
        for ventana in ventanas:
            try:
                ventana.activate()
                _enfocar_ventana(ventana, pausa)
                return True
            except Exception:
                continue
        time.sleep(pausa)

    return False


def _enfocar_ventana(ventana, pausa: float):
    try:
        x = ventana.left + (ventana.width // 2)
        y = ventana.top + (ventana.height // 2)
        posicion_actual = pyautogui.position()
        pyautogui.click(x, y)
        time.sleep(pausa)
        pyautogui.moveTo(posicion_actual)
    except Exception:
        time.sleep(pausa)


def _asegurar_ventana_whatsapp() -> bool:
    if _es_ventana_whatsapp_activa():
        return True

    if not _activar_ventana_whatsapp(reintentos=12, pausa=0.35):
        return False

    return _es_ventana_whatsapp_activa()


def _es_ventana_whatsapp_activa() -> bool:
    try:
        titulo = pyautogui.getActiveWindowTitle()
    except AttributeError:
        return False

    if not titulo:
        return False

    return "whatsapp" in titulo.lower()


def _construir_url_whatsapp(numero: str, mensaje: str) -> str:
    mensaje_codificado = quote(mensaje)
    return f"https://web.whatsapp.com/send?phone={numero}&text={mensaje_codificado}"


def _esperar_y_enfocar_whatsapp(timeout: float = 20.0, pausa: float = 0.5) -> bool:
    limite = time.time() + timeout
    while time.time() < limite:
        if _asegurar_ventana_whatsapp():
            return True
        time.sleep(pausa)
    return False


def _esperar_whatsapp_listo(
    inicio: float,
    timeout: float = 20.0,
    pausa: float = 0.5,
    minimo_espera: float = 4.0,
    checks_estables: int = 3,
) -> bool:
    limite = time.time() + timeout
    checks = 0
    while time.time() < limite:
        if not _asegurar_ventana_whatsapp():
            checks = 0
            time.sleep(pausa)
            continue

        if time.time() - inicio < minimo_espera:
            time.sleep(pausa)
            continue

        checks += 1
        if checks >= checks_estables:
            return True

        time.sleep(pausa)

    return False
