import os
import json
from pathlib import Path

import pandas as pd
from google import genai

from src.indexing.vector_index import VectorIndex

print("process started")
# ------------------------
# Paths
# ------------------------

VECTOR_STORE_DIR = Path("index/vector_store")
OUTPUT_FILE = Path("output/heor_extraction.xlsx")


# ------------------------
# Excel Columns (Schema)
# ------------------------

FIELDS = [

    "Study name",
    "Title",
    "Literature classification (Journal Articles, HTA)",
    "Publication year",
    "Country",
    "Objective",
    "Intervention Type",
    "PDF",
    "Location",
    "Intervention",
    "Comparators",
    "Perspective of the model",
    "Economic analysis type",
    "Model structure",
    "Health states used in model structure",
    "Time horizon",
    "Cycle length",
    "Discount rate (%) Benefits",
    "Discount rate (%) Cost",
    "Result - cost-effective? (Yes / No)",
    "Is uncertainty analysis conducted? If yes, then what type?",
    "Model critiques"
]


# ------------------------
# LLM Prompt
# ------------------------

SYSTEM_PROMPT = """
You are a Health Economics and Outcomes Research (HEOR) analyst.

Your task is to extract structured information from medical and economic evaluation papers.

Rules:
- Use ONLY the provided context.
- Do NOT guess.
- If information is missing, write "NA".
- Extract exact values from the text.
- Return VALID JSON.
- Keys must exactly match the field names.

"""


# ------------------------
# Helpers
# ------------------------

def build_context(chunks, max_chars=6500):

    parts = []
    total = 0

    for ch in chunks:

        part = f"[Pages {ch['pages']}]\n{ch['text']}\n\n"

        if total + len(part) > max_chars:
            break

        parts.append(part)
        total += len(part)

    return "".join(parts)


def extract_fields(client, context):

    fields_list = "\n".join([f'- "{f}"' for f in FIELDS])

    prompt = f"""
{SYSTEM_PROMPT}

IMPORTANT:
Return ONLY valid JSON.
Do NOT include explanations.
Do NOT include markdown.
Do NOT include code blocks.

Context:
{context}

Extract the following fields:

{fields_list}

Return a JSON object with exactly these keys.
"""

    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=prompt
    )

    text = response.text.strip()

    # -------- Clean common wrappers --------

    # Remove markdown ```json ``` wrappers
    if text.startswith("```"):
        text = text.strip("`")
        text = text.replace("json", "").strip()

    # Try to isolate JSON object
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:
        text = text[start:end + 1]

    # -------- Parse JSON --------

    try:
        data = json.loads(text)
    except Exception:
        print("\n----- RAW LLM OUTPUT -----\n")
        print(response.text)
        print("\n--------------------------\n")

        raise ValueError("LLM did not return valid JSON")

    return data

print("enetring main")
# ------------------------
# Main
# ------------------------

def main():
    print("entered main")

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("GOOGLE_API_KEY not set")

    client = genai.Client(api_key=api_key)

    # Load vector index (current PDF only)
    vector_index = VectorIndex()

    index_path = VECTOR_STORE_DIR / "faiss.index"
    metadata_path = VECTOR_STORE_DIR / "metadata.json"

    vector_index.load(index_path, metadata_path)

    print("Index loaded")

    # Query for extraction
    query = """
economic evaluation model cost effectiveness
intervention comparator perspective outcome discount rate
"""

    # Retrieve relevant chunks
    results = vector_index.search(query, top_k=12)

    if not results:
        raise ValueError("No context retrieved")

    context = build_context(results)

    print("Context prepared")

    # Extract fields
    print("Extracting fields...")

    data = extract_fields(client, context)

    # Normalize row
    row = {}

    for field in FIELDS:
        row[field] = data.get(field, "NA")

    # Get PDF name from metadata
    if results and "source_file" in results[0]:
        row["PDF"] = results[0]["source_file"].replace(".txt", ".pdf")
    else:
        row["PDF"] = "Unknown"

    # Ensure output dir exists
    OUTPUT_FILE.parent.mkdir(exist_ok=True)

    # Append to existing Excel (always)
    if OUTPUT_FILE.exists():

        df_old = pd.read_excel(OUTPUT_FILE)

        df_new = pd.DataFrame([row])

        df = pd.concat([df_old, df_new], ignore_index=True)

    else:
        df = pd.DataFrame([row])

    df.to_excel(OUTPUT_FILE, index=False)

    print("\nExtraction appended to Excel")
    print("Saved to:", OUTPUT_FILE.resolve())
if __name__ == "__main__":
    main()