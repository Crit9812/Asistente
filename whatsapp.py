import time

import pyautogui
import pywhatkit


def mensajeWhatsAPP(numero: str, mensaje: str):
    # Abre WhatsApp Web y envía el mensaje al contacto/numero
    # wait_time: segundos para que cargue WhatsApp Web antes de enviar
    pywhatkit.sendwhatmsg_instantly(numero, mensaje, wait_time=15, tab_close=True, close_time=3)

    # <-- ÚNICA MODIFICACIÓN REAL: presionar Enter para enviarlo
    time.sleep(2)
    _activar_ventana_whatsapp(reintentos=10, pausa=0.4)
    pyautogui.press("enter")

    time.sleep(1)


def _activar_ventana_whatsapp(reintentos: int = 5, pausa: float = 0.3) -> bool:
    try:
        ventanas = pyautogui.getWindowsWithTitle("WhatsApp")
    except AttributeError:
        return False

    for _ in range(reintentos):
        for ventana in ventanas:
            try:
                ventana.activate()
                time.sleep(pausa)
                return True
            except Exception:
                continue
        time.sleep(pausa)

    return False
