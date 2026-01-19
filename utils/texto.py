import re
import unicodedata


def normalizar_texto(texto: str) -> str:
    texto = texto.strip().lower()
    return "".join(
        caracter
        for caracter in unicodedata.normalize("NFD", texto)
        if unicodedata.category(caracter) != "Mn"
    )


def contiene_frase(texto: str, frases: tuple[str, ...]) -> bool:
    return any(frase in texto for frase in frases)


def extraer_regex(patron: str, texto: str) -> re.Match | None:
    return re.search(patron, texto)
