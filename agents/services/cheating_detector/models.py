"""
Pydantic models for Cheating Detector API.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List

class CheatingAnalysisRequest(BaseModel):
    """Request model for cheating analysis."""
    transcript: str = Field(..., description="Interview answer transcript")
    video_path: Optional[str] = Field(None, description="Path to video file")
    audio_path: Optional[str] = Field(None, description="Path to audio file")
    candidate_baseline: Optional[Dict] = Field(None, description="Previous answers for vocabulary comparison")

class CheatingIndicator(BaseModel):
    """Single cheating indicator."""
    type: str = Field(..., description="Indicator type (ai_assistance, eye_movement, etc.)")
    severity: float = Field(..., ge=0, le=1, description="Severity score (0-1)")
    confidence: float = Field(..., ge=0, le=1, description="Confidence in detection (0-1)")
    evidence: str = Field(..., description="Evidence description")
    timestamp: Optional[float] = Field(None, description="Timestamp in video/audio (seconds)")

class CheatingAnalysisResponse(BaseModel):
    """Response model for cheating analysis."""
    cheating_score: float = Field(..., ge=0, le=1, description="Overall cheating score (0-1)")
    is_likely_cheating: bool = Field(..., description="Whether cheating is likely")
    risk_level: str = Field(..., description="Risk level: LOW, MODERATE, HIGH")
    confidence: float = Field(..., ge=0, le=1, description="Overall confidence")
    num_indicators: int = Field(..., description="Number of indicators detected")
    indicators: List[Dict] = Field(..., description="List of cheating indicators")
    summary: str = Field(..., description="Human-readable summary")
    recommendation: str = Field(..., description="Recommended action")
    
    class Config:
        json_schema_extra = {
            "example": {
                "cheating_score": 0.75,
                "is_likely_cheating": True,
                "risk_level": "HIGH",
                "confidence": 0.85,
                "num_indicators": 3,
                "indicators": [
                    {
                        "type": "ai_assistance",
                        "severity": 0.8,
                        "confidence": 0.9,
                        "evidence": "Low perplexity (25.3) suggests AI-generated text"
                    }
                ],
                "summary": "🚨 HIGH RISK: Strong cheating indicators detected (3 indicators). Concerns: ai_assistance, eye_movement, timing.",
                "recommendation": "Manual review required"
            }
        }