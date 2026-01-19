import speech_recognition as sr


def textoAVoz(callback):
    while True:
        text = input("> ").strip().lower()
        if not callback(text):
            break


def reconocerVoz(callback):
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

                if not callback(texto):
                    break

            except sr.UnknownValueError:
                print("No entendí lo que dijiste. Intenta de nuevo.")
            except sr.RequestError as e:
                print("Error con el servicio de reconocimiento (¿internet?).")
                print(f"Detalle: {e}")
                break
