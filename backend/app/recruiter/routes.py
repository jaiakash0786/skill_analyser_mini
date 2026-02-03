from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from backend.app.auth.dependencies import get_current_user
from backend.app.db.database import SessionLocal
from backend.app.models.user import User
from backend.app.models.resume import Resume
from backend.app.models.analysis import AnalysisResult

router = APIRouter(
    prefix="/recruiter",
    tags=["recruiter"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/candidates")
def list_candidates(
    min_ats: Optional[int] = None,
    role: Optional[str] = None,
    skills: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.get("role") != "recruiter":
        raise HTTPException(status_code=403, detail="Access denied")

    requested_skills = []
    if skills:
        requested_skills = [
            s.strip().lower().replace('"', '').replace("'", "")
            for s in skills.split(",")
            if s.strip()
        ]

    results = []
    resumes = db.query(Resume).all()

    for resume in resumes:
        user = db.query(User).filter(User.id == resume.user_id).first()
        if not user:
            continue

        analysis = db.query(AnalysisResult)\
            .filter(AnalysisResult.resume_id == resume.id)\
            .first()

        ats_score = None
        candidate_role = None
        candidate_skills = []
        skill_match_count = 0

        if analysis:
            ats_score = analysis.result.get("ats", {}).get("ats_score")

            roles = analysis.result.get("roles", [])
            candidate_role = roles[0].get("role") if roles else None

            candidate_skills = analysis.result.get("ats", {}).get("matched_skills", [])
            normalized_candidate_skills = [
                s.strip().lower() for s in candidate_skills
            ]

            if requested_skills:
                skill_match_count = len(
                    set(requested_skills) & set(normalized_candidate_skills)
                )

        if min_ats is not None:
            if ats_score is None or ats_score < min_ats:
                continue

        if role is not None:
            if candidate_role is None or candidate_role.lower() != role.lower():
                continue

        if requested_skills and skill_match_count == 0:
            continue

        results.append({
            "candidate_email": user.email,
            "resume_id": resume.id,
            "filename": resume.original_filename,
            "ats_score": ats_score,
            "role": candidate_role,
            "skills": candidate_skills,
            "skill_match_count": skill_match_count
        })

    best_per_candidate = {}

    for item in results:
        email = item["candidate_email"]
        if email not in best_per_candidate:
            best_per_candidate[email] = item
        else:
            existing = best_per_candidate[email]
            if (
                item["skill_match_count"] > existing["skill_match_count"]
                or (
                    item["skill_match_count"] == existing["skill_match_count"]
                    and (item["ats_score"] or 0) > (existing["ats_score"] or 0)
                )
            ):
                best_per_candidate[email] = item

    final_results = list(best_per_candidate.values())

    return sorted(
        final_results,
        key=lambda x: (
            -x["skill_match_count"],
            x["ats_score"] is None,
            -(x["ats_score"] or 0)
        )
    )

@router.get("/resume/{resume_id}")
def get_candidate_analysis(
    resume_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.get("role") != "recruiter":
        raise HTTPException(status_code=403, detail="Access denied")

    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    user = db.query(User).filter(User.id == resume.user_id).first()

    analysis = db.query(AnalysisResult)\
        .filter(AnalysisResult.resume_id == resume.id)\
        .first()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return {
        "candidate_email": user.email if user else None,
        "resume_id": resume.id,
        "filename": resume.original_filename,
        "uploaded_at": resume.uploaded_at,
        "analysis": analysis.result
    }
