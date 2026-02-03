from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

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
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Ensure recruiter
    if current_user.get("role") != "recruiter":
        return {"error": "Access denied"}

    results = []

    resumes = db.query(Resume).all()

    for resume in resumes:
        user = db.query(User).filter(User.id == resume.user_id).first()
        analysis = db.query(AnalysisResult).filter(
            AnalysisResult.resume_id == resume.id
        ).first()

        ats_score = None
        if analysis and analysis.result.get("ats"):
            ats_score = analysis.result["ats"].get("ats_score")


        results.append({
            "candidate_email": user.email if user else None,
            "resume_id": resume.id,
            "filename": resume.original_filename,
            "ats_score": ats_score
        })

    return results
