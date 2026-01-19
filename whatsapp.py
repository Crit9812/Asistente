import pyautogui
import pywhatkit
import time


def mensajeWhatsAPP(numero: str, mensaje: str):
    # Abre WhatsApp Web y envía el mensaje al contacto/numero
    # wait_time: segundos para que cargue WhatsApp Web antes de enviar
    pywhatkit.sendwhatmsg_instantly(numero, mensaje, wait_time=15, tab_close=True, close_time=3)

    # <-- ÚNICA MODIFICACIÓN REAL: presionar Enter para enviarlo
    time.sleep(2)
    pyautogui.press("enter")

    time.sleep(1)
