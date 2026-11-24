# In app/main.py
print("--- RUNNING FLATTENED main.py (FINAL, CLEANED VERSION) ---")

from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from pydantic import BaseModel

# CORRECT IMPORTS - NO DOTS
import models
import schemas
import utils
import interview_agent # Correctly import our new module
from database import engine, get_db
import re

models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="AI Hiring App - Final Version", version="1.1.0")

origins = ["*"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# --- Schema for parser endpoint ---
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
class ParsedResumeData(BaseModel):
    full_name: Optional[str] = None; email: Optional[str] = None; phone: Optional[str] = None; location: Optional[str] = None
    current_title: Optional[str] = None; experience: Optional[str] = None; skills: List[str] = []
    education: Optional[str] = None; professional_summary: Optional[str] = None
class JobDescriptionText(BaseModel):
    text: str

# Add a new Pydantic model for the response
class ParsedJobData(BaseModel):
    title: Optional[str] = None
    skills: List[str] = []
# --- ALL ENDPOINTS ---
@app.post("/utils/parse-resume-for-profile", response_model=ParsedResumeData, tags=["Utilities"])
async def parse_resume_for_profile(file: UploadFile = File(...)):
    # ... (This logic is fine)
    file_bytes = await file.read()
    parsed_data = utils.parse_resume(file_bytes, file.filename)
    return parsed_data

@app.post("/users/register", response_model=schemas.User, tags=["Authentication"])
def create_user_simple(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # ... (This logic is fine)
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user: raise HTTPException(status_code=400, detail="Email already registered")
    new_user = models.User(email=user.email, password=user.password, role=user.role)
    db.add(new_user); db.commit(); db.refresh(new_user); return new_user
    
@app.post("/token", response_model=schemas.Token, tags=["Authentication"])
def login_simple(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # ... (This logic is fine)
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or user.password != form_data.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token = f"simple-token-for::{user.email}::role::{user.role}"
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/jobs/", response_model=schemas.Job, tags=["Jobs"])
def create_job(job: schemas.JobCreate, db: Session = Depends(get_db)):
    # ... (This logic is fine)
    db_job = models.Job(**job.model_dump()); db.add(db_job); db.commit(); db.refresh(db_job); return db_job

@app.get("/jobs/", response_model=List[schemas.Job], tags=["Jobs"])
def get_jobs(db: Session = Depends(get_db)):
    # This line MUST return a list of job objects.
    return db.query(models.Job).all()

# ... (All other Job and Candidate endpoints are also fine)

# =================================================================
# NEW AI INTERVIEW ENDPOINTS
# =================================================================

@app.post("/interviews/start/{job_id}", tags=["AI Interview"])
def start_interview(job_id: int, db: Session = Depends(get_db)):
    db_job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    initial_history = [{"role": "AI Interviewer", "content": "Hello and welcome. To start, please tell me about yourself and your background."}]
    first_question_text = initial_history[0]['content']
    audio_bytes = interview_agent.convert_text_to_speech(first_question_text)
    return {
        "conversation_history": initial_history,
        "next_question_text": first_question_text,
        "next_question_audio": list(audio_bytes)
    }

@app.post("/interviews/next", tags=["AI Interview"])
async def process_interview_turn(
    job_description: str,
    conversation_history: List[Dict],
    audio_file: UploadFile = File(...)
):
    audio_bytes = await audio_file.read()
    user_answer_text = interview_agent.transcribe_audio(audio_bytes)
    conversation_history.append({"role": "Candidate", "content": user_answer_text})
    next_question_text = interview_agent.generate_next_question(job_description, conversation_history)
    conversation_history.append({"role": "AI Interviewer", "content": next_question_text})
    audio_bytes = interview_agent.convert_text_to_speech(next_question_text)
    return {
        "conversation_history": conversation_history,
        "next_question_text": next_question_text,
        "next_question_audio": list(audio_bytes)
    }
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
@app.post("/auth/register/recruiter", response_model=schemas.User, tags=["Authentication"])
def register_recruiter(user_data: RecruiterCreate, db: Session = Depends(get_db)):
    # Check if user email already exists
    if db.query(models.User).filter(models.User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Find or create the company
    company = db.query(models.Company).filter(models.Company.name == user_data.company_name).first()
    if not company:
        company = models.Company(name=user_data.company_name)
        db.add(company)
        db.commit()
        db.refresh(company)

    # Create the user and link to the company
    new_user = models.User(
        email=user_data.email,
        password=user_data.password, # Plain text for dev
        role='recruiter',
        company_id=company.id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/auth/register/manager", response_model=schemas.User, tags=["Authentication"])
def register_manager(user_data: ManagerCreate, db: Session = Depends(get_db)):
    # Logic is identical to recruiter for now
    if db.query(models.User).filter(models.User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    company = db.query(models.Company).filter(models.Company.name == user_data.company_name).first()
    if not company:
        company = models.Company(name=user_data.company_name)
        db.add(company); db.commit(); db.refresh(company)

    new_user = models.User(
        email=user_data.email,
        password=user_data.password,
        role='manager',
        company_id=company.id
    )
    db.add(new_user); db.commit(); db.refresh(new_user)
    return new_user

@app.get("/recruiter/all-candidates", response_model=List[schemas.CandidateProfile], tags=["Recruiter Actions"])
def get_all_candidates_with_scores(db: Session = Depends(get_db)):
    """
    Fetches all candidates from the database and calculates their match score
    relative to the job they applied for.
    This is for the main recruiter dashboard.
    """
    all_candidates = db.query(models.Candidate).all()
    all_jobs = db.query(models.Job).all()
    
    # Create a quick lookup dictionary for jobs to avoid slow queries in a loop
    jobs_dict = {job.id: job for job in all_jobs}
    
    # Annotate each candidate with their match score
    for candidate in all_candidates:
        job_they_applied_for = jobs_dict.get(candidate.job_id)
        if job_they_applied_for:
            candidate.match_score = utils.calculate_match_score(
                candidate.skills, 
                job_they_applied_for.required_skills
            )
        else:
            candidate.match_score = 0 # Default score if job is not found

    return all_candidates
@app.post("/utils/parse-job-description", response_model=ParsedJobData, tags=["Utilities"])
def parse_job_description(job_text: JobDescriptionText):
    """
    (AI-POWERED) Takes raw job description text and extracts key details.
    """
    context = job_text.text
    if not context:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    # Use our existing 'ask_question' utility to parse the job description
    title = utils.ask_question(context, "What is the job title?")
    
    # Use our regex skill finder to find skills
    all_skills = utils.TECH_SKILLS + utils.SOFT_SKILLS # Assuming these lists are in utils.py
    extracted_skills = {skill for skill in all_skills if re.search(r"\b" + re.escape(skill) + r"\b", context, re.IGNORECASE)}
    
    return {
        "title": title,
        "skills": list(extracted_skills)
    }
@app.get("/candidate/recommendations/{user_id}", response_model=RecommendationsResponse, tags=["Candidate Portal"])
def get_job_recommendations(user_id: int, db: Session = Depends(get_db)):
    """
    Calculates personalized job recommendations for a specific job seeker.
    """
    # In a real app with auth, we'd get the user from a token.
    # For now, we get them by ID.
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # We need the user's skills. In a full app, this would be on a separate profile model.
    # For now, let's create a placeholder. We'll assume the user's skills are stored on
    # the first candidate profile they created. This is a temporary hack.
    first_candidate_profile = db.query(models.Candidate).filter(models.Candidate.email == user.email).first()
    
    if not first_candidate_profile or not first_candidate_profile.skills:
        # If the user has no skills, we can't recommend anything.
        return {"avg_match_score": 0, "recommended_count": 0, "jobs": []}
    
    user_skills = first_candidate_profile.skills
    
    all_jobs = db.query(models.Job).all()
    
    recommended_jobs = []
    total_score = 0
    high_match_count = 0

    for job in all_jobs:
        match_score = utils.calculate_match_score(user_skills, job.required_skills)
        
        # We'll consider a "recommended" job one with a score > 70%
        if match_score > 70:
            recommended_jobs.append({"match_score": match_score, **job.__dict__})
            total_score += match_score
            high_match_count += 1
    
    # Sort the jobs by the highest match score
    recommended_jobs.sort(key=lambda j: j['match_score'], reverse=True)
    
    avg_score = int(total_score / high_match_count) if high_match_count > 0 else 0
    
    return {
        "avg_match_score": avg_score,
        "recommended_count": high_match_count,
        "jobs": recommended_jobs
    }
@app.get("/users/by-email", response_model=schemas.User, tags=["Users"])
def get_user_by_email(email: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user