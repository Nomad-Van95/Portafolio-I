from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
from openai import OpenAI
import io
import re
import os

app = FastAPI()

# CORS para permitir peticiones desde el navegador (index.html)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Aquí se guarda el texto del documento cargado
DOCUMENT_TEXT = ""


# Diccionario base de palabras en inglés más comunes (puedes ampliarlo)
ENGLISH_WORDS = {
    "hello", "world", "code", "developer", "portfolio", "project",
    "react", "python", "javascript", "login", "user", "admin",
    "home", "about", "contact", "work", "design", "build"
}

def use_english_words(text: str, strict: bool = False) -> dict:
    """
    Filtra y usa palabras en inglés desde un texto.
    
    Args:
        text: Texto a analizar
        strict: Si True, solo acepta palabras del diccionario ENGLISH_WORDS
                Si False, acepta cualquier palabra con solo letras inglesas a-z
    
    Returns:
        dict con palabras válidas, no válidas y texto limpio
    """
    import re
    
    # Limpia y separa palabras
    words = re.findall(r"[a-zA-Z]+", text.lower())
    
    valid = []
    invalid = []
    
    for word in words:
        if strict:
            if word in ENGLISH_WORDS:
                valid.append(word)
            else:
                invalid.append(word)
        else:
            # Modo no estricto: acepta cualquier palabra en alfabeto inglés
            if word.isascii() and word.isalpha():
                valid.append(word)
            else:
                invalid.append(word)
    
    return {
        "valid_english": valid,
        "invalid": invalid,
        "clean_text": " ".join(valid),
        "count": len(valid)
    }

# --- EJEMPLO DE USO ---

# Ejemplo 1: Modo simple
resultado = use_english_words("Hola hello world 123")
print(resultado)
# {'valid_english': ['hola', 'hello', 'world'], 'invalid': [], 'clean_text': 'hola hello world', 'count': 3}

# Ejemplo 2: Modo estricto (solo palabras de tu diccionario)
resultado2 = use_english_words("hello mundo portfolio", strict=True)
print(resultado2)
# {'valid_english': ['hello', 'portfolio'], 'invalid': ['mundo'], 'clean_text': 'hello portfolio', 'count': 2}

# --- FUNCIÓN EXTRA PARA TU PORTAFOLIO ---
def translate_to_english_key(spanish_text: str) -> str:
    """Convierte texto español a clave en inglés para usar en tu app"""
    mapping = {
        "proyectos": "projects",
        "contacto": "contact",
        "habilidades": "skills",
        "sobre mi": "about",
        "inicio": "home"
    }
    return mapping.get(spanish_text.lower(), spanish_text.lower().replace(" ", "_"))