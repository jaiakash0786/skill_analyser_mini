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
    # Remove duplicates
    unique_skills = []
    for skill in missing_skills:
        if skill not in unique_skills:
            unique_skills.append(skill)
    
    # Format RAG context for better LLM understanding
    formatted_context = ""
    if rag_context and len(rag_context) > 0:
        for i, chunk in enumerate(rag_context, 1):
            formatted_context += f"\n--- Learning Resource {i} ---\n{chunk}\n"
    else:
        # If no RAG context, provide a helpful instruction to the LLM
        formatted_context = "\n--- No specific learning resources found. Use your general knowledge about software development learning paths. ---\n"

    # Create a more detailed prompt with examples
    prompt = f"""You are an expert technical mentor creating personalized learning paths.

TARGET ROLE: {target_role}

MISSING SKILLS TO LEARN (in order of priority):
{json.dumps(unique_skills, indent=2)}

LEARNING RESOURCES (use these as reference if relevant):
{formatted_context}

TASK:
Create a detailed, practical learning roadmap for each missing skill.

For EACH skill in the missing skills list, provide:
1. **skill**: The exact skill name
2. **level**: One of ["Beginner", "Intermediate", "Advanced"] based on complexity
3. **focus_topics**: 4-6 specific, actionable topics to study (be detailed)
4. **projects**: 2-3 practical, portfolio-worthy projects that demonstrate mastery

EXAMPLE FORMAT:
{{
  "skill": "Docker",
  "level": "Intermediate",
  "focus_topics": [
    "Dockerfile optimization and multi-stage builds",
    "Docker Compose for multi-container applications",
    "Container networking and communication",
    "Volume management for persistent data",
    "Docker security best practices"
  ],
  "projects": [
    "Containerize a MERN stack application with Docker Compose",
    "Build a CI/CD pipeline that builds and pushes Docker images",
    "Create a development environment with hot-reload using Docker"
  ]
}}

EXAMPLE FORMAT 2:
{{
  "skill": "REST APIs",
  "level": "Beginner",
  "focus_topics": [
    "HTTP methods (GET, POST, PUT, DELETE)",
    "Status codes and error handling",
    "API endpoint design best practices",
    "Request/response formats (JSON, XML)",
    "Authentication methods (JWT, OAuth)"
  ],
  "projects": [
    "Build a RESTful API for a blog platform",
    "Create a task management API with proper error handling",
    "Document your API using Swagger/OpenAPI"
  ]
}}

RULES:
- Be specific and practical - avoid vague topics
- Projects should be realistic and showcase the skill
- If learning resources provide specific information, prioritize that
- If no resources are available, use your expertise to create high-quality content
- Return ONLY valid JSON, no other text

The response MUST be a JSON object with this structure:
{{
  "timeline": "Estimated completion timeline (e.g., '3-4 months')",
  "learning_path": [array of skill objects as shown above]
}}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # You can also try "mixtral-8x7b-32768" for better results
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # Slight creativity for better project ideas
            max_tokens=4000   # Ensure enough tokens for detailed response
        )

        raw = response.choices[0].message.content
        cleaned = _clean_json(raw)
        
        result = json.loads(cleaned)
        
        # Validate the structure
        if "learning_path" not in result:
            result["learning_path"] = []
        
        # Ensure each skill has the required fields
        for item in result.get("learning_path", []):
            if "skill" not in item:
                continue
            if "level" not in item:
                item["level"] = "Beginner"
            if "focus_topics" not in item or not item["focus_topics"]:
                item["focus_topics"] = [f"Core concepts of {item['skill']}", f"Practical applications", f"Best practices"]
            if "projects" not in item or not item["projects"]:
                item["projects"] = [f"Build a project using {item['skill']}"]
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        print(f"Raw response: {raw[:500]}...")
        return {
            "timeline": "3-4 months",
            "learning_path": [
                {
                    "skill": skill,
                    "level": "Beginner",
                    "focus_topics": [f"Core concepts of {skill}", f"Practical applications", f"Best practices", f"Tools and technologies"],
                    "projects": [f"Build a basic {skill} project", f"Create a portfolio piece using {skill}"]
                }
                for skill in unique_skills[:5]  # Limit to top 5 in case of error
            ]
        }
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {
            "timeline": "3-4 months",
            "learning_path": [
                {
                    "skill": skill,
                    "level": "Beginner",
                    "focus_topics": [f"Introduction to {skill}", f"Core concepts", f"Hands-on practice"],
                    "projects": [f"Simple {skill} project"]
                }
                for skill in unique_skills[:3]
            ]
        }