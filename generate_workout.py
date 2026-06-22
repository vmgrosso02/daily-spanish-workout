import os
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

# --- 0. SHARED LOCAL TIME (Miami, auto-adjusts for DST) ---
now_local = datetime.now(ZoneInfo("America/New_York"))

# --- 1. GENERATE DYNAMIC SPANISH DATE, TIME, AND SEASON ---
def get_spanish_date_and_season(now):
    days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    months = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

    day_of_week = days[now.weekday()]
    day = now.day
    month_name = months[now.month - 1]
    year = now.year

    # Meteorological Season Logic (June to August is Summer)
    month = now.month
    if 3 <= month <= 5:
        season = "Primavera 🌸"
    elif 6 <= month <= 8:
        season = "Verano ☀️"
    elif 9 <= month <= 11:
        season = "Otoño 🍂"
    else:
        season = "Invierno ❄️"

    hour_24 = now.hour
    minute = now.minute
    hour_12 = hour_24 % 12
    if hour_12 == 0:
        hour_12 = 12
    if 0 <= hour_24 < 12:
        period = "de la mañana"
    elif 12 <= hour_24 < 19:
        period = "de la tarde"
    else:
        period = "de la noche"
    time_str = f"{hour_12}:{minute:02d} {period}"

    return f"{day_of_week}, {day} de {month_name} de {year} | {season} | {time_str}"

date_header_string = get_spanish_date_and_season(now_local)

# --- 2. MANAGE THE WORD BANK PERSISTENCE ---
word_bank_file = "word_bank.json"
already_learned = []
word_review_html = "¡Este es tu primer día con el nuevo sistema! Pronto aquí verás tu palabra anterior."

if os.path.exists(word_bank_file):
    try:
        with open(word_bank_file, "r", encoding="utf-8") as f:
            word_bank = json.load(f)
            if word_bank:
                already_learned = [item["word"].lower().strip() for item in word_bank]
                last_item = word_bank[-1]
                w = last_item.get("word", "")
                wm = last_item.get("meaning", "")
                we = last_item.get("example", "")
                if we:
                    word_review_html = f"Anterior: {w} ({wm})<br><br>Ejemplo: {we}"
                else:
                    word_review_html = f"Anterior: {w} ({wm})<br><br>(No se guardó un ejemplo para esta entrada.)"
    except Exception as e:
        print(f"Note: Could not read word_bank.json ({e}). Starting a clean word bank.")
        word_bank = []
else:
    word_bank = []

# --- 3. MANAGE THE PHRASE BANK PERSISTENCE ---
phrase_bank_file = "phrase_bank.json"
already_learned_phrases = []
phrase_review_html = "¡Este es tu primer día con el sistema de frases! Pronto aquí verás tu frase anterior."

if os.path.exists(phrase_bank_file):
    try:
        with open(phrase_bank_file, "r", encoding="utf-8") as f:
            phrase_bank = json.load(f)
            if phrase_bank:
                already_learned_phrases = [item["phrase"].lower().strip() for item in phrase_bank]
                last_phrase = phrase_bank[-1]
                p = last_phrase.get("phrase", "")
                pm = last_phrase.get("meaning", "")
                pe = last_phrase.get("example", "")
                if pe:
                    phrase_review_html = f"Anterior: {p} ({pm})<br><br>Ejemplo: {pe}"
                else:
                    phrase_review_html = f"Anterior: {p} ({pm})<br><br>(No se guardó un ejemplo para esta entrada.)"
    except Exception as e:
        print(f"Note: Could not read phrase_bank.json ({e}). Starting a clean phrase bank.")
        phrase_bank = []
else:
    phrase_bank = []

# --- 4. LOAD THE STUDENT'S FULL KNOWN-VOCABULARY / GRAMMAR BASE FROM YOUR TEXT FILE ---
known_vocab_block = ""
if os.path.exists("spanish_vocab.txt"):
    try:
        with open("spanish_vocab.txt", "r", encoding="utf-8") as f:
            known_vocab_block = f.read().strip()
    except Exception as e:
        print(f"Note: Could not read spanish_vocab.txt ({e}).")

# --- 5. SECRETS VALIDATION ---
gemini_api_key = os.environ.get("GEMINI_API_KEY")
smtp_user = os.environ.get("SMTP_USER")
smtp_password = os.environ.get("SMTP_PASSWORD")
to_email = os.environ.get("TO_EMAIL")

if not gemini_api_key or not smtp_user or not smtp_password or not to_email:
    print("Error: Missing required environment variables.")
    exit(1)

# --- 6. BUILD THE PROMPT FOR GEMINI ---
blacklist_words_str = ", ".join(already_learned) if already_learned else "Ninguna todavía"
blacklist_phrases_str = ", ".join(already_learned_phrases) if already_learned_phrases else "Ninguna todavía"

prompt = f"""
Eres un tutor experto de español. Tu tarea es generar el código HTML puro responsivo para el entrenamiento de hoy.

Nivel gramatical del estudiante: Presente, Presente Progresivo, Pretérito e Imperfecto para todos los verbos listados en la base de conocimiento; Ser vs Estar; pronombres de objeto directo e indirecto; pronombres de objeto dobles (ej. "me lo trajiste"); tiempo compuesto/Presente Perfecto (he, has, ha, hemos, han + participio); mandatos básicos con terminaciones -an/-en; y pronombres reflexivos.

BASE DE CONOCIMIENTO DEL ESTUDIANTE (vocabulario, verbos y gramática que el estudiante YA conoce; esta es la fuente obligatoria de vocabulario para las secciones 3, 4 y 5):
{known_vocab_block}

REGLAS DE SELECCIÓN DE PALABRAS Y FRASES:
1. Debes elegir una palabra o modismo completamente NUEVO para la "Palabra del Día" y una frase completamente NUEVA para la "Frase del Día" que un estudiante de nivel intermedio-bajo no sabría de forma nativa.
2. Está TERMINANTEMENTE PROHIBIDO usar cualquiera de estas palabras ya aprendidas: [{blacklist_words_str}].
3. Está TERMINANTEMENTE PROHIBIDO usar cualquiera de estas frases ya aprendidas: [{blacklist_phrases_str}].
4. REGLA DE VOCABULARIO (MUY IMPORTANTE): Las secciones 3 (Blurb de la Calle), 4 (Reto 1) y 5 (Reto 2) son ejercicios de refuerzo y deben construirse ÚNICAMENTE con palabras, verbos, modismos y estructuras gramaticales que aparecen en la BASE DE CONOCIMIENTO DEL ESTUDIANTE indicada arriba (más palabras funcionales básicas como artículos, preposiciones, conjunciones y pronombres, aunque no estén listadas explícitamente). ESTÁ TERMINANTEMENTE PROHIBIDO usar en las secciones 3, 4 y 5 cualquier palabra o modismo que NO esté en esa base de conocimiento, incluyendo la palabra nueva del día y la frase nueva del día (que deben aparecer ÚNICAMENTE en las secciones 1 y 2). Si necesitas variar el vocabulario en los retos de traducción, elige otras palabras que SÍ estén en la base de conocimiento del estudiante.
6. En el review-box de la sección 2 (Frase del Día), escribe EXACTAMENTE y sin modificar, traducir, ni agregar nada más, el siguiente texto literal: PLACEHOLDER_PREV_PHRASE_REVIEW

Estructura de diseño requerida (No uses em-dashes ni guiones largos "—" como separadores, usa barras verticales "|" o dos puntos):
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

        <!-- 1. WORD OF THE DAY & REVIEW -->
        <div class="card">
          <div class="card-title">1. 🌟 La Palabra del Día (Word of the Day)</div>
          <div class="highlight-box">
            <strong>Palabra:</strong> [Nueva palabra en español] ([Traducción])
          </div>
          <div class="example-text"><strong>Ejemplo Práctico:</strong> "[Frase contextual]" ([Traducción])</div>

          <div class="review-box">
            🔄 <strong>Repaso de ayer:</strong><br>
            PLACEHOLDER_PREV_WORD_REVIEW
          </div>
        </div>

        <!-- 2. FRASE DEL DIA -->
        <div class="card">
          <div class="card-title">2. 🗣️ La Frase del Día (Common Phrase)</div>
          <div class="highlight-box" style="border-left-color: #a855f7;">
            <strong>Frase:</strong> [Frase útil] ([Traducción])
          </div>
          <div style="font-size: 14px; margin-bottom: 6px;"><strong>When to use:</strong> [Explicación de uso en inglés]</div>
          <div class="example-text"><strong>Ejemplo:</strong> "[Frase]" ([Traducción])</div>

          <div class="review-box" style="background-color: #fdf2f8; border-color: #ec4899; color: #9d174d;">
            🔄 <strong>Repaso de ayer:</strong><br>
            PLACEHOLDER_PREV_PHRASE_REVIEW
          </div>
        </div>

        <!-- 3. BLURB DE LA CALLE -->
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

        <!-- 4. RETO 1 -->
        <div class="card">
          <div class="card-title">4. 🔀 Reto 1: Traducir al Español (English ➔ Spanish)</div>
          <div class="challenge-box">
            <strong>Challenge:</strong> "[Frase en inglés]"
          </div>
        </div>

        <!-- 5. RETO 2 -->
        <div class="card">
          <div class="card-title">5. 🔄 Reto 2: Traducir al Inglés (Spanish ➔ English)</div>
          <div class="challenge-box" style="background-color: #f0fdf4; border-color: #dcfce7; color: #14532d;">
            <strong>Challenge:</strong> "[Frase en español]"
          </div>
        </div>

        <!-- SPOILERS -->
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

CRITICAL EXTRA INSTRUCTION: At the absolute bottom of your response, on brand new lines after the closing </html> tag, output exactly these tracking lines so the system script can save your progress. Use the pipe character | to separate each field, exactly 2 pipes per line, no extra commentary:
TRACK_WORD: <palabra elegida> | <traducción al inglés> | <el mismo Ejemplo Práctico que escribiste en la sección 1, en el formato: "frase en español" (traducción)>
TRACK_PHRASE: <frase elegida> | <traducción al inglés> | <el mismo Ejemplo que escribiste en la sección 2, en el formato: "frase en español" (traducción)>
"""

data = {"contents": [{"parts": [{"text": prompt}]}]}

models_to_try = ["gemini-3.5-flash", "gemini-3.1-flash-lite"]
max_retries_per_model = 2
workout_html = None

for model_name in models_to_try:
    model_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={gemini_api_key}"
    req = urllib.request.Request(model_url, data=json.dumps(data).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")

    for attempt in range(1, max_retries_per_model + 1):
        print(f"Llamando a la API de Gemini con {model_name}... (intento {attempt}/{max_retries_per_model})")
        try:
            with urllib.request.urlopen(req) as response:
                workout_html = json.loads(response.read().decode("utf-8"))['candidates'][0]['content']['parts'][0]['text']
                if workout_html.startswith("```html"):
                    workout_html = workout_html[7:]
                if workout_html.endswith("```"):
                    workout_html = workout_html[:-3]
                workout_html = workout_html.strip()
            break  # success, stop retrying this model
        except Exception as e:
            print(f"Error calling Gemini with {model_name} (attempt {attempt}): {e}")
            if attempt < max_retries_per_model:
                wait_time = 15 * attempt
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
    if workout_html:
        break  # success, stop trying other models

if not workout_html:
    print("All models and retries exhausted. Giving up.")
    exit(1)

# --- 7. INJECT THE REAL PREVIOUS WORD/PHRASE REVIEW (replaces Gemini's placeholders) ---
workout_html = workout_html.replace("PLACEHOLDER_PREV_WORD_REVIEW", word_review_html)
workout_html = workout_html.replace("PLACEHOLDER_PREV_PHRASE_REVIEW", phrase_review_html)

# --- 8. PARSE THE TARGET TRACKING DATA AND SAVE BACK TO THE BANKS ---
extracted_word = "Desconocida"
extracted_meaning = "Unknown"
extracted_example = ""
extracted_phrase = "Desconocida"
extracted_phrase_meaning = "Unknown"
extracted_phrase_example = ""
cleaned_lines = []

for line in workout_html.split("\n"):
    if "TRACK_WORD:" in line:
        try:
            parts = line.replace("TRACK_WORD:", "").strip().split("|")
            if len(parts) >= 2:
                extracted_word = parts[0].strip()
                extracted_meaning = parts[1].strip()
            if len(parts) >= 3:
                extracted_example = parts[2].strip()
        except:
            pass
    elif "TRACK_PHRASE:" in line:
        try:
            parts = line.replace("TRACK_PHRASE:", "").strip().split("|")
            if len(parts) >= 2:
                extracted_phrase = parts[0].strip()
                extracted_phrase_meaning = parts[1].strip()
            if len(parts) >= 3:
                extracted_phrase_example = parts[2].strip()
        except:
            pass
    else:
        cleaned_lines.append(line)

workout_html = "\n".join(cleaned_lines).strip()

today_str = now_local.strftime("%Y-%m-%d")

# Save word to word_bank
if extracted_word != "Desconocida":
    word_bank.append({
        "word": extracted_word,
        "meaning": extracted_meaning,
        "example": extracted_example,
        "date": today_str
    })
    try:
        with open(word_bank_file, "w", encoding="utf-8") as f:
            json.dump(word_bank, f, ensure_ascii=False, indent=2)
        print(f"Saved word '{extracted_word}' to the word bank.")
    except Exception as e:
        print(f"Error saving word bank: {e}")

# Save phrase to phrase_bank
if extracted_phrase != "Desconocida":
    phrase_bank.append({
        "phrase": extracted_phrase,
        "meaning": extracted_phrase_meaning,
        "example": extracted_phrase_example,
        "date": today_str
    })
    try:
        with open(phrase_bank_file, "w", encoding="utf-8") as f:
            json.dump(phrase_bank, f, ensure_ascii=False, indent=2)
        print(f"Saved phrase '{extracted_phrase}' to the phrase bank.")
    except Exception as e:
        print(f"Error saving phrase bank: {e}")

# --- 9. WRITE HUMAN-READABLE .TXT MIRRORS OF EACH BANK ---
def write_readable_bank(filepath, bank, item_key, label):
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"{label}\n")
            f.write("=" * len(label) + "\n\n")
            for i, item in enumerate(bank, 1):
                f.write(f"{i}. {item.get(item_key, '')} — {item.get('meaning', '')}\n")
                f.write(f"   Fecha: {item.get('date', '')}\n")
                example = item.get("example")
                if example:
                    f.write(f"   Ejemplo: {example}\n")
                f.write("\n")
    except Exception as e:
        print(f"Error writing {filepath}: {e}")

write_readable_bank("word_bank.txt", word_bank, "word", "📚 Banco de Palabras Aprendidas")
write_readable_bank("phrase_bank.txt", phrase_bank, "phrase", "🗣️ Banco de Frases Aprendidas")

# --- 10. DISPATCH THE EMAIL ---
msg = MIMEMultipart()
msg['From'] = smtp_user
msg['To'] = to_email
msg['Subject'] = f"📅 Entrenamiento Diario: {date_header_string.split('|')[0].strip()}"
msg.attach(MIMEText(workout_html, 'html'))

print("Sending email...")
try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(smtp_user, smtp_password)
    server.sendmail(smtp_user, to_email, msg.as_string())
    server.close()
    print("Success! Spanish workout emailed.")
except Exception as e:
    print(f"SMTP Error: {e}")
    exit(1)
