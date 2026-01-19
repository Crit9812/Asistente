import win32com.client


speaker = win32com.client.Dispatch("SAPI.SpVoice")


def hablar(texto: str):
    """Pronuncia el texto recibido usando la voz de Windows."""
    speaker.Speak(texto)
