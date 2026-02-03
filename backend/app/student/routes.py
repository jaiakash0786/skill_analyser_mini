from fastapi import APIRouter, Depends, UploadFile, File
import os
import shutil
from sqlalchemy.orm import Session

from backend.app.auth.dependencies import get_current_user
from backend.app.db.database import SessionLocal
from backend.app.models.resume import Resume
from backend.app.models.user import User
from backend.app.models.analysis import AnalysisResult
from backend.app.services.pipeline import run_pipeline


router = APIRouter(
    prefix="/student",
    tags=["student"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/resume/upload")
def upload_resume(
    resume: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # ---------- Save file ----------
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, resume.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(resume.file, buffer)

    # ---------- Get user ----------
    db_user = db.query(User).filter(
        User.email == current_user["sub"]
    ).first()

    if not db_user:
        return {"error": "User not found"}

    # ---------- Save resume ----------
    new_resume = Resume(
        user_id=db_user.id,
        file_path=file_path,
        original_filename=resume.filename
    )

    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)

    # 🔥 CLOSE DB SESSION BEFORE PIPELINE
    db.close()

    # ---------- Run AI pipeline (NO DB HERE) ----------
    ai_result = run_pipeline(
        resume_path=file_path,
        target_domain="Web Development"
    )

    # ---------- NEW DB SESSION ----------
    db = SessionLocal()

    analysis = AnalysisResult(
        resume_id=new_resume.id,
        result=ai_result
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    db.close()

    return {
        "message": "Resume uploaded and analyzed successfully",
        "resume_id": new_resume.id,
        "analysis_id": analysis.id,
        "analysis": ai_result
    }
