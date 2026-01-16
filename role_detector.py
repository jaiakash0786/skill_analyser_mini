import json
import re
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def _clean_json(text):
    text = re.sub(r"```json|```", "", text).strip()
    match = re.search(r"\[.*\]", text, re.DOTALL)
    return match.group(0) if match else text


def detect_roles(resume_data: dict, rag_context: list[str]):
    context = "\n\n".join(rag_context)

    prompt = f"""
You are a career role inference engine.

ROLE DEFINITIONS (USE ONLY THIS):
{context}

CANDIDATE DATA:
{json.dumps(resume_data, indent=2)}

TASK:
Infer suitable job roles for this candidate.

Return ONLY valid JSON array sorted by confidence DESC:

[
  {{
    "role": "",
    "confidence": 0.0,
    "reason": ""
  }}
]

RULES:
- Confidence must be between 0 and 1
- Do NOT invent roles
- Base reasoning on skills and projects
- No explanation outside JSON
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    raw = response.choices[0].message.content
    cleaned = _clean_json(raw)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {
            "error": "Role detection JSON parsing failed",
            "raw_response": raw
        }
