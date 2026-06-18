import os
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import urllib.request

# 1. Look for custom vocabulary words in your repository
vocab_context = ""
if os.path.exists("spanish_vocab.txt"):
    try:
        with open("spanish_vocab.txt", "r", encoding="utf-8") as f:
            words = [line.strip() for line in f if line.strip()]
        if words:
            sample_words = random.sample(words, min(len(words), 8))
            vocab_context = f"\nPlease try to incorporate some of these specific vocabulary words/phrases into today's workout: {', '.join(sample_words)}"
    except Exception as e:
        print(f"Note: Could not read spanish_vocab.txt ({e}), proceeding without it.")

# 2. Grab your secret keys from repository settings
gemini_api_key = os.environ.get("GEMINI_API_KEY")
email_user = os.environ.get("EMAIL_USER")
email_password = os.environ.get("EMAIL_PASSWORD")

if not gemini_api_key or not email_user or not email_password:
    print("Error: Missing required environment variables (GEMINI_API_KEY, EMAIL_USER, or EMAIL_PASSWORD).")
    exit(1)

# 3. Request a personalized lesson layout from Gemini
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_api_key}"

prompt = f"""
You are an expert personal Spanish tutor. Generate a daily "Spanish Workout" for a student with the following current grammar knowledge base:
- Present Tense: Regular verbs (comer, beber, hablar) and stem-changing verbs (querer, dormir, almorzar, poder, volver, empezar, entender).
- Ser vs Estar: Core distinctions between traits and temporary states/locations.
- Preterite Tense: Regular -ar, -er, -ir verbs and high-frequency irregulars (fui, estuve).
- Imperfect Tense, basic commands, and direct/indirect object pronoun structures.
{vocab_context}

Please structure the workout beautifully as follows:
1. **Warm-up**: 3 quick conjugations or small exercises based on their level.
2. **Translation Challenge**: 3 English sentences to translate into Spanish using their grammar.
3. **Short Reading Passage**: A short paragraph (4-5 sentences) written in natural Spanish utilizing these rules, followed by 2 reading comprehension questions.
4. **Answer Key**: Place the full answer key at the very bottom with a clear spoiler separation line so they don't see it immediately.

Keep instructions in English and keep markdown styling simple so it reads perfectly in a standard text email.
"""

data = {
    "contents": [{
        "parts": [{"text": prompt}]
    }]
}

print("Calling Gemini API...")
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
    print(f"Error calling Gemini API: {e}")
    exit(1)

# 4. Format and send the email
msg = MIMEMultipart()
msg['From'] = email_user
msg['To'] = email_user  
msg['Subject'] = "Your Daily Spanish Workout 🇪🇸"
msg.attach(MIMEText(workout_text, 'plain'))

print("Sending email...")
try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email_user, email_password)
    server.sendmail(email_user, email_user, msg.as_string())
    server.close()
    print("Success! Your daily Spanish workout has been emailed.")
except Exception as e:
    print(f"Error sending email: {e}")
    exit(1)
