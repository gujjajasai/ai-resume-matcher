from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import json
import os
import pdfplumber
from collections import Counter
import uvicorn

from matcher import extract_text_from_pdf, extract_text_from_docx, extract_skills
from utils import calculate_similarity, extract_experience, ats_screening, semantic_search
from database import SessionLocal, engine, Base, Resume, Feedback

# Initialize Database
Base.metadata.create_all(bind=engine)

app = FastAPI()

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Allow only specific frontend origins
origins = ["http://localhost:3000", "https://yourfrontend.com"]  # Update frontend URL

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/match-resume/")
async def match_resume(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    db: Session = Depends(get_db)
):
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in ["pdf", "docx"]:
        raise HTTPException(status_code=400, detail="Unsupported file format")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    resume_text = extract_text_from_pdf(file_path) if file_ext == "pdf" else extract_text_from_docx(file_path)
    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="Failed to extract text from resume")

    ats_score, ats_feedback = ats_screening(resume_text)
    extracted_skills = extract_skills(resume_text)
    experience_years = extract_experience(resume_text)
    match_score = calculate_similarity(resume_text, job_description, extracted_skills, experience_years)
    job_ranking = semantic_search(resume_text, job_description)

    resume = Resume(
        filename=file.filename,
        skills=json.dumps(extracted_skills),
        experience_years=float(experience_years),
        match_score=match_score,
        job_ranking=job_ranking,
        ats_score=ats_score,
        ats_feedback=ats_feedback,
        job_description=job_description
    )

    db.add(resume)
    db.commit()
    db.refresh(resume)

    return {
        "filename": resume.filename,
        "skills": extracted_skills,
        "experience_years": resume.experience_years,
        "match_score": resume.match_score,
        "job_ranking": resume.job_ranking,
        "ats_score": resume.ats_score,
        "ats_feedback": resume.ats_feedback,
        "job_description": resume.job_description
    }

@app.post("/feedback/")
async def collect_feedback(
    filename: str,
    recruiter_rating: float,
    comments: str = None,
    db: Session = Depends(get_db)
):
    if not (0 <= recruiter_rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be between 0 and 5")

    resume = db.query(Resume).filter(Resume.filename == filename).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    feedback_entry = Feedback(filename=filename, rating=recruiter_rating, comments=comments)
    db.add(feedback_entry)
    db.commit()
    return {"message": "Feedback recorded successfully!"}

@app.get("/admin_dashboard/")
async def admin_dashboard(db: Session = Depends(get_db)):
    total_resumes = db.query(Resume).count()
    resumes = db.query(Resume).all()
    feedbacks = db.query(Feedback).all()

    avg_score = round(sum(r.match_score for r in resumes) / len(resumes), 2) if resumes else 0.0
    recruiter_avg_rating = round(sum(f.rating for f in feedbacks) / len(feedbacks), 2) if feedbacks else 0.0

    all_skills = [json.loads(r.skills) if r.skills else [] for r in resumes]
    flat_skills = [skill for sublist in all_skills for skill in sublist]
    top_skills = Counter(flat_skills).most_common(5) if flat_skills else []

    processed_resumes = [{
        "filename": r.filename,
        "match_score": r.match_score,
        "skills": json.loads(r.skills) if r.skills else []
    } for r in resumes]

    return {
        "total_resumes": total_resumes,
        "average_match_score": avg_score,
        "recruiter_average_rating": recruiter_avg_rating,
        "top_skills": top_skills,
        "feedback_count": len(feedbacks),
        "processed_resumes": processed_resumes,
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
