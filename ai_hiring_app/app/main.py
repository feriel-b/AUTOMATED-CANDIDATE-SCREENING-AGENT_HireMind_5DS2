print("--- RUNNING CLEANED main.py ---")

from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from pydantic import BaseModel
import re


import models
import schemas
import utils
from database import engine, get_db

print("--- DATABASE CONNECTION SUCCESSFUL ---")
models.Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------
# APP CONFIG
# ---------------------------------------------------------
app = FastAPI(title="AI Hiring App - Final Unified Version", version="1.2.0")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# SCHEMA DEFINITIONS
# ---------------------------------------------------------
class QuestionRequest(BaseModel):
    job_title: str

class QuestionResponse(BaseModel):
    questions: List[str]

class ParsedResumeData(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    current_title: Optional[str] = None
    experience: Optional[str] = None
    skills: List[str] = []
    education: Optional[str] = None
    professional_summary: Optional[str] = None

class JobDescriptionText(BaseModel):
    text: str

class ParsedJobData(BaseModel):
    title: Optional[str] = None
    skills: List[str] = []

class JobRecommendation(schemas.Job):
    match_score: int

class RecommendationsResponse(BaseModel):
    avg_match_score: int
    recommended_count: int
    jobs: List[JobRecommendation]

class CompanyCreate(BaseModel):
    name: str

class RecruiterCreate(schemas.UserCreate):
    company_name: str

class ManagerCreate(schemas.UserCreate):
    company_name: str

class ShortlistDashboardResponse(BaseModel):
    total_shortlisted: int
    total_approved: int
    pending_review: int
    avg_match_score: int
    candidates: List[schemas.CandidateProfile]

class SummaryResponse(BaseModel):
    summary: str

# ---------------------------------------------------------
# UTILS ENDPOINTS
# ---------------------------------------------------------
@app.post("/utils/parse-resume", response_model=ParsedResumeData, tags=["Utilities"])
async def parse_resume_for_profile(file: UploadFile = File(...)):
    file_bytes = await file.read()
    parsed_data = utils.parse_resume(file_bytes, file.filename)
    return parsed_data


@app.post("/utils/parse-job-description", response_model=ParsedJobData, tags=["Utilities"])
def parse_job_description(job_text: JobDescriptionText):
    context = job_text.text
    if not context:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    title = utils.ask_question(context, "What is the job title?")
    all_skills = utils.TECH_SKILLS + utils.SOFT_SKILLS
    extracted_skills = {
        skill for skill in all_skills if re.search(r"\b" + re.escape(skill) + r"\b", context, re.IGNORECASE)
    }

    return {"title": title, "skills": list(extracted_skills)}

# ---------------------------------------------------------
# AUTHENTICATION ENDPOINTS
# ---------------------------------------------------------
@app.post("/users/register", response_model=schemas.User, tags=["Authentication"])
def create_user_simple(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = models.User(email=user.email, password=user.password, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/token", response_model=schemas.Token, tags=["Authentication"])
def login_simple(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or user.password != form_data.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token = f"simple-token-for::{user.email}::role::{user.role}"
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/auth/register/recruiter", response_model=schemas.User, tags=["Authentication"])
def register_recruiter(user_data: RecruiterCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    company = db.query(models.Company).filter(models.Company.name == user_data.company_name).first()
    if not company:
        company = models.Company(name=user_data.company_name)
        db.add(company)
        db.commit()
        db.refresh(company)

    new_user = models.User(
        email=user_data.email,
        password=user_data.password,
        role='recruiter',
        company_id=company.id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/auth/register/manager", response_model=schemas.User, tags=["Authentication"])
def register_manager(user_data: ManagerCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    company = db.query(models.Company).filter(models.Company.name == user_data.company_name).first()
    if not company:
        company = models.Company(name=user_data.company_name)
        db.add(company)
        db.commit()
        db.refresh(company)

    new_user = models.User(
        email=user_data.email,
        password=user_data.password,
        role='manager',
        company_id=company.id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/job-seeker/create-profile", response_model=schemas.User, tags=["Job Seeker"])
def create_job_seeker_profile(profile_data: schemas.ProfileCompleteData, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == profile_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")
    new_user = models.User(
        email=profile_data.email,
        password=profile_data.password,
        role='job_seeker'
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# ---------------------------------------------------------
# JOB MANAGEMENT ENDPOINTS
# ---------------------------------------------------------
@app.post("/jobs/", response_model=schemas.Job, tags=["Jobs"])
def create_job(job: schemas.JobCreate, db: Session = Depends(get_db)):
    db_job = models.Job(**job.model_dump())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


@app.get("/jobs/", response_model=List[schemas.Job], tags=["Jobs"])
def get_jobs(db: Session = Depends(get_db)):
    return db.query(models.Job).all()

# ---------------------------------------------------------
# CANDIDATE & RESUME UPLOAD
# ---------------------------------------------------------
@app.post("/jobs/{job_id}/upload_resume/", response_model=schemas.CandidateProfile, tags=["Candidates"])
async def upload_resume(job_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    db_job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")

    file_bytes = await file.read()
    parsed_data = utils.parse_resume(file_bytes, file.filename)

    if "error" in parsed_data or not parsed_data.get("email"):
        raise HTTPException(status_code=400, detail="Could not parse resume or find an email.")

    existing_candidate = db.query(models.Candidate).filter(
        models.Candidate.email == parsed_data["email"],
        models.Candidate.job_id == job_id
    ).first()
    if existing_candidate:
        raise HTTPException(status_code=400, detail="Candidate has already applied for this job.")

    resume_text = parsed_data.get("raw_text", "")
    job_description = db_job.description
    ai_insights = utils.generate_candidate_insights(resume_text, job_description)

    db_candidate = models.Candidate(
        name=parsed_data.get("full_name"),
        email=parsed_data.get("email"),
        skills=parsed_data.get("skills"),
        raw_text=resume_text,
        job_id=job_id,
        ai_insights=ai_insights
    )

    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate

# ---------------------------------------------------------
# AI TOOLS
# ---------------------------------------------------------
@app.post("/ai/generate-interview-questions", response_model=QuestionResponse, tags=["AI Tools"])
def generate_interview_questions(data: QuestionRequest):
    if not data.job_title:
        raise HTTPException(status_code=400, detail="Job title cannot be empty.")

    prompt = (
        f"You are an expert hiring manager preparing to interview a candidate for a '{data.job_title}' position. "
        "Generate a list of 5 insightful interview questions for this role. "
        "Include behavioral, technical, and situational questions. "
        "Return ONLY a numbered list."
    )

    response_text = utils.call_llm(prompt)
    questions = [
        line.strip().lstrip('0123456789. ') for line in response_text.split('\n')
        if line.strip() and len(line) > 5
    ]
    if not questions:
        return {"questions": ["The AI could not generate questions at this time."]}
    return {"questions": questions}


@app.get("/ai/summarize-candidate/{candidate_id}", response_model=SummaryResponse, tags=["AI Tools"])
def summarize_candidate_for_manager(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    job = db.query(models.Job).filter(models.Job.id == candidate.job_id).first()
    if not candidate or not job:
        raise HTTPException(status_code=404, detail="Candidate or Job not found.")

    prompt = (
        f"You are a hiring manager. Provide 3 concise bullet points summarizing this candidate's suitability "
        f"for the '{job.title}' role based on their resume:\n\n{candidate.raw_text}"
    )

    summary = utils.call_llm(prompt)
    return {"summary": summary}
# ---------------------------------------------------------
# RECRUITER DASHBOARD & JOB RECOMMENDATIONS
# ---------------------------------------------------------
@app.get("/recruiter/dashboard-data", response_model=ShortlistDashboardResponse, tags=["Recruiter"])
def get_recruiter_dashboard_data(db: Session = Depends(get_db)):
    all_candidates = db.query(models.Candidate).all()
    all_jobs_dict = {j.id: j for j in db.query(models.Job).all()}

    total_score = 0
    candidate_count = 0
    for cand in all_candidates:
        job = all_jobs_dict.get(cand.job_id)
        if job:
            cand.match_score = utils.calculate_match_score(cand.skills, job.required_skills)
            total_score += cand.match_score
            candidate_count += 1
        else:
            cand.match_score = 0

    avg_score = int(total_score / candidate_count) if candidate_count > 0 else 0
    sorted_candidates = sorted(all_candidates, key=lambda c: c.match_score, reverse=True)

    return {
        "total_shortlisted": len([c for c in all_candidates if c.status == 'shortlisted']),
        "total_approved": len([c for c in all_candidates if c.status == 'approved']),
        "pending_review": len([c for c in all_candidates if c.status == 'shortlisted']),
        "avg_match_score": avg_score,
        "candidates": sorted_candidates,
    }


@app.get("/candidate/recommendations/{user_id}", response_model=RecommendationsResponse, tags=["Candidate Portal"])
def get_job_recommendations(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    first_candidate_profile = db.query(models.Candidate).filter(models.Candidate.email == user.email).first()
    if not first_candidate_profile or not first_candidate_profile.skills:
        return {"avg_match_score": 0, "recommended_count": 0, "jobs": []}

    user_skills = first_candidate_profile.skills
    all_jobs = db.query(models.Job).all()

    recommended_jobs = []
    total_score = 0
    high_match_count = 0

    for job in all_jobs:
        match_score = utils.calculate_match_score(user_skills, job.required_skills)
        if match_score > 70:
            recommended_jobs.append({"match_score": match_score, **job.__dict__})
            total_score += match_score
            high_match_count += 1

    recommended_jobs.sort(key=lambda j: j['match_score'], reverse=True)
    avg_score = int(total_score / high_match_count) if high_match_count > 0 else 0

    return {
        "avg_match_score": avg_score,
        "recommended_count": high_match_count,
        "jobs": recommended_jobs,
    }


@app.get("/users/by-email", response_model=schemas.User, tags=["Users"])
def get_user_by_email(email: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
@app.post("/job-seeker/create-profile", response_model=schemas.User, tags=["Job Seeker"])
def create_job_seeker_profile(profile_data: schemas.ProfileCompleteData, db: Session = Depends(get_db)):
    """
    Creates a new user with the role 'job_seeker' from the reviewed profile data.
    """
    existing_user = db.query(models.User).filter(models.User.email == profile_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")
    
    # Using the simple, insecure password storage for now
    new_user = models.User(
        email=profile_data.email,
        password=profile_data.password,
        role='job_seeker'
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # In a full app, you'd also save the rest of the profile data here.
    
    return new_user
@app.post("/recruiter/candidates/{candidate_id}/approve", tags=["Recruiter Actions"])
def approve_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """
    Finds a candidate and changes their status from 'shortlisted' to 'approved'.
    'Approved' candidates are ready for the hiring manager.
    """
    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Update the status
    candidate.status = "approved"
    db.commit()
    
    return {"status": "success", "message": "Candidate approved for hiring manager review."}


@app.post("/recruiter/candidates/{candidate_id}/reject", tags=["Recruiter Actions"])
def reject_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """
    Finds a candidate and PERMANENTLY DELETES them from the database.
    """
    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    # Delete the record from the database
    db.delete(candidate)
    db.commit()
    
    return {"status": "success", "message": "Candidate has been rejected and deleted."}
@app.get("/jobs/{job_id}/approved_candidates", response_model=List[schemas.CandidateProfile], tags=["Manager Actions"])
def get_approved_candidates_for_job(job_id: int, db: Session = Depends(get_db)):
    """
    Fetches all candidates for a specific job that have been marked as 'approved'
    by a recruiter, making them ready for hiring manager review.
    """
    approved_candidates = (
        db.query(models.Candidate)
        .filter(
            models.Candidate.job_id == job_id,
            models.Candidate.status == 'approved'
        )
        .all()
    )
    
    if not approved_candidates:
        return [] # Return an empty list if none are found, not an error
        
    return approved_candidates
@app.get("/manager/dashboard", response_model=schemas.ManagerDashboardResponse, tags=["Manager Actions"])
def get_manager_dashboard_data(db: Session = Depends(get_db)):
    """
    Provides a simple, unprotected list of jobs that have 'approved' candidates.
    This is what the manager sees.
    """
    # 1. Find all candidates with the 'approved' status.
    approved_candidates = db.query(models.Candidate).filter(models.Candidate.status == 'approved').all()
    
    # 2. Get the unique job IDs from this list.
    job_ids_with_approved_candidates = {c.job_id for c in approved_candidates if c.job_id is not None}
    
    # If no jobs have approved candidates, return an empty dashboard.
    if not job_ids_with_approved_candidates:
        return schemas.ManagerDashboardResponse(
            stats=schemas.ManagerDashboardStats(total_jobs=0, total_approved_candidates=0, highest_priority_job="None"),
            jobs=[]
        )

    # 3. Fetch the full job objects for those IDs.
    jobs_to_review = db.query(models.Job).filter(models.Job.id.in_(job_ids_with_approved_candidates)).all()

    # 4. Count how many approved candidates each job has.
    candidate_counts = {}
    for candidate in approved_candidates:
        candidate_counts[candidate.job_id] = candidate_counts.get(candidate.job_id, 0) + 1

    # 5. Build the summary list for the frontend.
    job_summaries = [schemas.ManagerJobSummary(
        id=job.id,
        title=job.title,
        company_name=job.company_name,
        location=job.location,
        approved_candidate_count=candidate_counts.get(job.id, 0)
    ) for job in jobs_to_review]
    
    # 6. Calculate simple stats.
    highest_priority_job = sorted(job_summaries, key=lambda j: j.approved_candidate_count, reverse=True)
    stats = schemas.ManagerDashboardStats(
        total_jobs=len(job_summaries),
        total_approved_candidates=len(approved_candidates),
        highest_priority_job=highest_priority_job[0].title if highest_priority_job else "None"
    )

    return schemas.ManagerDashboardResponse(stats=stats, jobs=job_summaries)

# =====================================================================
# Other essential endpoints that your app needs to function
# =====================================================================

@app.get("/jobs/{job_id}/approved_candidates", response_model=List[schemas.CandidateProfile], tags=["Manager Actions"])
def get_approved_candidates_for_job(job_id: int, db: Session = Depends(get_db)):
    approved_candidates = db.query(models.Candidate).filter(
        models.Candidate.job_id == job_id,
        models.Candidate.status == 'approved'
    ).all()
    return approved_candidates

@app.post("/recruiter/candidates/{candidate_id}/approve", tags=["Recruiter Actions"])
def approve_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not candidate: raise HTTPException(status_code=404, detail="Candidate not found")
    candidate.status = "approved"
    db.commit()
    return {"status": "success"}

@app.post("/recruiter/candidates/{candidate_id}/reject", tags=["Recruiter Actions"])
def reject_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not candidate: raise HTTPException(status_code=404, detail="Candidate not found")
    db.delete(candidate)
    db.commit()
    return {"status": "success"}

@app.get("/recruiter/dashboard-data", response_model=schemas.ShortlistDashboardResponse, tags=["Recruiter"])
def get_recruiter_dashboard_data(db: Session = Depends(get_db)):
    candidates_for_recruiter = db.query(models.Candidate).filter(models.Candidate.status.in_(['new', 'shortlisted'])).all()
    all_candidates = db.query(models.Candidate).all()
    return {
        "candidates": sorted(candidates_for_recruiter, key=lambda c: c.match_score or 0, reverse=True),
        "total_shortlisted": len([c for c in all_candidates if c.status == 'shortlisted']),
        "total_approved": len([c for c in all_candidates if c.status == 'approved']),
        "pending_review": len(candidates_for_recruiter),
        "avg_match_score": 0
    }
