import os
from google import genai


def main():
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found")

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents="Say hello and confirm that the API is working."
    )

    print("\nGemini Response:\n")
    print(response.text)


if __name__ == "__main__":
    main()

