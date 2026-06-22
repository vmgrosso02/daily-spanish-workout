import os
from google import genai

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

prompt = """
You are my Spanish tutor. Create a daily lesson. You MUST follow this exact 5-part structure:
1. Grammar Review: A clear, concise explanation of one grammar rule.
2. Vocabulary: 5 new words with Spanish-to-English translations.
3. Sentences: 5 sentences to translate from English to Spanish.
4. Reading Passage: A short paragraph in Spanish.
5. Comprehension Question: One question based on the passage above.
Use Markdown headers (##) for each section.
"""

response = client.models.generate_content(
    model='gemini-2.0-flash',
    contents=prompt,
)

with open("workout.md", "w", encoding="utf-8") as f:
    f.write(response.text)
