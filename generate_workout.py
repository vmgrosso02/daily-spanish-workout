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
    
    # Meteorological Season Logic
    month = now.month
    if 3 <= month <= 5:
        season = "Primavera 🌸"
    elif 6 <= month <= 8:
        season = "Verano ☀️"
    elif 9 <= month <= 11:
        season = "Otoño 🍂"
    else:
        season = "Invierno ❄️"
        
    return f"{day_of_week}, {day} de {month_name} de {year} | {season}"

date_header_string = get_spanish_date_and_season()

# --- 2. MANAGE THE WORD BANK PERSISTENCE ---
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
        print(f"Note: Could not read word_bank.json ({e}). Starting a clean word bank.")
        word_bank = []
else:
    word_bank = []

# --- 3. MANAGE THE PHRASE BANK PERSISTENCE ---
phrase_bank_file = "phrase_bank.json"
already_learned_phrases = []
previous_phrase_info = "Ninguna (¡Este es tu primer día con el sistema de frases!)"

if os.path.exists(phrase_bank_file):
    try:
        with open(phrase_bank_file, "r", encoding="utf-8") as f:
            phrase_bank = json.load(f)
            if phrase_bank:
                already_learned_phrases = [item["phrase"].lower().strip() for item in phrase_bank]
                last_phrase = phrase_bank[-1]
                previous_phrase_info = f"'{last_phrase['phrase']}' ({last_phrase['meaning']})"
    except Exception as e:
        print(f"Note: Could not read phrase_bank.json ({e}). Starting a clean phrase bank.")
        phrase_bank = []
else:
    phrase_bank = []

# --- 4. LOAD THE ENTIRE VOCABULARY FILE FOR THE PROMPT ---
vocab_content = ""
if os.path.exists("spanish_vocab.txt"):
    try:
        with open("spanish_vocab.txt", "r", encoding="utf-8") as f:
            vocab_content = f.read().strip()
    except Exception as e:
        print(f"Error reading spanish_vocab.txt: {e}")
        vocab_content = "Default: comer, beber, hablar, tener, querer"

# --- 5. SECRETS VALIDATION ---
gemini_api_key = os.environ.get("GEMINI_API_KEY")
smtp_user = os.environ.get("SMTP_USER")
smtp_password = os.environ.get("SMTP_PASSWORD")
to_email = os.environ.get("TO_EMAIL")

if not gemini_api_key or not smtp_user or not smtp_password or not to_email:
    print("Error: Missing required environment variables.")
    exit(1)

# --- 6. BUILD THE PROMPT FOR GEMINI ---
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_api_key}"

blacklist_words_str = ", ".join(already_learned) if already_learned else "None yet"
blacklist_phrases_str = ", ".join(already_learned_phrases) if already_learned_phrases else "None yet"

prompt = f"""
Eres un tutor experto de español. Tu tarea es generar el código HTML puro responsivo para el entrenamiento de hoy.

CRITICAL INSTRUCTION (ABSOLUTE VOCABULARY CONSTRAINT):
Except for the "Word of the Day" (Section 1) and "Phrase of the Day" (Section 2) which are meant to teach NEW concepts, ALL OTHER SECTIONS—including Section 3 (Conversational Snippet), Section 4 (Translate to Spanish), and Section 5 (Translate to English)—MUST ONLY USE words that are explicitly present in the Student's Vocabulary list below, or direct allowed conjugations of verbs. 
You are STRICTLY FORBIDDEN from using any Spanish word, noun, adjective, or verb that is not in this document. Do not assume or guess. Stick 100% to this vocabulary:

=== STUDENT ALLOWED VOCABULARY ===
{vocab_content}
==================================

REGLAS DE SELECCIÓN DE PALABRAS Y FRASES NUEVAS:
1. "Palabra del Día" (Section 1) and "Frase del Día" (Section 2) must introduce a completely NEW vocabulary term or spoken idiom that is NOT in the student's vocabulary sheet.
2. DO NOT select any word present in this blacklist: [{blacklist_words_str}].
3. DO NOT select any phrase present in this blacklist: [{blacklist_phrases_str}].
4. In Section 1 (Review Box), write a quick micro-challenge or translation test using yesterday's word: {previous_word_info}.
5. In Section 2 (Review Box), write a quick micro-challenge or translation test using yesterday's phrase: {previous_phrase_info}.

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
    .card {{ background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin
