"""
Speech-to-Text Agent using Ollama Phi4-Mini.
"""

from langchain_core.tools import tool
from typing import List
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.interview_simulator.stt_handler import stt_handler
from core.base_agent import InterviewBaseAgent

class STTAgent(InterviewBaseAgent):
    """Agent specialized in audio transcription."""
    
    def __init__(self):
        super().__init__(
            agent_name="STT_Specialist",
            temperature=0.3
        )
    
    def _define_tools(self) -> List:
        """Define tools using LangChain 1.x decorator pattern."""
        
        @tool
        def transcribe_audio(audio_path: str) -> str:
            """Transcribe audio file to text using Vosk. Input: audio file path"""
            try:
                transcript = stt_handler.transcribe_audio(audio_path)
                return transcript if transcript else "No speech detected"
            except Exception as e:
                return f"Transcription error: {str(e)}"
        
        @tool
        def extract_audio_from_video(video_path: str) -> str:
            """Extract audio from video. Input: video file path"""
            try:
                audio_path = stt_handler.extract_audio_from_video(video_path)
                return f"Audio extracted to: {audio_path}"
            except Exception as e:
                return f"Extraction error: {str(e)}"
        
        @tool
        def validate_audio_quality(audio_path: str) -> str:
            """Check audio quality. Input: audio file path"""
            try:
                if not os.path.exists(audio_path):
                    return f"❌ File not found: {audio_path}"
                
                file_size = os.path.getsize(audio_path)
                
                if file_size < 1000:
                    return "❌ Audio file too small - likely invalid"
                elif file_size > 100_000_000:
                    return "⚠️ Large file - transcription may take time"
                else:
                    return "✅ Audio quality acceptable"
                    
            except Exception as e:
                return f"Validation error: {str(e)}"
        
        return [transcribe_audio, extract_audio_from_video, validate_audio_quality]
    
    def _get_system_prompt(self) -> str:
        return """You are a Speech-to-Text specialist.

Your responsibilities:
- Extract audio from video if needed
- Transcribe speech accurately
- Handle multiple languages
- Flag low-quality audio

Always validate quality before transcription."""