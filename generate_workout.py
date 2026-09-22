import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google import genai
from google.genai import types

# Load secrets
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip("[]'\" ")
SMTP_USER = os.environ.get("SMTP_USER", "").strip("[]'\" ")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "").strip("[]'\" ")
TO_EMAIL = os.environ.get("TO_EMAIL", "").strip("[]'\" ")

WORD_BANK_JSON = "word_bank.json"
PHRASE_BANK_JSON = "phrase_bank.json"
WORD_BANK_TXT = "word_bank.txt"
PHRASE_BANK_TXT = "phrase_bank.txt"

def load_json_list(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception as e:
            print(f"Warning: Failed to load {filepath}: {e}")
    return []

def save_json_list(filepath, data_list):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data_list, f, ensure_ascii=False, indent=2)

def write_txt_history(filepath, data_list):
    with open(filepath, "w", encoding="utf-8") as f:
        for item in data_list:
            f.write(f"{item}\n")

used_words = load_json_list(WORD_BANK_JSON)
used_phrases = load_json_list(PHRASE_BANK_JSON)

# Initialize Gemini Client
client = genai.Client(api_key=GEMINI_API_KEY)

prompt = f"""
You are an expert Spanish language instructor creating a daily "Mi Entrenamiento Diario" lesson for an intermediate learner.

Provide a structured, engaging daily workout in HTML format for an email newsletter body.

STRICT CONSTRAINTS:
1. Do NOT use any words from this used word bank: {json.dumps(used_words[-100:])}
2. Do NOT use any phrases from this used phrase bank: {json.dumps(used_phrases[-50:])}

OUTPUT REQUIREMENTS:
Return valid JSON matching this schema:
{{
  "selected_word": "Spanish word introduced today",
  "selected_phrase": "Spanish phrase introduced today",
  "html_content": "Complete HTML string for email body"
}}

CONTENT STRUCTURE IN HTML:
- Header: "Mi Entrenamiento Diario"
- Section 1: Palabra del Día (Word, English translation, example sentence)
- Section 2: Frase del Día (Phrase, English translation, example usage context)
- Section 3: Ejercicio Práctico (3 short translation practice items)
- Section 4: Cultural or Grammar Tip (1-2 quick sentences)
"""

# Call model
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=0.7,
    ),
)

data = json.loads(response.text)

selected_word = data.get("selected_word", "").strip()
selected_phrase = data.get("selected_phrase", "").strip()
html_body = data.get("html_content", "")

# Save history
if selected_word and selected_word not in used_words:
    used_words.append(selected_word)
    save_json_list(WORD_BANK_JSON, used_words)
    write_txt_history(WORD_BANK_TXT, used_words)

if selected_phrase and selected_phrase not in used_phrases:
    used_phrases.append(selected_phrase)
    save_json_list(PHRASE_BANK_JSON, used_phrases)
    write_txt_history(PHRASE_BANK_TXT, used_phrases)

# Send Email
msg = MIMEMultipart("alternative")
msg["Subject"] = f"Mi Entrenamiento Diario: {selected_word} & {selected_phrase}"
msg["From"] = SMTP_USER
msg["To"] = TO_EMAIL
msg.attach(MIMEText(html_body, "html", "utf-8"))

with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login(SMTP_USER, SMTP_PASSWORD)
    server.sendmail(SMTP_USER, TO_EMAIL, msg.as_string())

print(f"Successfully generated workout and sent email to {TO_EMAIL}.")
