import os
import json
import time
from google import genai
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional, List


load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

client = genai.Client(api_key=api_key)


class Meta(BaseModel):
    language_detected: str
    focus_requested: str
    review_confidence: str = Field(description="high | medium | low")
    lines_reviewed: int


class Verdict(BaseModel):
    headline: str
    severity: str = Field(description="high | medium | low | clean")
    ship_ready: bool
    one_liner: str


class Finding(BaseModel):
    id: int
    severity: str = Field(description="high | medium | low")
    category: str
    line: Optional[str] = None
    title: str
    what: str
    why_it_matters: str
    suggestion: str
    code_before: Optional[str] = None
    code_after: Optional[str] = None
    references: List[str] = []


class ImprovedCode(BaseModel):
    language: str
    content: str
    notes: str


class Review(BaseModel):
    meta: Meta
    verdict: Verdict
    findings: List[Finding]
    strengths: List[str]
    improved_code: Optional[ImprovedCode] = None
    followup_questions: List[str]


SYSTEM_PROMPT = """You are a senior software engineer performing a code review.

Rules:
- Be specific. Point to line numbers when possible.
- For every finding, explain WHY it matters (consequence, not just description).
- If focus is unclear or gibberish, set review_confidence to "low" and add a followup_question asking for clarification.
- Only report real issues. Do not invent problems to fill space.
- Include at least 1 genuine strength if the code has any.
- Return findings sorted by severity (high first).
- If the code is clean, findings can be empty and severity should be "clean".
- ship_ready = true only if there are no high or medium severity findings.
- If no code is provided, set lines_reviewed to 0 and add a followup question asking for code.
"""

# Fallback chain — ordered from most-preferred to last-resort
MODEL_CHAIN = [
    "gemini-flash-latest",
    "gemini-3.5-flash",
    "gemini-3.7-flash",
    "gemini-3.8-flash",
    "gemini-pro-latest",
]


def _try_model(model_name, user_prompt, max_attempts=2):
    """Try a single model with N quick retries. Returns parsed Review or None."""
    for attempt in range(max_attempts):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=user_prompt,
                config={
                    "system_instruction": SYSTEM_PROMPT,
                    "response_mime_type": "application/json",
                    "response_schema": Review,
                },
            )
            print(f"[OK] Reviewed using: {model_name}")
            return response.parsed
        except Exception as e:
            err_name = type(e).__name__
            print(f"[FAIL] {model_name} attempt {attempt+1}: {err_name}")
            if attempt < max_attempts - 1:
                time.sleep(2)
    return None


def review_code(code: str, language: str, focus: str) -> Review:
    if not code or not code.strip():
        raise ValueError("Code is empty. Please provide code to review.")

    user_prompt = (
        f"Language: {language}\n"
        f"Focus: {focus}\n\n"
        f"Here is the code to review:\n\n"
        f"{code}\n\n"
        f"Review the code above according to the focus and rules."
    )

    for model_name in MODEL_CHAIN:
        result = _try_model(model_name, user_prompt)
        if result is not None:
            return result

    raise RuntimeError(
        "All models in the fallback chain failed. "
        "This usually means Google's API is having a bad day. Try again in a few minutes."
    )


if __name__ == "__main__":
    sample_code = (
        "counter = 0\n"
        "\n"
        "def increment():\n"
        "    global counter\n"
        "    counter = counter + 1\n"
        "\n"
        "def divide(a, b):\n"
        "    return a / b\n"
        "\n"
        "password = 'admin123'\n"
    )

    result = review_code(
        code=sample_code,
        language="python",
        focus="check thread safety, error handling, and any security issues"
    )

    print(json.dumps(result.model_dump(), indent=2))
