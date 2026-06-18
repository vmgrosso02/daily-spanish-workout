import os
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import urllib.request

# 1. Buscar palabras personalizadas en tu repositorio
vocab_context = ""
if os.path.exists("spanish_vocab.txt"):
    try:
        with open("spanish_vocab.txt", "r", encoding="utf-8") as f:
            words = [line.strip() for line in f if line.strip()]
        if words:
            sample_words = random.sample(words, min(len(words), 8))
            vocab_context = f"\nPor favor, intenta incorporar o basarte en algunas de estas palabras/frases de la lista del usuario: {', '.join(sample_words)}"
    except Exception as e:
        print(f"Nota: No se pudo leer spanish_vocab.txt ({e}), continuando sin él.")

# 2. Obtener tus secretos de GitHub Actions
gemini_api_key = os.environ.get("GEMINI_API_KEY")
smtp_user = os.environ.get("SMTP_USER")
smtp_password = os.environ.get("SMTP_PASSWORD")
to_email = os.environ.get("TO_EMAIL")

if not gemini_api_key or not smtp_user or not smtp_password or not to_email:
    print("Error: Faltan variables de entorno requeridas (GEMINI_API_KEY, SMTP_USER, SMTP_PASSWORD, o TO_EMAIL).")
    exit(1)

# 3. Solicitar el entrenamiento personalizado con el formato original
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_api_key}"

prompt = f"""
Eres un tutor experto de español. Tu tarea es generar un correo electrónico titulado "📅 Mi Entrenamiento Diario" estructurado EXACTAMENTE con el formato de las 5 secciones de abajo. 

Nivel de gramática del estudiante para construir los ejemplos y retos:
- Presente: Verbos regulares (comer, beber, hablar) y de cambio de raíz (querer, dormir, almorzar, poder, volver, empezar, entender).
- Ser vs Estar: Distinciones de rasgos vs estados/ubicaciones temporales.
- Pretérito: Verbos regulares (-ar, -er, -ir) e irregulares comunes (fui, estuve, dije, hice, traje, tuve).
- Estructuras de imperfecto, mandatos básicos y pronombres de objeto directo/indirecto (me parece, le dije).
{vocab_context}

Estructura estricta que debes replicar (usa exactamente estos títulos y formato):

📅 Mi Entrenamiento Diario
1. 🌟 La Palabra del Día (Word of the Day)
Palabra: [Palabra en español] ([Traducción al inglés]) — [Nota de contexto, ej: Nueva palabra o de tu lista]
Ejemplo Práctico: "[Frase natural en español]" ([Traducción al inglés]).

2. 🗣️ La Frase del Día (Common Phrase)
Frase: [Frase/Modismo en español] ([Traducción al inglés]) — [Nota]
Uso: [Breve explicación de cuándo usarla].
Ejemplo: "[Frase en español]" ([Traducción al inglés]).

3. 💬 El Blurb de la Calle (Conversational Snippet)
Persona A: "[Línea corta de diálogo natural]"
Persona B: "[Respuesta corta de diálogo natural]"
English Translation:
Persona A: "[Traducción al inglés]"
Persona B: "[Traducción al inglés]"

4. 🔀 Reto 1: Traducir al Español (English ➔ Spanish)
Challenge: "[Una frase en inglés para que el usuario traduzca usando su nivel de gramática]"

5. 🔄 Reto 2: Traducir al Inglés (Spanish ➔ English)
Challenge: "[Una frase en español para que el usuario traduzca al inglés]"

---
🔑 CLAVE DE RESPUESTAS (ANSWER KEY)
(Deja un espacio amplio abajo y coloca las respuestas correctas para el Reto 1 y Reto 2 aquí, para que funcionen como spoiler y el usuario no las vea de inmediato al abrir el correo).
Objetivo de traducción Reto 1: "[Traducción exacta esperada]"
Objetivo de traducción Reto 2: "[Traducción exacta esperada]"

Nota: Asegúrate de que todas las palabras utilizadas se ajusten estrictamente al nivel del estudiante y prioriza incluir términos de su lista si se proporcionaron. Mantén el formato limpio en texto plano para correos.
"""

data = {
    "contents": [{
        "parts": [{"text": prompt}]
    }]
}

print("Llamando a la API de Gemini...")
req = urllib.request.Request(
    url,
    data=json.dumps(data).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST"
)

try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode("utf-8"))
        workout_text = result['candidates'][0]['content']['parts'][0]['text']
except Exception as e:
    print(f"Error al llamar a Gemini: {e}")
    exit(1)

# 4. Formatear y enviar el correo electrónico
msg = MIMEMultipart()
msg['From'] = smtp_user
msg['To'] = to_email  
msg['Subject'] = "📅 Mi Entrenamiento Diario 🇪🇸"
msg.attach(MIMEText(workout_text, 'plain'))

print("Enviando correo electrónico...")
try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(smtp_user, smtp_password)
    server.sendmail(smtp_user, to_email, msg.as_string())
    server.close()
    print("¡Éxito! Tu entrenamiento diario de español ha sido enviado por correo.")
except Exception as e:
    print(f"Error al enviar el correo: {e}")
    exit(1)
