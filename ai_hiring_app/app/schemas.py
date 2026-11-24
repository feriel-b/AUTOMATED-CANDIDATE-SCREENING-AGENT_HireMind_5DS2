# In app/schemas.py
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

# =====================================================================
# JOB SCHEMAS (Your original, correct version)
# =====================================================================

class JobBase(BaseModel):
    title: str
    description: str
    required_skills: List[str]
    company_name: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    culture_description: Optional[str] = None
    growth_opportunities: Optional[str] = None

class JobCreate(JobBase):
    pass

class Job(JobBase):
    id: int
    date_posted: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


# =====================================================================
# NEW: Nested Models for Structured Candidate Data
# =====================================================================

class ExperienceItem(BaseModel):
    """Represents a single job in a candidate's work history."""
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None # Responsibilities and achievements

class EducationItem(BaseModel):
    """Represents a single educational qualification."""
    degree: Optional[str] = None
    institution: Optional[str] = None
    graduation_date: Optional[str] = None

class AIEvaluation(BaseModel):
    """A structured way to store the output of AI analysis."""
    summary: Optional[str] = None
    strengths: List[str] = []
    considerations: List[str] = []


# =====================================================================
# EXPANDED: Candidate Schemas
# =====================================================================

class CandidateBase(BaseModel):
    """The foundational data for a candidate profile, now much richer."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    current_title: Optional[str] = None
    
    professional_summary: Optional[str] = None
    
    # NOTE: While we can model this, for simplicity the frontend
    # will likely handle experience and education as single text blocks.
    # The models are here for future expansion.
    experience: Optional[str] = None
    education: Optional[str] = None
    
    skills: List[str] = []
    raw_text: Optional[str] = None

class CandidateProfile(CandidateBase):
    """The full candidate profile as it exists in the database."""
    id: int
    job_id: Optional[int] = None # Made optional for general candidate pool
    status: str
    match_score: Optional[int] = None
    ai_insights: Optional[AIEvaluation] = None # Store the AI's analysis here

    model_config = ConfigDict(from_attributes=True)


# =====================================================================
# EXPANDED: API Payload for Completing a Profile
# =====================================================================

class ProfileCompleteData(BaseModel):
    """The comprehensive data sent from the frontend after user review."""
    full_name: str
    email: str
    password: str
    
    # All the fields the AI extracts and the user can edit
    phone: Optional[str] = None
    location: Optional[str] = None
    current_title: Optional[str] = None
    
    experience: Optional[str] = None 
    education: Optional[str] = None
    professional_summary: Optional[str] = None
    
    skills: List[str] = []
    raw_text: Optional[str] = None


# =====================================================================
# AUTHENTICATION & OTHER SCHEMAS (Your original, correct versions)
# =====================================================================

class UserBase(BaseModel):
    email: str
    role: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class ManagerJobSummary(BaseModel):
    id: int
    title: str
    company_name: str
    location: str
    approved_candidate_count: int

class ManagerDashboardStats(BaseModel):
    total_jobs: int
    total_approved_candidates: int
    highest_priority_job: Optional[str] = None

class ManagerDashboardResponse(BaseModel):
    stats: ManagerDashboardStats
    jobs: List[ManagerJobSummary]
class ShortlistDashboardResponse(BaseModel):
    total_shortlisted: int
    total_approved: int
    pending_review: int
    avg_match_score: int
    candidates: List[CandidateProfile] # It depends on CandidateProfile
