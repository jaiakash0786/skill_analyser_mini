import json

from resume_reader import read_resume
from resume_parser import parse_resume_with_llm
from services.skill_normalizer import normalize_skills
from rag_engine_v2 import MetadataRAGEngine

from ats_evaluator import evaluate_ats
from learning_path_generator import generate_learning_path
from role_detector import detect_roles
from pathlib import Path

# Import your existing AI pipeline entry
from resume_reader import read_resume
from resume_parser import parse_resume_with_llm
from services.skill_normalizer import normalize_skills
from rag_engine_v2 import MetadataRAGEngine
from role_detector import detect_roles
from ats_evaluator import evaluate_ats
from learning_path_generator import generate_learning_path


def run_pipeline(resume_path: str, target_domain: str = "Web Development"):
    rag = MetadataRAGEngine()

    resume_text = read_resume(resume_path)
    parsed_resume = parse_resume_with_llm(resume_text)
    parsed_resume["skills"] = normalize_skills(parsed_resume.get("skills", []))

    role_context = rag.retrieve(
        query="job roles and required skills",
        doc_types=["roles"],
        top_k=5
    )

    roles = detect_roles(parsed_resume, role_context)

    top_role = roles[0]["role"]
    role_key = top_role.lower().replace(" ", "_")
    domain_key = target_domain.lower().replace(" ", "_")

    rag_context = rag.retrieve(
        query=f"{top_role} {target_domain} ATS requirements",
        role=role_key,
        domain=domain_key,
        doc_types=["roles", "domains", "ats"],
        top_k=5
    )

    ats = evaluate_ats(
        resume_data=parsed_resume,
        rag_context=rag_context,
        target_role=f"{top_role} ({target_domain})"
    )

    learning = None
    if ats.get("missing_skills"):
        learning_ctx = rag.retrieve(
            query=" ".join(ats["missing_skills"]),
            doc_types=["skills", "learning"],
            top_k=5
        )
        learning = generate_learning_path(
            ats["missing_skills"],
            learning_ctx,
            f"{top_role} ({target_domain})"
        )

    return {
        "roles": roles,
        "ats": ats,
        "learning_path": learning
    }
