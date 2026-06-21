import os
import google.generativeai as genai

# 1. Configure the Gemini API using your GitHub Secrets Token
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# 2. Try to read yesterday's workout file so the AI has context for the review
previous_workout_content = "No previous workout found."
if os.path.exists("workout.md"):
    with open("workout.md", "r", encoding="utf-8") as f:
        previous_workout_content = f.read()

# 3. Initialize the model
model = genai.GenerativeModel('gemini-1.5-flash')

# 4. Strict instruction prompt forcing BOTH the target items and their examples
prompt = f"""
You are an expert personal Spanish language tutor. Your job is to generate a customized Daily Spanish Workout based on the user's current knowledge and yesterday's layout.

CRITICAL ASSIGNMENT FOR THE REVIEW SECTION:
Look closely at yesterday's workout content provided below. You must extract the exact "Target Word" and "Target Phrase" that were taught, along with the example sentences they were used in. You must list them explicitly in the 'Repaso de Ayer' section following the exact formatting tags.

Here is yesterday's workout content:
\"\"\"
{previous_workout_content}
\"\"\"

CRITICAL LAYOUT RULES:
Output your entire response in clean Markdown. Do not include any intro conversational filler (like "Sure, here is your workout") or outro notes. Start immediately with the title header.

Follow this EXACT template structure:

# 🏋️‍♂️ Daily Spanish Workout

## 🔄 Repaso de Ayer (Yesterday's Review)
* **Palabra Anterior (Previous Word):** [Extract and insert the exact target vocabulary word from yesterday here]
    * *Ejemplo de ayer:* [Insert the exact sentence that word was used in yesterday]
* **Frase Anterior (Previous Phrase):** [Extract and insert the exact target phrase/idiom from yesterday here]
    * *Ejemplo de ayer:* [Insert the exact sentence that phrase was used in yesterday]

## 🧠 Vocabulario de Hoy (Today's New Word)
* **Palabra Nueva (New Word):** [Insert one new intermediate/advanced Spanish word]
* **Significado (Meaning):** [English definition]
* **Ejemplo de Hoy (Today's Example Sentence):** [A practical Spanish sentence using this new word]
* **Traducción (Translation):** [English translation of today's example sentence]

## 🗣️ Frase de Hoy (Today's New Phrase)
* **Frase Nueva (New Phrase):** [Insert one natural, useful everyday Spanish phrase or idiom]
* **Significado (Meaning):** [English definition]
* **Ejemplo de Hoy (Today's Example Sentence):** [A practical Spanish sentence using this new phrase]
* **Traducción (Translation):** [English translation of today's example sentence]

## 📝 Práctica (Your Turn!)
[Provide 2 brief translation exercises or open-ended prompts testing today's new word and phrase]
"""

# 5. Generate the content
response = model.generate_content(prompt)

# 6. Save today's updated workout over the old one
with open("workout.md", "w", encoding="utf-8") as f:
    f.write(response.text)

print("Workout updated successfully with explicit word and phrase review tracking!")
