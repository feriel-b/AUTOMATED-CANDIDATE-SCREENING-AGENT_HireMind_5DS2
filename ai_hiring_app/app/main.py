# =================================================================
# SECTION 1: IMPORTS
# =================================================================
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware  # << -------------------- ADD THIS LINE
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import Query
import logging

# These are your application's internal imports
from . import models, schemas
from .database import engine, get_db
from .ai_modules.resume_parser import parse_resume
from .ai_modules.matching_engine import calculate_match_score
from .interview_simulator.question_bank import get_question_bank
from .interview_simulator.tts_service import get_tts_service
from .interview_simulator.answer_evaluator import get_answer_evaluator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =================================================================
# SECTION 2: APPLICATION SETUP
# =================================================================

# This command tells SQLAlchemy to create all tables defined in models.py
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Hiring Management App API",
    description="The backend API for the AI-powered hiring application.",
    version="0.1.0",
)

# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
# START OF NEW CODE BLOCK TO ADD
# This is the CORS configuration. It must be added after `app` is defined.
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

"""
For local development, allow requests from any origin (including file:// pages with Origin: null).
Credentials are disabled to permit wildcard origin.
"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# END OF NEW CODE BLOCK
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


# =================================================================
# SECTION 3: API ENDPOINTS (No changes below this line)
# =================================================================

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Hiring API"}

@app.post("/jobs/", response_model=schemas.Job, status_code=201)
def create_job(job: schemas.JobCreate, db: Session = Depends(get_db)):
    """
    Endpoint to create a new job posting and save it to the database.
    """
    db_job = models.Job(**job.model_dump())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

@app.get("/jobs/", response_model=List[schemas.Job])
def get_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Endpoint to retrieve all job postings from the database.
    """
    jobs = db.query(models.Job).offset(skip).limit(limit).all()
    return jobs

@app.post("/upload/resume/", response_model=schemas.CandidateProfile)
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Endpoint to upload a resume, parse it, and save the candidate to the database.
    """
    if not (file.filename.endswith(".pdf") or file.filename.endswith(".docx")):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF or DOCX.")
        
    file_bytes = await file.read()
    
    try:
        parsed_data = parse_resume(file_bytes, file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing file: {str(e)}")

    if "error" in parsed_data or not parsed_data.get("email"):
        raise HTTPException(status_code=400, detail="Could not parse resume or find an email.")
    
    existing_candidate = db.query(models.Candidate).filter(models.Candidate.email == parsed_data["email"]).first()
    if existing_candidate:
        raise HTTPException(status_code=400, detail=f"Candidate with email {parsed_data['email']} already exists.")

    db_candidate = models.Candidate(**parsed_data)
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    
    return schemas.CandidateProfile.model_validate(db_candidate)

@app.get("/jobs/{job_id}/candidates/rank", response_model=List[schemas.CandidateProfile])
def get_ranked_candidates_for_job(job_id: int, db: Session = Depends(get_db)):
    """
    Retrieves all candidates, calculates their match score for a specific job,
    and returns them ranked from highest score to lowest.
    """
    db_job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_skills = db_job.required_skills
    all_candidates = db.query(models.Candidate).all()
    if not all_candidates:
        return []

    for candidate in all_candidates:
        candidate.match_score = calculate_match_score(candidate.skills, job_skills)
    
    all_candidates.sort(key=lambda x: x.match_score, reverse=True)

    return all_candidates


# =================================================================
# SECTION 4: INTERVIEW SIMULATOR ENDPOINTS
# =================================================================

@app.post("/interview/analyze-voice", response_model=schemas.VoiceAnalysisResult)
async def analyze_interview_voice(file: UploadFile = File(...)):
    """
    Endpoint to analyze candidate's voice during interview for stress detection.
    
    Accepts audio files (WAV, MP3, etc.) and returns:
    - Stress probability
    - Confidence level
    - Human-readable stress level
    - Audio metadata
    
    This uses:
    1. Wav2Vec2 for audio feature extraction
    2. HuggingFace stress recognition model for classification
    """
    # Validate file type (support browser recordings like WebM/Opus and .weba)
    allowed_extensions = [
        ".wav", ".mp3", ".m4a", ".flac", ".ogg", ".webm", ".opus", ".weba"
    ]
    allowed_content_types = {
        "audio/webm", "video/webm", "audio/ogg", "audio/opus", "audio/mpeg",
        "audio/wav", "audio/x-wav", "audio/mp4", "audio/aac", "audio/flac"
    }
    file_ext = "." + file.filename.split(".")[-1].lower() if "." in (file.filename or "") else ""
    content_type = (file.content_type or "").lower()

    if (file_ext not in allowed_extensions) and (content_type not in allowed_content_types):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)} or content-types {', '.join(sorted(allowed_content_types))}"
        )
    
    logger.info(f"Received audio file: {file.filename} ({file_ext})")
    
    # Read file bytes
    try:
        audio_bytes = await file.read()
        logger.info(f"File size: {len(audio_bytes)} bytes")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read audio file: {str(e)}")
    
    # Get analyzer instance and perform analysis
    try:
        # Lazy import to avoid import errors on platforms without optional deps
        from .interview_simulator.voice_analyzer import get_voice_analyzer
        analyzer = get_voice_analyzer()
        results = analyzer.analyze_audio(audio_bytes)
        logger.info(f"✓ Analysis successful: {results['stress_level']} stress")
        return results
    except ValueError as e:
        # Audio processing errors
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Model inference errors
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Voice analysis failed: {str(e)}"
        )


@app.get("/interview/health")
def check_interview_module_health():
    """
    Health check endpoint for interview simulator module.
    Verifies that voice analysis models are loaded and ready.
    """
    try:
        # Lazy import to avoid import errors on platforms without optional deps
        from .interview_simulator.voice_analyzer import get_voice_analyzer
        analyzer = get_voice_analyzer()
        # Try enabling VAD at runtime in case it was installed after analyzer init
        try:
            if hasattr(analyzer, "try_enable_vad"):
                analyzer.try_enable_vad()
        except Exception:
            pass
        vad_status = "ready" if getattr(analyzer, "vad", None) is not None else "unavailable"
        return {
            "status": "healthy",
            "module": "interview_simulator",
            "voice_analyzer": "ready",
            "models": {
                "wav2vec2": "loaded",
                "stress_recognition": "loaded",
                "vad": vad_status
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Interview module not ready: {str(e)}"
        )


# =================================================================
# SECTION 7: AI INTERVIEW SIMULATOR ENDPOINTS
# =================================================================

@app.get("/interview/roles", tags=["AI Interview Simulator"])
def get_interview_roles():
    """
    Get all available job roles for interview practice.
    
    Returns:
        List of role names
    """
    try:
        qbank = get_question_bank()
        roles = qbank.get_roles()
        return {
            "roles": roles,
            "count": len(roles)
        }
    except Exception as e:
        logger.error(f"Error fetching roles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/interview/categories", tags=["AI Interview Simulator"])
def get_interview_categories(role: Optional[str] = None):
    """
    Get all available question categories, optionally filtered by role.
    
    Args:
        role: Filter categories by this role (optional)
    
    Returns:
        List of category names
    """
    try:
        qbank = get_question_bank()
        categories = qbank.get_categories(role=role)
        return {
            "categories": categories,
            "count": len(categories),
            "filtered_by_role": role
        }
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/interview/questions", tags=["AI Interview Simulator"])
def get_interview_questions(
    role: Optional[str] = None,
    category: Optional[str] = None,
    categories: Optional[List[str]] = Query(None),
    limit: Optional[int] = None,
    shuffle: bool = False
):
    """
    Get interview questions filtered by role and/or category.
    
    Args:
        role: Filter by job role
        category: Filter by question category
        limit: Maximum number of questions to return
        shuffle: Randomize question order
    
    Returns:
        List of questions with answers and metadata
    """
    try:
        qbank = get_question_bank()
        # Backward compatibility: if no categories list provided, but category provided, wrap it
        categories_list = categories if categories else ([category] if category else None)
        questions = qbank.get_questions(
            role=role,
            category=category,
            categories=categories_list,
            limit=limit,
            shuffle=shuffle
        )
        return {
            "questions": questions,
            "count": len(questions),
            "filters": {
                "role": role,
                "category": category,
                "categories": categories_list,
                "limit": limit,
                "shuffle": shuffle
            }
        }
    except Exception as e:
        logger.error(f"Error fetching questions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/interview/read-question", tags=["AI Interview Simulator"])
async def read_question(request: dict):
    """
    Generate TTS audio for a question.
    
    Request body:
        {
            "text": "Question text to read",
            "lang": "en" (optional),
            "slow": false (optional)
        }
    
    Returns:
        Audio file (MP3) of the question being read
    """
    try:
        text = request.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="Question text is required")
        
        lang = request.get("lang", "en")
        slow = request.get("slow", False)
        
        tts = get_tts_service()
        audio_path = tts.generate_speech(text, lang=lang, slow=slow)
        
        return FileResponse(
            path=str(audio_path),
            media_type="audio/mpeg",
            filename="question.mp3"
        )
    except Exception as e:
        logger.error(f"Error generating TTS: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/interview/evaluate-answer", tags=["AI Interview Simulator"])
async def evaluate_answer(request: dict):
    """
    Evaluate user's answer against expected answer.
    
    Request body:
        {
            "user_answer": "User's transcribed answer",
            "expected_answer": "Expected answer or guidance",
            "question": "Original question" (optional)
        }
    
    Returns:
        {
            "score": 85,
            "semantic_score": 90,
            "keyword_score": 75,
            "feedback": {
                "level": "good",
                "message": "Good answer!...",
                "color": "#3b82f6"
            },
            "method": "ml_semantic"
        }
    """
    try:
        user_answer = request.get("user_answer", "")
        expected_answer = request.get("expected_answer", "")
        question = request.get("question", "")
        key_points = request.get("key_points")
        
        if not user_answer:
            raise HTTPException(status_code=400, detail="User answer is required")
        
        # If expected_answer not provided, try to fetch from question bank by question text
        used_qbank_expected = False
        if not expected_answer and question:
            try:
                qbank = get_question_bank()
                q = qbank.find_question(question)
                if q:
                    expected_answer = q.get("answer", "")
                    # Optional: allow key_points from JSON
                    if key_points is None:
                        key_points = q.get("key_points")
                    used_qbank_expected = True
            except Exception:
                pass

        evaluator = get_answer_evaluator()
        result = evaluator.evaluate(
            user_answer=user_answer,
            expected_answer=expected_answer,
            question=question,
            key_points=key_points
        )
        if used_qbank_expected:
            result["used_expected_from_qbank"] = True
        
        return result
    except Exception as e:
        logger.error(f"Error evaluating answer: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/interview/detect-ai-answer", tags=["AI Interview Simulator"])
async def detect_ai_answer(request: dict):
    """
    Estimate whether a given answer is AI-generated or human-written.

    Request body:
        { "text": "Answer text to check" }

    Returns:
        {
            "ai_probability": 0.73,
            "confidence": 0.62,
            "method": "ml_perplexity+heuristics" | "heuristics_only",
            "features": { ... },
            "explanation": "..."
        }
    """
    try:
        text = (request or {}).get("text", "")
        if not text or not isinstance(text, str) or not text.strip():
            raise HTTPException(status_code=400, detail="Text is required")

        # Lazy import to avoid optional dependency issues
        from .interview_simulator.ai_text_detector import get_ai_text_detector
        detector = get_ai_text_detector()
        result = detector.detect(text)

        # Convert dataclass to dict if needed
        if hasattr(result, "__dict__"):
            return {
                "ai_probability": result.ai_probability,
                "confidence": result.confidence,
                "method": result.method,
                "features": result.features,
                "explanation": result.explanation,
            }
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error detecting AI text: {e}")
        raise HTTPException(status_code=500, detail=str(e))