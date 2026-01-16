import os
import re
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise RuntimeError("GROQ_API_KEY not found in .env")

client = Groq(api_key=API_KEY)


def _clean_llm_json(content: str):
    content = content.strip()
    content = re.sub(r"```json|```", "", content).strip()

    match = re.search(r"\{.*\}", content, re.DOTALL)
    if match:
        content = match.group(0)

    return content


def parse_resume_with_llm(resume_text: str) -> dict:
    prompt = f"""
You are a Resume Parser.

Extract the following JSON structure ONLY:

{{
  "name": "",
  "summary": "",
  "location": "",
  "skills": [],
  "education": [
    {{
      "degree": "",
      "institution": "",
      "year": ""
    }}
  ],
  "experience": [],
  "projects": []
}}

Rules:
- Output ONLY valid JSON
- No explanation
- No markdown
- Leave missing fields empty

Resume Text:
{resume_text}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    raw_content = response.choices[0].message.content
    cleaned = _clean_llm_json(raw_content)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {
            "error": "Failed to parse JSON",
            "raw_response": raw_content
        }
