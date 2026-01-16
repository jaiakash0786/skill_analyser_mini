import json
import re
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def _clean_json(text):
    text = re.sub(r"```json|```", "", text).strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else text


def generate_learning_path(
    missing_skills: list[str],
    rag_context: list[str],
    target_role: str
):
    context = "\n\n".join(rag_context)

    prompt = f"""
You are an AI Career Planner.

TARGET ROLE:
{target_role}

MISSING SKILLS:
{missing_skills}

RETRIEVED LEARNING KNOWLEDGE (USE ONLY THIS):
{context}

TASK:
Create a personalized learning roadmap.

Return ONLY valid JSON in this format:

{{
  "timeline": "",
  "learning_path": [
    {{
      "skill": "",
      "level": "",
      "focus_topics": [],
      "projects": []
    }}
  ]
}}

RULES:
- Do NOT invent resources
- Use only retrieved knowledge
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
            "error": "Learning path JSON parsing failed",
            "raw_response": raw
        }
