"""
Pydantic models for request/response validation.

Pydantic automatically validates incoming data and generates API documentation.
Each model represents the structure of data we send/receive from the API.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class QuestionResponse(BaseModel):
    """
    Response model for a single interview question.
    
    Returned when client requests a question from the Q&A bank.
    """
    id: int
    category: str
    question: str
    difficulty: str
    time_limit: int = Field(description="Maximum time to answer in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "category": "behavioral",
                "question": "Tell me about a time you failed at something.",
                "difficulty": "medium",
                "time_limit": 120
            }
        }

class SessionStartRequest(BaseModel):
    """
    Request to start a new interview session.
    
    Client can optionally specify categories and difficulty.
    """
    categories: Optional[List[str]] = Field(
        default=None,
        description="Filter questions by categories (behavioral, technical, etc.)"
    )
    difficulty: Optional[str] = Field(
        default=None,
        description="Filter by difficulty: easy, medium, hard"
    )
    num_questions: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of questions in the session"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "categories": ["behavioral", "technical"],
                "difficulty": "medium",
                "num_questions": 5
            }
        }

class SessionStartResponse(BaseModel):
    """
    Response when starting a new session.
    
    Returns session_id and first question.
    """
    session_id: str
    total_questions: int
    current_question: QuestionResponse
    message: str = "Session started successfully"

class AnswerSubmitRequest(BaseModel):
    """
    Request when submitting an answer.
    
    Client uploads audio/video file via multipart form-data,
    so this model is used for metadata only.
    """
    session_id: str
    question_id: int
    response_time: Optional[float] = Field(
        default=None,
        description="Time taken to answer in seconds"
    )

class EmotionResult(BaseModel):
    """
    Emotion detection result for a single frame.
    """
    timestamp: str = Field(description="Time in video (MM:SS format)")
    emotion: str = Field(description="Dominant emotion detected")
    confidence: float = Field(ge=0, le=1)
    all_emotions: Dict[str, float] = Field(
        description="Scores for all 7 emotions"
    )

class StressMetrics(BaseModel):
    """
    Voice stress analysis results.
    
    Higher values indicate more stress/anxiety.
    """
    stress_score: float = Field(
        ge=0, le=1,
        description="Overall stress level (0=calm, 1=very stressed)"
    )
    pitch_mean: float = Field(description="Average pitch in Hz")
    pitch_variance: float = Field(description="Pitch variability")
    jitter: float = Field(description="Pitch instability (higher=more stress)")
    shimmer: float = Field(description="Amplitude instability")
    
    class Config:
        json_schema_extra = {
            "example": {
                "stress_score": 0.35,
                "pitch_mean": 180.5,
                "pitch_variance": 42.3,
                "jitter": 0.012,
                "shimmer": 0.045
            }
        }

class ProsodyMetrics(BaseModel):
    """
    Speech prosody (rhythm and intonation) metrics.
    """
    speaking_rate: float = Field(description="Words per minute")
    pause_ratio: float = Field(
        ge=0, le=1,
        description="Fraction of time spent pausing"
    )
    energy_mean: float = Field(description="Average audio energy")
    energy_variance: float = Field(description="Energy variability")
    
    class Config:
        json_schema_extra = {
            "example": {
                "speaking_rate": 145.0,
                "pause_ratio": 0.12,
                "energy_mean": 0.045,
                "energy_variance": 0.023
            }
        }

class AnswerEvaluation(BaseModel):
    """
    Complete evaluation of an interview answer.
    
    This is the main response returned after processing audio/video.
    """
    session_id: str
    question_id: int
    question_text: str
    transcript: str = Field(description="Speech-to-text result")
    
    # Scores (0-100)
    relevance_score: float = Field(
        ge=0, le=100,
        description="How well answer matches question"
    )
    clarity_score: float = Field(
        ge=0, le=100,
        description="Speech clarity and coherence"
    )
    overall_score: float = Field(
        ge=0, le=100,
        description="Combined score"
    )
    
    # Detailed metrics
    prosody_metrics: ProsodyMetrics
    stress_metrics: Optional[StressMetrics] = None
    emotion_timeline: Optional[List[EmotionResult]] = None
    
    # Feedback
    feedback: List[str] = Field(
        description="Human-readable feedback points"
    )
    
    # Metadata
    processing_time: float = Field(description="Time taken to process in seconds")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess_abc123",
                "question_id": 1,
                "question_text": "Tell me about a time you failed.",
                "transcript": "I worked on a project that didn't meet expectations...",
                "relevance_score": 85.0,
                "clarity_score": 78.0,
                "overall_score": 81.5,
                "prosody_metrics": {
                    "speaking_rate": 145.0,
                    "pause_ratio": 0.12,
                    "energy_mean": 0.045,
                    "energy_variance": 0.023
                },
                "stress_metrics": {
                    "stress_score": 0.35,
                    "pitch_mean": 180.5,
                    "pitch_variance": 42.3,
                    "jitter": 0.012,
                    "shimmer": 0.045
                },
                "emotion_timeline": [
                    {
                        "timestamp": "00:03",
                        "emotion": "neutral",
                        "confidence": 0.89,
                        "all_emotions": {
                            "neutral": 0.89,
                            "happy": 0.05,
                            "sad": 0.03,
                            "angry": 0.01,
                            "fear": 0.01,
                            "surprise": 0.00,
                            "disgust": 0.01
                        }
                    }
                ],
                "feedback": [
                    "✅ Good clarity and speaking pace",
                    "💡 Try to maintain eye contact with camera",
                    "⚠️ Detected slight stress in voice tone"
                ],
                "processing_time": 65.3,
                "timestamp": "2025-10-19T15:30:00"
            }
        }

class SessionSummary(BaseModel):
    """
    Summary of completed interview session.
    """
    session_id: str
    total_questions: int
    questions_answered: int
    average_score: float
    total_duration: float = Field(description="Total session time in seconds")
    completed: bool

class ErrorResponse(BaseModel):
    """
    Standard error response.
    """
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)