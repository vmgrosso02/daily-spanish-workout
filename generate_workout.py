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
            vocab_context = f"Por favor, prioriza incorporar o basarte en algunas de estas palabras/frases reales de la lista personal del usuario: {', '.join(sample_words)}."
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

# 3. Solicitar entrenamiento en un formato HTML puro y móvil-responsivo
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_api_key}"

prompt = f"""
Eres un tutor experto de español. Tu tarea es generar el código de cuerpo de un correo electrónico en formato HTML puro que sea 100% responsivo para teléfonos y computadoras. 

Nivel de gramática del estudiante:
- Presente: Verbos regulares e irregulares con cambio de raíz (querer, dormir, almorzar, poder, volver, empezar, entender).
- Ser vs Estar: Rasgos vs estados temporales/ubicaciones.
- Pretérito: Verbos regulares e irregulares de alta frecuencia (fui, estuve, dije, hice, traje, tuve).
- Estructuras de imperfecto, mandatos básicos y pronombres de objeto directo/indirecto (me parece, le dije).
{vocab_context}

Debes estructurar el HTML usando la siguiente plantilla CSS de diseño limpio. No uses bloques de código de markdown (como ```html) en tu respuesta. Devuelve exclusivamente el código HTML listo para usar.

Usa exactamente esta estructura visual interna dentro del cuerpo del HTML:

<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; color: #334155; margin: 0; padding: 0; }}
    .wrapper {{ width: 100%; background-color: #f8fafc; padding: 20px 0; }}
    .container {{ max-width: 580px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); border: 1px solid #e2e8f0; }}
    .header {{ background: linear-gradient(135deg, #1e293b 0%, #334155 100%); color: #ffffff; padding: 32px 24px; text-align: center; border-bottom: 4px solid #ef4444; }}
    .header h1 {{ margin: 0; font-size: 24px; font-weight: 700; letter-spacing: -0.5px; }}
    .header p {{ margin: 6px 0 0 0; opacity: 0.85; font-size: 14px; }}
    .content {{ padding: 24px; }}
    .card {{ background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
    .card-title {{ font-size: 15px; font-weight: 700; color: #1e40af; margin-top: 0; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px; }}
    .highlight-box {{ background-color: #f1f5f9; padding: 14px; border-left: 4px solid #3b82f6; margin: 12px 0; border-radius: 0 6px 6px 0; font-size: 15px; }}
    .example-text {{ font-style: italic; color: #475569; margin-top: 6px; font-size: 14px; }}
    .dialogue {{ background-color: #f8fafc; border-radius: 6px; padding: 14px; border: 1px solid #e2e8f0; font-size: 14px; }}
    .dialogue-line {{ margin-bottom: 8px; line-height: 1.5; }}
    .dialogue-line:last-child {{ margin-bottom: 0; }}
    .challenge-box {{ background-color: #fffbeb; border: 1px solid #fef3c7; padding: 16px; border-radius: 8px; color: #78350f; font-size: 15px; line-height: 1.5; }}
    .spoiler-section {{ margin-top: 50px; border-top: 2px dashed #cbd5e1; padding-top: 30px; }}
    .spoiler-header {{ font-size: 12px; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 1.5px; text-align: center; margin-bottom: 16px; }}
    .answer-key {{ background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 18px; font-size: 14px; line-height: 1.6; color: #475569; }}
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="container">
      <div class="header">
        <h1>📅 Mi Entrenamiento Diario</h1>
        <p>Tu dosis personalizada de práctica e inputs reales</p>
      </div>
      <div class="content">
        
        <div class="card">
          <div class="card-title">1. 🌟 La Palabra del Día (Word of the Day)</div>
          <div class="highlight-box">
            <strong>Palabra:</strong> [Palabra en español] ([Traducción]) — <span style="color: #64748b; font-size: 12px;">[Nota de procedencia]</span>
          </div>
          <div class="example-text"><strong>Ejemplo Práctico:</strong> "[Frase]" ([Traducción al inglés])</div>
        </div>

        <div class="card">
          <div class="card-title">2. 🗣️ La Frase del Día (Common Phrase)</div>
          <div class="highlight-box">
            <strong>Frase:</strong> [Frase en español] ([Traducción])
          </div>
          <div style="font-size: 14px; margin-bottom: 8px;"><strong>Uso:</strong> [Explicación corta de uso]</div>
          <div class="example-text"><strong>Ejemplo:</strong> "[Frase]" ([Traducción al inglés])</div>
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
            <strong>Challenge:</strong> "[Frase en inglés retadora usando su gramática]"
          </div>
        </div>

        <div class="card">
          <div class="card-title">5. 🔄 Reto 2: Traducir al Inglés (Spanish ➔ English)</div>
          <div class="challenge-box" style="background-color: #f0fdf4; border-color: #dcfce7; color: #14532d;">
            <strong>Challenge:</strong> "[Frase en español retadora usando su gramática]"
          </div>
        </div>

        <div class="spoiler-section">
          <div class="spoiler-header">👇 CLAVE DE RESPUESTAS / ANSWER KEY</div>
          <div class="answer-key">
            <p style="margin-top: 0;"><strong>Objetivo de traducción Reto 1:</strong><br>"[Traducción exacta al español]"</p>
            <p style="margin-bottom: 0;"><strong>Objetivo de traducción Reto 2:</strong><br>"[Traducción exacta al inglés]"</p>
          </div>
        </div>

      </div>
    </div>
  </div>
</body>
</html>
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
        workout_html = result['candidates'][0]['content']['parts'][0]['text']
        
        # Limpieza de seguridad en caso de que Gemini devuelva bloques de código markdown
        if workout_html.startswith("```html"):
            workout_html = workout_html[7:]
        if workout_html.endswith("```"):
            workout_html = workout_html[:-3]
        workout_html = workout_html.strip()
        
except Exception as e:
    print(f"Error al llamar a Gemini: {e}")
    exit(1)

# 4. Formatear y enviar el correo electrónico (Cambiado a 'html')
msg = MIMEMultipart()
msg['From'] = smtp_user
msg['To'] = to_email  
msg['Subject'] = "📅 Mi Entrenamiento Diario 🇪🇸"
msg.attach(MIMEText(workout_html, 'html'))

print("Enviando correo electrónico...")
try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(smtp_user, smtp_password)
    server.sendmail(smtp_user, to_email, msg.as_string())
    server.close()
    print("¡Éxito! Tu entrenamiento premium de español ha sido enviado por correo.")
except Exception as e:
    print(f"Error al enviar el correo: {e}")
    exit(1)
