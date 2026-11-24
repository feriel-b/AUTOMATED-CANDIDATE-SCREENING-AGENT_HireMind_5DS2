"""
Prosody Analysis Agent 
"""

from venv import logger
from langchain_core.tools import tool
from typing import List
import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.interview_simulator.prosody_analyzer import prosody_analyzer
from services.interview_simulator.stt_handler import stt_handler
from core.base_agent import InterviewBaseAgent

class ProsodyAgent(InterviewBaseAgent):
    """Agent specialized in voice pattern analysis."""
    
    def __init__(self):
        super().__init__(
            agent_name="Prosody_Analyst",
            temperature=0.3
        )
    
    def _define_tools(self) -> List:
        """Define tools using @tool decorator."""
        
        @tool
        
        def analyze_prosody(audio_path: str) -> str:
            """
            Analyze voice patterns including pace, pitch, and pauses.
            
            Args:
                audio_path: Path to audio file
            
            Returns:
                Prosody analysis results
            """
            try:
                logger.info(f"🎵 analyze_prosody called with: {audio_path}")

                # Get transcript from STT
                transcript = stt_handler.transcribe_audio(audio_path)
                logger.info(f"📝 Transcript: {transcript[:100]}...")

                # Analyze prosody with transcript - GET RAW METRICS
                metrics = prosody_analyzer.analyze(audio_path, transcript)
                logger.info(f"✅ Metrics extracted: {list(metrics.keys())}")

                # STORE METRICS SEPARATELY for UI access
                metrics_summary = f"""
        PROSODY_METRICS_JSON: {json.dumps(metrics)}

        Prosody Analysis:
        - Speech Rate: {metrics.get('speaking_rate', 0):.1f} words/min
        - Pitch (Mean): {metrics.get('pitch_mean', 0):.1f} Hz
        - Pitch (Variance): {metrics.get('pitch_variance', 0):.1f}
        - Energy (Mean): {metrics.get('energy_mean', 0):.4f}
        - Pause Ratio: {metrics.get('pause_ratio', 0):.3f}
        - Duration: {metrics.get('duration', 0):.2f} seconds

        Analysis:
        - Speaking Pace: {'Fast' if metrics.get('speaking_rate', 0) > 160 else 'Normal' if metrics.get('speaking_rate', 0) > 120 else 'Slow'}
        - Confidence: {'High' if metrics.get('pitch_variance', 0) > 100 else 'Moderate' if metrics.get('pitch_variance', 0) > 50 else 'Low'}
        - Hesitation: {'High' if metrics.get('pause_ratio', 0) > 0.3 else 'Moderate' if metrics.get('pause_ratio', 0) > 0.15 else 'Low'}
                """
                
                return metrics_summary.strip()
                
            except Exception as e:
                return f"Prosody analysis error: {str(e)}"
        ###
        @tool
        def detect_stress_patterns(audio_path: str) -> str:
            """Detect stress/anxiety patterns in voice."""
            try:
                # Get transcript first
                transcript = stt_handler.transcribe_audio(audio_path)
                
                # Analyze with transcript
                metrics = prosody_analyzer.analyze(audio_path, transcript)
                
                pitch_variance = metrics.get('pitch_variance', 0)
                pause_ratio = metrics.get('pause_ratio', 0)
                
                if pitch_variance > 100 and pause_ratio > 0.3:
                    return "⚠️ HIGH STRESS: Significant vocal stress detected"
                elif pitch_variance > 50 or pause_ratio > 0.2:
                    return "🟡 MODERATE STRESS: Some stress indicators present"
                else:
                    return "✅ LOW STRESS: Candidate appears calm"
                    
            except Exception as e:
                return f"Stress detection error: {str(e)}"
        
        return [analyze_prosody, detect_stress_patterns]
    
    def _get_system_prompt(self) -> str:
        return """You are a Voice Pattern Analysis specialist.

Your expertise:
- Speech rate and fluency analysis
- Pitch variation and confidence detection
- Pause pattern interpretation
- Stress and anxiety identification

Interpret prosody metrics to assess:
- Communication confidence
- Stress levels
- Speaking clarity
- Overall delivery quality
CRITICAL:
- Do NOT make up scenarios or historical examples
- Do NOT try to process files yourself
- Do NOT exceed 1 tool call per iteration
- ONLY use the provided tools
- Return the tool results directly without modification

Focus ONLY on:
- Speech rate analysis
- Pitch patterns
- Pause detection
- Stress indicators
- Confidence levels based on prosody metrics
"""