import os
from google import genai

def generate_workout():
    # 1. Fetch the API key safely from environment secrets
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")

    # 2. Initialize the modern Google GenAI Client
    client = genai.Client(api_key=api_key)

    # 3. Request your tailored daily review
    prompt = (
        "You are my personal Spanish tutor. Based on my existing knowledge base of verbs, "
        "tenses, and vocabulary, generate a comprehensive daily workout. Include a short "
        "grammar review, 5 vocabulary flashcard pairs, 5 sentence translations (English to Spanish), "
        "and a brief reading comprehension passage with a question. Keep the layout highly structured."
    )

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )

    # 4. Save the response exactly as markdown text
    with open("workout.md", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("Workout successfully generated and saved to workout.md!")

if __name__ == "__main__":
    generate_workout()
