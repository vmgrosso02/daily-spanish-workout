import os
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import urllib.request
from datetime import datetime

# --- 1. GENERATE DYNAMIC SPANISH DATE AND SEASON ---
def get_spanish_date_and_season():
    now = datetime.now()
    days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    months = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    
    day_of_week = days[now.weekday()]
    day = now.day
    month_name = months[now.month - 1]
    year = now.year
    
    # Season logic (Northern Hemisphere standard)
    md = (now.month, now.day)
    if (3, 21) <= md <= (6, 20):
        season = "Primavera 🌸"
    elif (6, 21) <= md <= (9, 22):
        season = "Verano ☀️"
    elif (9, 23) <= md <= (12, 20):
        season = "Otoño 🍂"
    else:
        season = "Invierno ❄️"
        
    return f"{day_of_week}, {day} de {month_name} de {year} — {season}"

date_header_string = get_spanish_date_and_season()

# --- 2. MANAGE THE NEW WORD BANK PERSISTENCE ---
word_bank_file = "word_bank.json"
already_learned = []
previous_word_info = "Ninguna (¡Este es tu primer día con el nuevo sistema!)"

if os.path.exists(word_bank_file):
    try:
        with open(word_bank_file, "r", encoding="utf-8") as f:
            word_bank = json.load(f)
            if word_bank:
                already_learned = [item["word"].lower().strip() for item in word_bank]
                last_item = word_bank[-1]
                previous_word_info = f"'{last_item['word']}' ({last_item['meaning']})"
    except Exception as e:
        print(f"Nota: No se pudo leer el banco de palabras ({e}). Iniciando uno vacío.")
        word_bank = []
else:
    word_bank = []

# --- 3. LOOK FOR CUSTOM VOCABULARY WORDS FROM YOUR TEXT FILE ---
vocab_context = ""
if os.path.exists("spanish_vocab.txt"):
    try:
        with open("spanish_vocab.txt", "r", encoding="utf-8") as f:
            words = [line.strip() for line in f if line.strip()]
        if words:
            sample_words = random.sample(words, min(len(words), 8))
            vocab_context = f"Para los retos de traducción y diálogos, puedes inspirarte en estos términos que el usuario ya conoce: {', '.join(sample_words)}."
    except Exception as e:
        print(f"Nota: No se pudo leer spanish_vocab.txt ({e}).")

# --- 4. SECRETS VALIDATION ---
gemini_api_key = os.environ.get("GEMINI_API_KEY")
smtp_user = os.environ.get("SMTP_USER")
smtp_password = os.environ.get("SMTP_PASSWORD")
to_email = os.environ.get("TO_EMAIL")

if not gemini_api_key or not smtp_user or not smtp_password or not to_email:
    print("Error: Faltan variables de entorno esenciales.")
    exit(1)

# --- 5. BUILD THE PROMPT FOR GEMINI ---
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_api_key}"

blacklist_str = ", ".join(already_learned) if already_learned else "Ninguna todavía"

prompt = f"""
Eres un tutor experto de español. Tu tarea es generar el código HTML puro responsivo para el entrenamiento de hoy. 

Nivel gramatical: Presente (regulares/cambio de raíz), Ser/Estar básicos, Pretérito (regulares e irregulares: fui, estuve, dije, hice, traje, tuve), Imperfecto básico, mandatos directos y pronombres de objeto.
{vocab_context}

REGLAS DE SELECCIÓN DE PALABRAS:
1. Debes elegir una palabra o modismo completamente NUEVO que un estudiante de nivel intermedio-bajo no sabría de forma nativa.
2. Está TERMINANTEMENTE PROHIBIDO usar cualquiera de estas palabras ya aprendidas: [{blacklist_str}].
3. Debes incluir un pequeño repaso de la palabra del día anterior: "{previous_word_info}". Puede ser una pregunta corta, una oración de ejemplo o una nota de traducción rápida dentro de la tarjeta de la sección 1.

Entrega exclusivamente el código estructurado dentro de esta plantilla CSS. No uses bloques de código markdown (```html).

Estructura de diseño requerida:
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; color: #334155; margin: 0; padding: 0; }}
    .wrapper {{ width: 100%; background-color: #f8fafc; padding: 20px 0; }}
    .container {{ max-width: 580px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); border: 1px solid #e2e8f0; }}
    .header {{ background: linear-gradient(135deg, #1e293b 0%, #334155 100%); color: #ffffff; padding: 28px 24px; text-align: center; border-bottom: 4px solid #ef4444; }}
    .header h1 {{ margin: 0; font-size: 20px; font-weight: 700; letter-spacing: -0.3px; }}
    .content {{ padding: 24px; }}
    .card {{ background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
    .card-title {{ font-size: 14px; font-weight: 700; color: #1e40af; margin-top: 0; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px; }}
    .highlight-box {{ background-color: #f1f5f9; padding: 14px; border-left: 4px solid #3b82f6; margin: 12px 0; border-radius: 0 6px 6px 0; font-size: 15px; }}
    .review-box {{ background-color: #f0fdfa; padding: 10px 14px; border: 1px dashed #0d9488; margin-top: 12px; border-radius: 6px; font-size: 13px; color: #0f766e; }}
    .example-text {{ font-style: italic; color: #475569; margin-top: 6px; font-size: 14px; }}
    .dialogue {{ background-color: #f8fafc; border-radius: 6px; padding: 14px; border: 1px solid #e2e8f0; font-size: 14px; }}
    .dialogue-line {{ margin-bottom: 8px; line-height: 1.5; }}
    .challenge-box {{ background-color: #fffbeb; border: 1px solid #fef3c7; padding: 16px; border-radius: 8px; color: #78350f; font-size: 15px; line-height: 1.5; }}
    .spoiler-section {{ margin-top: 45px; border-top: 2px dashed #cbd5e1; padding-top: 25px; }}
    .spoiler-header {{ font-size: 12px; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 1.5px; text-align: center; margin-bottom: 16px; }}
    .answer-key {{ background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 18px; font-size: 14px; color: #475569; }}
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="container">
      <div class="header">
        <h1>{date_header_string}</h1>
      </div>
      <div class="content">
        
        <div class="card">
          <div class="card-title">1. 🌟 La Palabra del Día (Word of the Day)</div>
          <div class="highlight-box">
            <strong>Palabra:</strong> [Nueva palabra en español] ([Traducción]) — <span style="color: #ef4444; font-size: 12px; font-weight: bold;">[¡Nueva Palabra!]</span>
          </div>
          <div class="example-text"><strong>Ejemplo Práctico:</strong> "[Frase contextual]" ([Traducción])</div>
          
          <div class="review-box">
            🔄 <strong>Repaso de ayer:</strong> [Pon aquí un minireto, traducción rápida o recordatorio usando la palabra previa: {previous_word_info}]
          </div>
        </div>

        <div class="card">
          <div class="card-title">2. 🗣️ La Frase del Día (Common Phrase)</div>
          <div class="highlight-box" style="border-left-color: #a855f7;">
            <strong>Frase:</strong> [Frase útil] ([Traducción])
          </div>
          <div style="font-size: 14px; margin-bottom: 6px;"><strong>Uso:</strong> [Cuándo se usa]</div>
          <div class="example-text"><strong>Ejemplo:</strong> "[Frase]" ([Traducción])</div>
        </div>

        <div class="card">
          <div class="card-title">3. 💬 El Blurb de la Calle (Conversational Snippet)</div>
          <div class="dialogue">
            <div class="dialogue-line"><strong>Persona A:</strong> "[Línea 1]"</div>
            <div class="dialogue-line"><strong>Persona B:</strong> "[Línea 2]"</div>
            <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 10px 0;">
            <div class="dialogue-line" style="color: #64748b; font-style: italic;"><strong>English:</strong></div>
            <div class="dialogue-line" style="color: #64748b;">Persona A: "[Traducción 1]"</div>
            <div class="dialogue-line" style="color: #64748b;">Persona B: "[Traducción 2]"</div>
          </div>
        </div>

        <div class="card">
          <div class="card-title">4. 🔀 Reto 1: Traducir al Español (English ➔ Spanish)</div>
          <div class="challenge-box">
            <strong>Challenge:</strong> "[Frase en inglés]"
          </div>
        </div>

        <div class="card">
          <div class="card-title">5. 🔄 Reto 2: Traducir al Inglés (Spanish ➔ English)</div>
          <div class="challenge-box" style="background-color: #f0fdf4; border-color: #dcfce7; color: #14532d;">
            <strong>Challenge:</strong> "[Frase en español]"
          </div>
        </div>

        <div class="spoiler-section">
          <div class="spoiler-header">👇 CLAVE DE RESPUESTAS / ANSWER KEY</div>
          <div class="answer-key">
            <p style="margin-top: 0;"><strong>Objetivo Reto 1:</strong><br>"[Traducción]"</p>
            <p style="margin-bottom: 0;"><strong>Objetivo Reto 2:</strong><br>"[Traducción]"</p>
          </div>
        </div>

      </div>
    </div>
  </div>
</body>
</html>

CRITICAL EXTRA INSTRUCTION: At the absolute bottom of your response, on a brand new line, output exactly this tracking text so the system script can save the progress:
TRACK_WORD: <word chosen> | <english translation>
"""

data = {"contents": [{"parts": [{"text": prompt}]}]}

print("Llamando a la API de Gemini...")
req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")

try:
    with urllib.request.urlopen(req) as response:
        workout_html = json.loads(response.read().decode("utf-8"))['candidates'][0]['content']['parts'][0]['text']
        if workout_html.startswith("
http://googleusercontent.com/immersive_entry_chip/0
http://googleusercontent.com/immersive_entry_chip/1

### What to expect next:
1. Save and commit both modifications.
2. Trigger the action via the **Run workflow** button.
3. You will receive an beautifully rendered email box where the large dark slate-blue card displays the exact localized calendar date and season. 
4. Check your code folder a minute later: a new file called `word_bank.json` will automatically appear in your repository containing your very first tracked word! Every subsequent execution will block previously generated items while generating rolling context reviews seamlessly.
