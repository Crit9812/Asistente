import time

import pyautogui
import pywhatkit


def mensajeWhatsAPP(numero: str, mensaje: str) -> bool:
    # Abre WhatsApp Web y envía el mensaje al contacto/numero
    # wait_time: segundos para que cargue WhatsApp Web antes de enviar
    pywhatkit.sendwhatmsg_instantly(numero, mensaje, wait_time=15, tab_close=True, close_time=3)

    # <-- ÚNICA MODIFICACIÓN REAL: presionar Enter para enviarlo
    time.sleep(2)
    if not _asegurar_ventana_whatsapp():
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
