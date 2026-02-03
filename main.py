import json

from resume_reader import read_resume
from resume_parser import parse_resume_with_llm
from services.skill_normalizer import normalize_skills
from rag_engine_v2 import MetadataRAGEngine

from ats_evaluator import evaluate_ats
from learning_path_generator import generate_learning_path
from role_detector import detect_roles




# ================= CONFIG =================
RESUME_PATH = "resumes/resume_0863.pdf"

TARGET_ROLE = "backend Engineer"
TARGET_DOMAIN = "Web Development"
ROLE_KEY = TARGET_ROLE.lower().replace(" ", "_")
DOMAIN_KEY = TARGET_DOMAIN.lower().replace(" ", "_")

# =========================================

def pretty_print(data, indent=0):
    space = "  " * indent

    if isinstance(data, dict):
        for key, value in data.items():
            print(f"{space}{key.upper()}:")
            pretty_print(value, indent + 1)

    elif isinstance(data, list):
        for item in data:
            pretty_print(item, indent)

    else:
        print(f"{space}{data}")


def main():
    print("\n========== STEP 1: READ RESUME ==========\n")
    resume_text = read_resume(RESUME_PATH)

    print("Resume loaded successfully.")

    # -------------------------------------------------

    print("\n========== STEP 2: PARSE RESUME (LLM) ==========\n")
    parsed_resume = parse_resume_with_llm(resume_text)

    if "error" in parsed_resume:
        print("Resume parsing failed.")
        print(parsed_resume)
        return
    pretty_print(parsed_resume)
    print("Resume parsed successfully.")

    # -------------------------------------------------

    print("\n========== STEP 3: NORMALIZE SKILLS ==========\n")
    parsed_resume["skills"] = normalize_skills(
        parsed_resume.get("skills", [])
    )

    print("Normalized Skills:")
    print(parsed_resume["skills"])

    # -------------------------------------------------

    print("\n========== STEP 4: RAG RETRIEVAL ==========\n")
    rag = MetadataRAGEngine()

    rag_context = rag.retrieve(
    query=f"{TARGET_ROLE} {TARGET_DOMAIN} ATS requirements",
    role=ROLE_KEY,
    domain=DOMAIN_KEY,
    doc_types=["roles", "domains", "ats"],
    top_k=7
)



    print(f"Retrieved {len(rag_context)} RAG context chunks.")

    # -------------------------------------------------

    print("\n========== STEP 5: ATS EVALUATION ==========\n")
    ats_report = evaluate_ats(
        resume_data=parsed_resume,
        rag_context=rag_context,
        target_role=f"{TARGET_ROLE} ({TARGET_DOMAIN})"
    )

    if "error" in ats_report:
        print("ATS evaluation failed.")
        print(ats_report)
        return

    print("\n----- ATS REPORT -----\n")
    print(json.dumps(ats_report, indent=4))

    # -------------------------------------------------

    print("\n========== STEP 6: LEARNING PATH GENERATION ==========\n")
    missing_skills = ats_report.get("missing_skills", [])

    if not missing_skills:
        print("No missing skills detected. Learning path not required.")
        return

    learning_rag_context = rag.retrieve(
    query=" ".join(missing_skills),
    doc_types=["skills", "learning"],
    top_k=5
)


    learning_path = generate_learning_path(
        missing_skills=missing_skills,
        rag_context=learning_rag_context,
        target_role=f"{TARGET_ROLE} ({TARGET_DOMAIN})"
    )

    if "error" in learning_path:
        print("Learning path generation failed.")
        print(learning_path)
        return

    print("\n----- PERSONALIZED LEARNING PATH -----\n")
    print(json.dumps(learning_path, indent=4))
        # -------------------------------------------------

    print("\n========== ROLE SUGGESTIONS (AI-INFERRED) ==========\n")

    role_rag_context = rag.retrieve(
        query="job roles and required skills",
        doc_types=["roles"],
        top_k=10
    )

    role_suggestions = detect_roles(
        resume_data=parsed_resume,
        rag_context=role_rag_context
    )

    if "error" in role_suggestions:
        print("Role suggestion failed.")
        print(role_suggestions)
    else:
        for r in role_suggestions:
            print(f"{r['role']}  | confidence: {r['confidence']}")

    print("\n========== PIPELINE COMPLETED SUCCESSFULLY ==========\n")


if __name__ == "__main__":
    main()
