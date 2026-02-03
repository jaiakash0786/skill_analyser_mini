from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from backend.app.db.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    file_path = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)

    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
