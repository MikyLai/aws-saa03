import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise SystemExit(
        "Error: OPENAI_API_KEY environment variable is not set.\n"
        "Please set it via:\n"
        "  export OPENAI_API_KEY='your-api-key'\n"
        "  or add OPENAI_API_KEY=your-api-key to your .env file"
    )
QUESTION_API_URL = os.getenv("QUESTION_API_URL", "http://localhost:8000/questions/")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")

INPUT_FILE = Path("data/questions.json")
OUTPUT_FILE = Path("data/questions_bilingual.json")

client = OpenAI(api_key=OPENAI_API_KEY)


def translate_question(question: dict) -> dict:
    system_prompt = """
    You are translating AWS certification practice questions into Traditional Chinese.

    Rules:
    1. Return valid JSON only.
    2. Keep the exact same structure and field names.
    3. Do not change answers.
    4. Do not change labels.
    5. Keep AWS service names in English where appropriate.
    6. Translate:
    - stem_en -> stem_zh
    - explanation_en -> explanation_zh
    - choices[].text_en -> choices[].text_zh
    7. Do NOT rename fields.
    8. Keep choices[].text_en unchanged.
    9. Each choice in output must contain:
    - label
    - text_en
    - text_zh
    10. Do not include markdown or explanations.
    11. The output must be parseable by json.loads().
    """

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": json.dumps(question, ensure_ascii=False),
            },
        ],
    )

    text = response.output_text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as err:
        raise ValueError(f"Failed to parse model response as JSON.\nRaw output:\n{text}") from err


def import_question(payload: dict) -> requests.Response:
    return requests.post(
        QUESTION_API_URL,
        json=payload,
        timeout=60,
    )


def normalize_bilingual_payload(original_question: dict, translated_question: dict) -> dict:
    """
    Make sure the translated payload matches the API schema exactly.
    API expects:
      - stem_en, stem_zh
      - explanation_en, explanation_zh
      - choices[].label, text_en, text_zh
      - difficulty, domain, question_type, active, answers
    """
    normalized = {
        "stem_en": (original_question.get("stem_en") or original_question.get("stem")),
        "stem_zh": translated_question.get("stem_zh"),
        "explanation_en": (
            original_question.get("explanation_en") or original_question.get("explanation")
        ),
        "explanation_zh": translated_question.get("explanation_zh"),
        "difficulty": original_question.get("difficulty", 1),
        "domain": original_question.get("domain"),
        "question_type": original_question.get("question_type", "single"),
        "active": original_question.get("active", True),
        "choices": [],
        "answers": original_question.get("answers", []),
    }

    original_choices = original_question.get("choices", [])
    translated_choices = translated_question.get("choices", [])

    if len(original_choices) != len(translated_choices):
        raise ValueError(
            f"Choice count mismatch: original={len(original_choices)},"
            f" translated={len(translated_choices)}"
        )

    for orig, trans in zip(original_choices, translated_choices, strict=True):
        normalized["choices"].append(
            {
                "label": orig["label"],
                "text_en": orig.get("text_en") or orig.get("text"),
                "text_zh": trans.get("text_zh") or trans.get("text"),
            }
        )

    return normalized


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    with open(INPUT_FILE, encoding="utf-8") as f:
        questions = json.load(f)

    if not isinstance(questions, list):
        raise ValueError("Input JSON must be a list of questions.")

    bilingual_questions: list[dict] = []

    for idx, q in enumerate(questions, start=1):
        print(f"[{idx}/{len(questions)}] Processing question: {q['stem_en'][:60]}...")

        try:
            translated_payload = translate_question(q)
            bilingual_payload = normalize_bilingual_payload(q, translated_payload)
        except Exception as e:
            print(f"[{idx}] Translation failed: {e}")
            raise

        bilingual_questions.append(bilingual_payload)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(bilingual_questions, f, ensure_ascii=False, indent=2)

        try:
            response = import_question(bilingual_payload)
        except Exception as e:
            print(f"[{idx}] API request failed: {e}")
            raise

        print(f"[{idx}] API status: {response.status_code}")

        if response.status_code == 409:
            print(f"[{idx}] Skipped (duplicate)")
            continue

        if response.status_code >= 400:
            print(f"[{idx}] API error response:")
            print(response.text)
            raise RuntimeError(f"Failed to import question #{idx}")

    print(f"Done. Saved bilingual payloads to {OUTPUT_FILE}")


if __name__ == "__main__":
    # main()
    INPUT_FILE = Path("data/question_bilingual_25-65.json")
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    with open(INPUT_FILE, encoding="utf-8") as f:
        questions = json.load(f)

    for idx, question in enumerate(questions, start=1):
        print(f"[{idx}/{len(questions)}] Processing question: {question['stem_en'][:60]}...")
        try:
            response = import_question(question)
        except Exception as e:
            print(f"[{idx}] API request failed: {e}")
            raise

        print(f"[{idx}] API status: {response.status_code}")

        if response.status_code == 409:
            print(f"[{idx}] Skipped (duplicate)")
            continue

        if response.status_code >= 400:
            print(f"[{idx}] API error response:")
            print(response.text)
            raise RuntimeError(f"Failed to import question #{idx}")

    print(f"Done. Saved bilingual payloads to {OUTPUT_FILE}")
