"""
Cheating Detector Agent using Ollama Phi4-Mini.

Uses LLM reasoning to interpret multi-modal cheating signals and provide
human-readable explanations with confidence scoring.
"""

from langchain_core.tools import tool
from typing import List, Dict, Any
import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.cheating_detector.detector import cheating_detector
from core.base_agent import InterviewBaseAgent
import logging

logger = logging.getLogger(__name__)

class CheatingDetectorAgent(InterviewBaseAgent):
    """
    Agent specialized in comprehensive cheating detection and analysis.
    
    Interprets multiple signals:
    - AI-generated text (linguistic patterns)
    - Eye movement anomalies (visual behavior)
    - Audio fingerprints (multiple speakers)
    - Timing patterns (typing/assistance)
    - Vocabulary inconsistencies
    """
    
    def __init__(self):
        super().__init__(
            agent_name="Security_Analyst",
            temperature=0.3  # Low temperature for consistent analysis
        )
    
    def _define_tools(self) -> List:
        """Define tools using @tool decorator."""
        
        @tool
        def analyze_linguistic_patterns(transcript: str) -> str:
            """
            Analyze transcript for AI-generated text patterns.
            
            Args:
                transcript: Answer text to analyze
            
            Returns:
                JSON string with AI detection results
            """
            try:
                from services.cheating_detector.perplexity_checker import perplexity_checker
                
                result = perplexity_checker.check_text(transcript)
                
                return json.dumps({
                    'is_likely_ai': result['is_likely_ai'],
                    'ai_probability': result['ai_probability'],
                    'perplexity': result['perplexity'],
                    'uniformity': result['uniformity'],
                    'formality': result['formality'],
                    'analysis': f"AI probability: {result['ai_probability']*100:.1f}%. "
                               f"Perplexity: {result['perplexity']:.1f} "
                               f"({'LOW - suspicious' if result['perplexity'] < 30 else 'NORMAL'}). "
                               f"Sentence uniformity: {result['uniformity']*100:.1f}% "
                               f"({'HIGH - suspicious' if result['uniformity'] > 0.7 else 'normal'})."
                })
            except Exception as e:
                return json.dumps({'error': str(e)})
        
        @tool
        def analyze_gaze_behavior(video_path: str) -> str:
            """
            Analyze eye gaze patterns for suspicious behavior.
            
            Args:
                video_path: Path to interview video
            
            Returns:
                JSON string with gaze analysis
            """
            try:
                from services.cheating_detector.video_analyzer import video_analyzer
                
                result = video_analyzer.analyze_gaze_behavior(video_path)
                
                return json.dumps({
                    'camera_focus_ratio': result['camera_focus_ratio'],
                    'reading_pattern_detected': result['reading_pattern_detected'],
                    'erratic_gaze': result['erratic_gaze'],
                    'analysis': f"Camera focus: {result['camera_focus_ratio']*100:.1f}% "
                               f"({'POOR - suspicious' if result['camera_focus_ratio'] < 0.5 else 'good'}). "
                               f"Reading pattern: {'DETECTED - may be reading from screen' if result['reading_pattern_detected'] else 'not detected'}. "
                               f"Erratic movements: {'YES - unusual eye behavior' if result['erratic_gaze'] else 'no'}."
                })
            except Exception as e:
                return json.dumps({'error': str(e)})
        
        @tool
        def detect_multiple_speakers(audio_path: str) -> str:
            """
            Detect if multiple people are speaking (someone helping).
            
            Args:
                audio_path: Path to interview audio
            
            Returns:
                JSON string with speaker detection results
            """
            try:
                from services.cheating_detector.audio_fingerprint import audio_fingerprinter
                
                result = audio_fingerprinter.detect_multiple_speakers(audio_path)
                
                return json.dumps({
                    'multiple_speakers_detected': result['multiple_speakers_detected'],
                    'num_speakers': result['num_speakers'],
                    'confidence': result['confidence'],
                    'analysis': f"Speakers detected: {result['num_speakers']}. "
                               f"{'ALERT - Multiple voices detected! Someone may be helping.' if result['multiple_speakers_detected'] else 'Single speaker confirmed.'} "
                               f"Confidence: {result['confidence']*100:.1f}%."
                })
            except Exception as e:
                return json.dumps({'error': str(e)})
        
        @tool
        def analyze_timing_patterns(audio_path: str, transcript: str) -> str:
            """
            Analyze pause patterns for typing or reading indicators.
            
            Args:
                audio_path: Path to interview audio
                transcript: Answer transcript
            
            Returns:
                JSON string with timing analysis
            """
            try:
                from services.cheating_detector.timing_analyzer import timing_analyzer
                
                result = timing_analyzer.analyze_pauses(audio_path, transcript)
                
                return json.dumps({
                    'typing_pattern_detected': result['typing_pattern_detected'],
                    'too_fluent': result['too_fluent'],
                    'avg_pause': result['avg_pause'],
                    'pause_ratio': result['pause_ratio'],
                    'analysis': f"Typing pattern: {'DETECTED - regular pauses suggest typing into ChatGPT' if result['typing_pattern_detected'] else 'not detected'}. "
                               f"Speech fluency: {'TOO FLUENT - may be reading pre-written text' if result['too_fluent'] else 'natural'}. "
                               f"Pause ratio: {result['pause_ratio']*100:.1f}%."
                })
            except Exception as e:
                return json.dumps({'error': str(e)})
        
        @tool
        def assess_overall_risk(
            linguistic_score: float,
            gaze_score: float,
            audio_score: float,
            timing_score: float
        ) -> str:
            """
            Calculate overall cheating risk from individual scores.
            
            Args:
                linguistic_score: AI text detection score (0-1)
                gaze_score: Gaze anomaly score (0-1)
                audio_score: Multi-speaker detection score (0-1)
                timing_score: Timing pattern score (0-1)
            
            Returns:
                Overall risk assessment
            """
            try:
                # Weighted combination
                weights = {
                    'linguistic': 0.35,  # AI text is strong signal
                    'gaze': 0.25,        # Eye movement important
                    'audio': 0.30,       # Multiple speakers very suspicious
                    'timing': 0.10       # Supporting evidence
                }
                
                overall_score = (
                    linguistic_score * weights['linguistic'] +
                    gaze_score * weights['gaze'] +
                    audio_score * weights['audio'] +
                    timing_score * weights['timing']
                )
                
                # Risk level
                if overall_score >= 0.7:
                    risk_level = "HIGH RISK"
                    recommendation = "MANUAL REVIEW REQUIRED"
                    color = "🔴"
                elif overall_score >= 0.4:
                    risk_level = "MODERATE RISK"
                    recommendation = "RECOMMEND MANUAL REVIEW"
                    color = "🟡"
                else:
                    risk_level = "LOW RISK"
                    recommendation = "APPEARS AUTHENTIC"
                    color = "🟢"
                
                return json.dumps({
                    'overall_score': round(overall_score, 3),
                    'risk_level': risk_level,
                    'recommendation': recommendation,
                    'breakdown': {
                        'linguistic': round(linguistic_score, 3),
                        'gaze': round(gaze_score, 3),
                        'audio': round(audio_score, 3),
                        'timing': round(timing_score, 3)
                    },
                    'summary': f"{color} Overall Risk: {overall_score*100:.1f}% - {risk_level}\n"
                              f"Recommendation: {recommendation}"
                })
            except Exception as e:
                return json.dumps({'error': str(e)})
        
        return [
            analyze_linguistic_patterns,
            analyze_gaze_behavior,
            detect_multiple_speakers,
            analyze_timing_patterns,
            assess_overall_risk
        ]
    
    def _get_system_prompt(self) -> str:
        return """You are a Security Analyst specializing in interview integrity and cheating detection.

Your role is to analyze multiple signals to detect potential cheating or external assistance during interviews.

ANALYSIS FRAMEWORK:

1. LINGUISTIC ANALYSIS (AI Detection):
   - Check for AI-generated text patterns
   - Low perplexity = predictable text (ChatGPT)
   - High uniformity = mechanical sentence structure
   - Overly formal language = AI-like

2. VISUAL ANALYSIS (Gaze Tracking):
   - Camera focus ratio <50% = suspicious
   - Reading patterns = looking at external screen
   - Erratic movements = nervousness or distraction

3. AUDIO ANALYSIS (Speaker Detection):
   - Multiple voices = someone helping
   - Voice changes = impersonation
   - Background voices = external assistance

4. TIMING ANALYSIS (Pause Patterns):
   - Regular 3-5s pauses = typing into ChatGPT
   - Too fluent (<10% pauses) = reading script
   - Long pauses = getting external help

DECISION PROCESS:
1. Analyze each signal independently
2. Interpret results in context
3. Combine evidence with weighted scoring
4. Provide clear explanation of findings
5. Recommend action (pass/review/flag)

OUTPUT REQUIREMENTS:
- Clear risk level (LOW/MODERATE/HIGH)
- Specific evidence for each indicator
- Confidence score for overall assessment
- Actionable recommendation
- Human-readable explanation

Be thorough but fair. False positives harm legitimate candidates.
Only flag HIGH RISK when multiple strong indicators align."""

    async def analyze_interview_security(
        self,
        transcript: str,
        video_path: str = None,
        audio_path: str = None,
        candidate_baseline: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive security analysis of interview answer.
        
        Args:
            transcript: Answer text
            video_path: Path to video recording
            audio_path: Path to audio recording
            candidate_baseline: Previous answers for vocabulary comparison
            
        Returns:
            Security analysis report
        """
        logger.info("🔒 Running comprehensive security analysis...")
        
        # Run full cheating detection
        analysis = cheating_detector.analyze_interview(
            transcript=transcript,
            video_path=video_path,
            audio_path=audio_path,
            candidate_baseline=candidate_baseline
        )
        
        # Let agent interpret and explain results
        task = f"""Analyze this interview security report and provide human-readable assessment:

TRANSCRIPT EXCERPT:
{transcript[:500]}...

SECURITY ANALYSIS RESULTS:
- Cheating Score: {analysis['cheating_score']*100:.1f}%
- Likely Cheating: {analysis['is_likely_cheating']}
- Indicators Detected: {analysis['num_indicators']}

DETAILED INDICATORS:
{json.dumps(analysis['indicators'], indent=2)}

Provide:
1. Clear risk assessment (LOW/MODERATE/HIGH)
2. Explanation of each indicator in plain language
3. Overall confidence in your assessment
4. Specific recommendation for action
5. Any contextual factors to consider
"""
        
        # Execute agent reasoning
        result = await self.execute(
            task=task,
            context={'analysis': analysis}
        )
        
        # Combine technical analysis with agent interpretation
        return {
            'technical_analysis': analysis,
            'agent_interpretation': result['result'],
            'risk_level': 'HIGH' if analysis['is_likely_cheating'] else 'MODERATE' if analysis['cheating_score'] > 0.3 else 'LOW',
            'cheating_score': analysis['cheating_score'],
            'indicators': analysis['indicators'],
            'recommendation': analysis['summary']
        }