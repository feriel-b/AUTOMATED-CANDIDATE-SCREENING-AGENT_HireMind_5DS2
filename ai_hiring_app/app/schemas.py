from pydantic import BaseModel, Field, ConfigDict 
from typing import List, Optional, Dict, Any

class JobCreate(BaseModel):
    title: str = Field(..., example="Senior Python Developer")
    description: str = Field(..., example="We are looking for a developer with experience in FastAPI and AWS.")
    required_skills: List[str] = Field(..., example=["Python", "FastAPI", "AWS", "SQL"])

    
class Job(JobCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

  

class CandidateProfile(BaseModel):
    name: Optional[str] = Field(None, example="Jane Doe")
    email: Optional[str] = Field(None, example="jane.doe@example.com")
    skills: List[str] = Field([], example=["Python", "Machine Learning"])
    raw_text: Optional[str] = Field(None, example="Experienced Python developer...")
    match_score: Optional[int] = Field(None, example=95) # <-- ADD THIS LINE
    model_config = ConfigDict(from_attributes=True)


# =================================================================
# INTERVIEW SIMULATOR SCHEMAS
# =================================================================

class PauseAnalysis(BaseModel):
    """Analysis of pause patterns in speech"""
    total_pause_time: float = Field(..., description="Total time spent in pauses (seconds)")
    pause_count: int = Field(..., description="Number of significant pauses (>200ms)")
    avg_pause_duration: float = Field(..., description="Average duration of pauses (seconds)")
    pause_frequency: float = Field(..., description="Pauses per second")
    speech_ratio: float = Field(..., description="Ratio of speech to total time (0-1)")
    speech_intervals: Optional[List[Dict[str, float]]] = Field(default=None, description="List of speech segments with start/end seconds")

class SpeechRateAnalysis(BaseModel):
    """Analysis of speech rate and tempo"""
    words_per_minute: float = Field(..., description="Estimated words per minute")
    estimated_word_count: int = Field(..., description="Estimated number of words spoken")
    duration_seconds: float = Field(..., description="Total audio duration")
    speech_rate_category: str = Field(..., description="slow, normal, or fast")

class PitchAnalysis(BaseModel):
    """Analysis of pitch variation and vocal characteristics"""
    mean_pitch: float = Field(..., description="Average fundamental frequency (Hz)")
    pitch_std: float = Field(..., description="Standard deviation of pitch")
    pitch_range: float = Field(..., description="Range between min and max pitch (Hz)")
    pitch_jitter: float = Field(..., description="Local pitch variation measure")
    voiced_ratio: float = Field(..., description="Ratio of voiced to total frames")
    pitch_category: str = Field(..., description="monotone, normal, or highly_variable")

class TranscriptAnalysis(BaseModel):
    """Enhanced linguistic analysis with nervous pattern detection"""
    filler_word_count: int = Field(..., description="Count of filler words (uh, um, like)")
    filler_word_ratio: float = Field(..., description="Ratio of filler words to total words")
    filler_breakdown: Optional[dict] = Field(None, description="Breakdown of specific filler words and counts")
    repetition_count: int = Field(..., description="Count of word repetitions")
    hedge_word_count: int = Field(..., description="Count of uncertainty indicators")
    nervous_phrase_count: int = Field(default=0, description="Count of nervous/panic phrases")
    detected_nervous_phrases: Optional[List[str]] = Field(default=[], description="List of detected nervous phrases")
    nervous_phrase_breakdown: Optional[Dict[str, int]] = Field(default=None, description="Counts per nervous phrase")
    apology_count: int = Field(default=0, description="Count of apology words indicating nervousness")
    emergency_stress_detected: bool = Field(default=False, description="Whether emergency stress patterns were detected")
    stress_indicators: Optional[List[str]] = Field(default=[], description="List of detected stress indicators")
    total_words: Optional[int] = Field(None, description="Total word count in transcript")
    transcript_available: bool = Field(..., description="Whether transcript was generated")
    transcript_text: Optional[str] = Field(None, description="Partial transcript text (preview)")
    full_transcript: Optional[str] = Field(None, description="Complete transcript text")
    segments: Optional[List[Dict[str, Any]]] = Field(default=None, description="Whisper ASR segments with start/end times and text")

class VoiceAnalysisResult(BaseModel):
    """Comprehensive voice analysis result including Phase 2 features"""
    # Phase 1: Stress Detection
    not_stressed_probability: float = Field(..., example=0.25, description="Probability of not being stressed (0-1)")
    stressed_probability: float = Field(..., example=0.75, description="Probability of being stressed (0-1)")
    is_stressed: bool = Field(..., example=True, description="Whether the speaker is classified as stressed")
    confidence: float = Field(..., example=0.75, description="Confidence in the prediction (0-1)")
    stress_level: str = Field(..., example="High", description="Human-readable stress level: Low, Moderate, High, Very High")
    
    # Phase 2: Advanced Audio Analysis
    pause_analysis: PauseAnalysis = Field(..., description="Pause and silence pattern analysis")
    speech_rate_analysis: SpeechRateAnalysis = Field(..., description="Speech rate and tempo analysis")
    pitch_analysis: PitchAnalysis = Field(..., description="Pitch variation and vocal characteristics")
    transcript_analysis: TranscriptAnalysis = Field(..., description="Linguistic features from transcript")
    nervousness_score: float = Field(..., example=0.68, description="Composite nervousness score (0-1)")
    
    # Metadata
    sample_rate: int = Field(..., example=16000, description="Audio sample rate in Hz")
    duration_seconds: float = Field(..., example=5.3, description="Duration of the audio clip in seconds")
    analysis_version: str = Field(..., example="phase2", description="Version of analysis pipeline used")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "not_stressed_probability": 0.25,
                "stressed_probability": 0.75,
                "is_stressed": True,
                "confidence": 0.75,
                "stress_level": "High",
                "pause_analysis": {
                    "total_pause_time": 1.2,
                    "pause_count": 3,
                    "avg_pause_duration": 0.4,
                    "pause_frequency": 0.56,
                    "speech_ratio": 0.77
                },
                "speech_rate_analysis": {
                    "words_per_minute": 145.0,
                    "estimated_word_count": 12,
                    "duration_seconds": 5.3,
                    "speech_rate_category": "normal"
                },
                "pitch_analysis": {
                    "mean_pitch": 180.5,
                    "pitch_std": 25.3,
                    "pitch_range": 95.2,
                    "pitch_jitter": 3.1,
                    "voiced_ratio": 0.82,
                    "pitch_category": "normal"
                },
                "transcript_analysis": {
                    "filler_word_count": 2,
                    "filler_word_ratio": 0.17,
                    "repetition_count": 0,
                    "hedge_word_count": 1,
                    "total_words": 12,
                    "transcript_available": True,
                    "transcript_text": "Well, I think, um, this is a really good opportunity for me to, uh, demonstrate my skills."
                },
                "nervousness_score": 0.68,
                "sample_rate": 16000,
                "duration_seconds": 5.3,
                "analysis_version": "phase2"
            }
        }
    )