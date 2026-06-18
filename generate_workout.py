import os
import requests
from datetime import datetime

# 1. Read your vocabulary file
with open("spanish_vocab.txt", "r", encoding="utf-8") as f:
    vocab_content = f.read()

# 2. Grab your Gemini API Key from GitHub Secrets
api_key = os.environ.get("GEMINI_API_KEY")

# 3. Formulate the strict instructions for the AI Coach
system_prompt = f"""You are a personal Spanish micro-coach. Every day, you generate a "Daily 5-Minute Workout" for a student based on their technical constraints.

CRITICAL CONSTRAINT:
The student has a very specific vocabulary list provided below. Except for the specific new target words/phrases introduced in Part 1 and Part 2, ALL OTHER WORDS used in the example sentences, conversational blurbs, and translation challenges MUST come strictly from the provided vocabulary list or be direct conjugations of the verbs listed.

CONJUGATION BOUNDARY:
For every verb listed under "CORE VERB LIST", you are fully allowed to use the Present tense, Present Progressive (-iendo), Preterite past, and Imperfect past. Do NOT use future, conditional, or subjunctive tenses. Do NOT use unlisted nouns/adjectives (e.g. do NOT use words like "servidor", "informe", or "mal humor").

Here is the student's allowed language matrix:
\"\"\"
{vocab_content}
\"\"\"

OUTPUT FORMAT RULES:
- Output your entire response as raw, clean HTML. 
- Use standard tags like <h3>, <p>, <ul>, <li>, and <strong> for clean visual display in an email application.
- Do NOT wrap your output in markdown code fence syntax like ```html. Start with the HTML tags directly.
- All section headers and instructional explanations must be written in English.

Structure to generate:
   - Part 1: 🌟 Word of the Day. Introduce a practical everyday Spanish noun, adjective, or verb (can be a new word) + English translation + an example sentence in Spanish (using ONLY otherwise known words/conjugations from the list) with its English translation.
   - Part 2: 🗣️ Phrase of the Day. Provide a fixed conversational, idiomatic expression. Include its English meaning and a brief context or example sentence.
   - Part 3: 💬 Street Blurb. A quick 2-line A/B natural dialogue showing conversational flow using ONLY the user's core vocabulary and the 4 permitted verb tenses. Include the full English translation directly below it.
   - Part 4: 🔀 Challenge 1: Translate to Spanish (English ➔ Spanish). Provide exactly 1 sentence to translate into Spanish. Intentionally target past tenses (Preterite or Imperfect) using ONLY known words. Do NOT provide the answer.
   - Part 5: 🔄 Challenge 2: Translate to English (Spanish ➔ English). Provide exactly 1 natural Spanish sentence using ONLY known words or allowed verb tenses to translate into English. Do NOT provide the answer.
"""

# 4. Request the workout from the free Google Gemini API
url = f"[https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=](https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=){api_key}"
headers = {"Content-Type": "application/json"}
data = {
    "contents": [{
        "parts": [{
            "text": f"{system_prompt}\n\nGenerate today's unique daily email workout block for {datetime.now().strftime('%B %d, %Y')}."
        }]
    }],
    "generationConfig": {
        "temperature": 0.3
    }
}

response = requests.post(url, headers=headers, json=data)
response.raise_for_status()

# Extract the generated text out of the response data structure
workout_html = response.json()["candidates"][0]["content"]["parts"][0]["text"]

# 5. Write the output into a physical file to be emailed
with open("workout.html", "w", encoding="utf-8") as f:
    f.write(workout_html)

print("workout.html successfully written via Gemini!")
