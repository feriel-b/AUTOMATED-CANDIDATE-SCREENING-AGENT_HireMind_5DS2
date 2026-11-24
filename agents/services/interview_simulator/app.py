"""
FastAPI app for interview simulator using LangChain agents with Ollama.
Migrated from CrewAI to pure LangChain orchestration.
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import logging
import sys
import os
import json

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

# Import LangChain orchestrator (replaced CrewAI)
from crews.interview_orchestrator import InterviewOrchestrator
from core.ollama_config import OllamaConfig

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="HireMind Interview Simulator API",
    description="AI-powered interview system using LangChain + Ollama",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestrator instance
orchestrator: Optional[InterviewOrchestrator] = None

@app.on_event("startup")
async def startup_event():
    """Initialize the interview orchestrator on startup."""
    global orchestrator
    
    logger.info("="*70)
    logger.info("🚀 HireMind Interview Simulator Starting...")
    logger.info("="*70)
    
    try:
        # Check Ollama availability
        logger.info("🔍 Checking Ollama server...")
        if not OllamaConfig.check_availability():
            logger.error("❌ Ollama server not available!")
            logger.info("💡 Start Ollama: ollama serve")
            logger.info(f"💡 Pull model: ollama pull {os.getenv('OLLAMA_MODEL_NAME', 'phi4-mini')}")
            return
        
        logger.info(f"✅ Ollama server available at {os.getenv('OLLAMA_BASE_URL')}")
        logger.info(f"✅ Using model: {os.getenv('OLLAMA_MODEL_NAME', 'phi4-mini')}")
        
        # Initialize orchestrator
        logger.info("🔧 Initializing LangChain orchestrator...")
        orchestrator = InterviewOrchestrator()
        
        # Log status
        status = orchestrator.get_status()
        logger.info("\n" + "="*70)
        logger.info("✅ SYSTEM READY")
        logger.info("="*70)
        logger.info(f"Framework: {status['framework']}")
        logger.info(f"Model: {status['model']}")
        logger.info(f"Agents: {len(status['agents'])} ready")
        logger.info(f"Tools: {', '.join(status['tools'].values())}")
        logger.info("="*70 + "\n")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize orchestrator: {e}")
        import traceback
        traceback.print_exc()

@app.get("/")
async def root():
    """Health check and system status endpoint."""
    if orchestrator is None:
        return {
            "status": "error",
            "message": "Orchestrator not initialized. Check Ollama server.",
            "hint": "Run: ollama serve"
        }
    
    status = orchestrator.get_status()
    return {
        "status": "running",
        "message": "HireMind Interview Simulator API",
        "version": "2.0.0",
        "framework": status["framework"],
        "model": status["model"],
        "agents": status["agents"],
        "tools": status["tools"],
        "capabilities": status["capabilities"]
    }

@app.get("/api/status")
async def get_status():
    """Detailed system status."""
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="Orchestrator not ready")
    
    return orchestrator.get_status()

@app.post("/api/select-questions")
async def select_questions(
    categories: str = Form(..., description="Comma-separated categories"),
    difficulty: str = Form("medium", description="easy, medium, or hard"),
    num_questions: int = Form(3, description="Number of questions to select"),
    candidate_performance: str = Form("average", description="low, average, or high")
):
    """
    Select interview questions based on criteria.
    
    Example:
        categories: "Python,Algorithms,Data Structures"
        difficulty: "medium"
        num_questions: 5
        candidate_performance: "average"
    """
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="Orchestrator not ready")
    
    try:
        # Parse categories
        category_list = [c.strip() for c in categories.split(",")]
        
        logger.info(f"📋 Question selection request: {num_questions} questions")
        logger.info(f"   Categories: {category_list}")
        logger.info(f"   Difficulty: {difficulty}")
        
        # Call orchestrator
        result = await orchestrator.select_questions(
            categories=category_list,
            difficulty=difficulty,
            num_questions=num_questions,
            candidate_performance=candidate_performance
        )
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Question selection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process-answer")
async def process_answer(
    question_id: int = Form(...),
    question_text: str = Form(...),
    category: str = Form("General"),
    difficulty: str = Form("medium"),
    audio_file: UploadFile = File(...),
    video_file: Optional[UploadFile] = File(None)
):
    """
    Process candidate answer through complete pipeline.
    
    Pipeline:
    1. Transcription (Vosk STT)
    2. Prosody Analysis (Librosa)
    3. Emotion Detection (DeepFace, if video provided)
    4. Comprehensive Evaluation (Phi4-Mini)
    """
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="Orchestrator not ready")
    
    try:
        # Create temp directory
        os.makedirs("temp", exist_ok=True)
        
        # Save audio file
        audio_path = f"temp/audio_{question_id}_{audio_file.filename}"
        logger.info(f"💾 Saving audio to: {audio_path}")
        
        with open(audio_path, "wb") as f:
            content = await audio_file.read()
            f.write(content)
        
        # Save video file (if provided)
        video_path = None
        if video_file:
            video_path = f"temp/video_{question_id}_{video_file.filename}"
            logger.info(f"💾 Saving video to: {video_path}")
            
            with open(video_path, "wb") as f:
                content = await video_file.read()
                f.write(content)
        
        # Prepare question dict
        question = {
            "id": question_id,
            "question": question_text,
            "category": category,
            "difficulty": difficulty
        }
        
        # Process through orchestrator
        logger.info(f"🚀 Processing answer for question {question_id}")
        result = await orchestrator.process_answer(
            question=question,
            audio_path=audio_path,
            video_path=video_path
        )
        
        # Cleanup temp files
        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
            if video_path and os.path.exists(video_path):
                os.remove(video_path)
        except Exception as cleanup_error:
            logger.warning(f"⚠️ Cleanup failed: {cleanup_error}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Answer processing failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-summary")
async def generate_summary(session_data: dict):
    """
    Generate comprehensive session summary.
    
    Expected session_data format:
    {
        "candidate_id": "12345",
        "answers": [
            {
                "question_id": 1,
                "question": "...",
                "evaluation": {...}
            }
        ]
    }
    """
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="Orchestrator not ready")
    
    try:
        logger.info(f"📊 Generating summary for {len(session_data.get('answers', []))} answers")
        
        result = await orchestrator.generate_session_summary(session_data)
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Summary generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting HireMind Interview Simulator API...")
    logger.info("📡 Server will be available at: http://localhost:8000")
    logger.info("📚 API docs available at: http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )