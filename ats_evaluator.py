import json
import re
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=API_KEY)


def _clean_json(content: str):
    # Remove markdown code blocks
    content = re.sub(r"```json|```", "", content)

    # Remove // comments
    content = re.sub(r"//.*", "", content)

    # Remove trailing commas
    content = re.sub(r",\s*([}\]])", r"\1", content)

    # Extract JSON object
    match = re.search(r"\{.*\}", content, re.DOTALL)
    return match.group(0).strip() if match else content.strip()


def evaluate_ats(resume_data: dict, rag_context: list[str], target_role: str):
    context_text = "\n\n".join(rag_context)

    prompt = f"""
You are an ATS evaluation engine.

TARGET ROLE:
{target_role}

RETRIEVED KNOWLEDGE (USE ONLY THIS):
{context_text}

CANDIDATE RESUME DATA:
{json.dumps(resume_data, indent=2)}

TASK:
Evaluate the resume strictly using the retrieved knowledge.

Return ONLY valid JSON in the following format:

{{
  "ats_score": 0,
  "matched_skills": [],
  "missing_skills": [],
  "strengths": [],
  "improvements": []
}}

RULES:
- Do NOT invent skills
- Do NOT use outside knowledge
- Score must be between 0 and 100
- No explanations outside JSON
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
            "error": "ATS JSON parsing failed",
            "raw_response": raw
        }
