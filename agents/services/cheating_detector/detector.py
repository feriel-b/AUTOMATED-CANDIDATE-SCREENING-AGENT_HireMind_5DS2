"""
Comprehensive Cheating Detection System.

Detects:
1. AI-assisted answers (GPT detection)
2. Eye movement anomalies (looking away from camera)
3. Vocabulary inconsistencies (spontaneous vs prepared)
4. Timing anomalies (pause patterns)
5. Audio fingerprinting (multiple voices)
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class CheatingIndicator:
    """Single cheating indicator with severity and evidence."""
    type: str  # 'ai_assistance', 'eye_movement', 'vocabulary', 'timing', 'audio'
    severity: float  # 0-1 (0=no issue, 1=severe)
    confidence: float  # 0-1 (how confident we are)
    evidence: str  # Description of what was detected
    timestamp: Optional[float] = None  # When detected (seconds into interview)

class CheatingDetector:
    """
    Multi-modal cheating detection system.
    
    Combines multiple signals:
    - Linguistic analysis (AI detection)
    - Visual analysis (gaze tracking)
    - Audio analysis (voice fingerprinting)
    - Behavioral analysis (timing patterns)
    """
    
    def __init__(self):
        """Initialize cheating detector with sub-analyzers."""
        logger.info("Initializing Cheating Detector...")
        
        # Import sub-analyzers
        from services.cheating_detector.perplexity_checker import perplexity_checker
        from services.cheating_detector.video_analyzer import video_analyzer
        from services.cheating_detector.audio_fingerprint import audio_fingerprinter
        from services.cheating_detector.timing_analyzer import timing_analyzer
        
        self.perplexity_checker = perplexity_checker
        self.video_analyzer = video_analyzer
        self.audio_fingerprinter = audio_fingerprinter
        self.timing_analyzer = timing_analyzer
        
        # Thresholds
        self.CHEATING_THRESHOLD = 0.6  # Overall score above this = likely cheating
        self.AI_PERPLEXITY_THRESHOLD = 30.0  # GPT text typically has low perplexity
        self.CAMERA_FOCUS_THRESHOLD = 0.5  # Looking at camera <50% = suspicious
        self.VOCABULARY_MISMATCH_THRESHOLD = 0.4  # Significant vocabulary change
        
        logger.info("✅ Cheating Detector initialized")
    
    def analyze_interview(
        self,
        transcript: str,
        video_path: Optional[str] = None,
        audio_path: Optional[str] = None,
        candidate_baseline: Optional[Dict] = None
    ) -> Dict:
        """
        Comprehensive cheating analysis of an interview answer.
        
        Args:
            transcript: Answer text
            video_path: Path to video recording
            audio_path: Path to audio recording
            candidate_baseline: Previous answers for comparison (vocabulary baseline)
            
        Returns:
            Cheating analysis report with score and indicators
        """
        logger.info("🔍 Running comprehensive cheating detection...")
        
        indicators: List[CheatingIndicator] = []
        
        # ═══════════════════════════════════════════════════════
        # 1. AI ASSISTANCE DETECTION (Linguistic Analysis)
        # ═══════════════════════════════════════════════════════
        logger.info("📝 Checking for AI-generated text...")
        ai_result = self.perplexity_checker.check_text(transcript)
        
        if ai_result['is_likely_ai']:
            indicators.append(CheatingIndicator(
                type='ai_assistance',
                severity=ai_result['ai_probability'],
                confidence=0.8,
                evidence=f"Low perplexity ({ai_result['perplexity']:.1f}) suggests AI-generated text. "
                         f"AI probability: {ai_result['ai_probability']*100:.1f}%"
            ))
        
        # ═══════════════════════════════════════════════════════
        # 2. EYE MOVEMENT ANALYSIS (Visual Behavior)
        # ═══════════════════════════════════════════════════════
        if video_path:
            logger.info("👁️ Analyzing eye movement and gaze patterns...")
            gaze_result = self.video_analyzer.analyze_gaze_behavior(video_path)
            
            # Check camera focus
            if gaze_result['camera_focus_ratio'] < self.CAMERA_FOCUS_THRESHOLD:
                indicators.append(CheatingIndicator(
                    type='eye_movement',
                    severity=1.0 - gaze_result['camera_focus_ratio'],
                    confidence=0.7,
                    evidence=f"Poor camera focus: only {gaze_result['camera_focus_ratio']*100:.1f}% "
                             f"looking at camera. Frequent looking away detected."
                ))
            
            # Check for reading patterns (left-to-right eye movement)
            if gaze_result.get('reading_pattern_detected', False):
                indicators.append(CheatingIndicator(
                    type='eye_movement',
                    severity=0.8,
                    confidence=0.6,
                    evidence="Reading pattern detected: horizontal eye movements suggest "
                             "reading from external source (screen/notes)."
                ))
            
            # Check for unusual gaze patterns
            if gaze_result.get('erratic_gaze', False):
                indicators.append(CheatingIndicator(
                    type='eye_movement',
                    severity=0.5,
                    confidence=0.5,
                    evidence="Erratic gaze patterns detected: rapid, non-natural eye movements."
                ))
        
        # ═══════════════════════════════════════════════════════
        # 3. VOCABULARY ANALYSIS (Consistency Check)
        # ═══════════════════════════════════════════════════════
        if candidate_baseline:
            logger.info("📚 Checking vocabulary consistency...")
            vocab_result = self._analyze_vocabulary_consistency(
                transcript,
                candidate_baseline
            )
            
            if vocab_result['mismatch_score'] > self.VOCABULARY_MISMATCH_THRESHOLD:
                indicators.append(CheatingIndicator(
                    type='vocabulary',
                    severity=vocab_result['mismatch_score'],
                    confidence=0.7,
                    evidence=f"Vocabulary mismatch: {vocab_result['mismatch_score']*100:.1f}% "
                             f"difference from baseline. Sophisticated words not used previously: "
                             f"{', '.join(vocab_result['new_sophisticated_words'][:5])}"
                ))
        
        # ═══════════════════════════════════════════════════════
        # 4. TIMING ANALYSIS (Pause Patterns)
        # ═══════════════════════════════════════════════════════
        if audio_path:
            logger.info("⏱️ Analyzing timing and pause patterns...")
            timing_result = self.timing_analyzer.analyze_pauses(audio_path, transcript)
            
            # Unnatural pause patterns (typing delays)
            if timing_result.get('typing_pattern_detected', False):
                indicators.append(CheatingIndicator(
                    type='timing',
                    severity=0.7,
                    confidence=0.6,
                    evidence=f"Typing pattern detected: regular pauses of {timing_result['avg_pause']:.1f}s "
                             f"suggest external assistance (typing into ChatGPT)."
                ))
            
            # Too smooth (no natural pauses)
            if timing_result.get('too_fluent', False):
                indicators.append(CheatingIndicator(
                    type='timing',
                    severity=0.5,
                    confidence=0.5,
                    evidence="Unnaturally fluent speech with minimal pauses suggests reading "
                             "pre-prepared or AI-generated text."
                ))
        
        # ═══════════════════════════════════════════════════════
        # 5. AUDIO FINGERPRINTING (Multiple Voices)
        # ═══════════════════════════════════════════════════════
        if audio_path:
            logger.info("🎤 Checking for multiple speakers...")
            audio_result = self.audio_fingerprinter.detect_multiple_speakers(audio_path)
            
            if audio_result['multiple_speakers_detected']:
                indicators.append(CheatingIndicator(
                    type='audio',
                    severity=1.0,
                    confidence=audio_result['confidence'],
                    evidence=f"Multiple speakers detected: {audio_result['num_speakers']} distinct voices. "
                             f"Someone else may be helping."
                ))
        
        # ═══════════════════════════════════════════════════════
        # AGGREGATE RESULTS
        # ═══════════════════════════════════════════════════════
        cheating_score = self._calculate_cheating_score(indicators)
        
        result = {
            'cheating_score': round(cheating_score, 3),
            'is_likely_cheating': cheating_score >= self.CHEATING_THRESHOLD,
            'confidence': self._calculate_overall_confidence(indicators),
            'num_indicators': len(indicators),
            'indicators': [
                {
                    'type': ind.type,
                    'severity': round(ind.severity, 3),
                    'confidence': round(ind.confidence, 3),
                    'evidence': ind.evidence,
                    'timestamp': ind.timestamp
                }
                for ind in indicators
            ],
            'summary': self._generate_summary(cheating_score, indicators)
        }
        
        logger.info(f"✅ Cheating detection complete: score={cheating_score:.2f}, "
                   f"indicators={len(indicators)}")
        
        return result
    
    def _analyze_vocabulary_consistency(
        self,
        current_text: str,
        baseline: Dict
    ) -> Dict:
        """
        Compare vocabulary sophistication against baseline.
        
        Args:
            current_text: Current answer text
            baseline: Previous answers for vocabulary comparison
            
        Returns:
            Vocabulary analysis results
        """
        from collections import Counter
        import re
        
        # Extract words
        current_words = set(re.findall(r'\b\w+\b', current_text.lower()))
        baseline_words = set(baseline.get('vocabulary', []))
        
        # Sophisticated words (length > 8, uncommon)
        sophisticated_words = {
            w for w in current_words
            if len(w) > 8 and w not in baseline_words
        }
        
        # Calculate mismatch score
        if not baseline_words:
            mismatch_score = 0.0
        else:
            new_word_ratio = len(sophisticated_words) / max(len(current_words), 1)
            mismatch_score = min(new_word_ratio * 2, 1.0)  # Scale to 0-1
        
        return {
            'mismatch_score': mismatch_score,
            'new_sophisticated_words': list(sophisticated_words)[:10],
            'baseline_size': len(baseline_words),
            'current_size': len(current_words)
        }
    
    def _calculate_cheating_score(self, indicators: List[CheatingIndicator]) -> float:
        """
        Calculate overall cheating score from individual indicators.
        
        Weighted by severity and confidence.
        
        Args:
            indicators: List of cheating indicators
            
        Returns:
            Overall cheating score (0-1)
        """
        if not indicators:
            return 0.0
        
        # Weighted scores
        weighted_scores = [
            ind.severity * ind.confidence
            for ind in indicators
        ]
        
        # Average with boost for multiple indicators
        base_score = np.mean(weighted_scores)
        
        # Boost if multiple types detected
        num_types = len(set(ind.type for ind in indicators))
        type_boost = min(num_types * 0.1, 0.3)  # Max 30% boost
        
        final_score = min(base_score + type_boost, 1.0)
        
        return final_score
    
    def _calculate_overall_confidence(self, indicators: List[CheatingIndicator]) -> float:
        """Calculate overall confidence in cheating detection."""
        if not indicators:
            return 1.0  # High confidence in "no cheating"
        
        return float(np.mean([ind.confidence for ind in indicators]))
    
    def _generate_summary(self, score: float, indicators: List[CheatingIndicator]) -> str:
        """Generate human-readable summary of cheating analysis."""
        if score < 0.3:
            return "✅ No significant cheating indicators detected. Answer appears authentic."
        elif score < 0.6:
            summary = f"⚠️ Some suspicious patterns detected ({len(indicators)} indicators). "
            summary += "Recommend manual review. "
        else:
            summary = f"🚨 HIGH RISK: Strong cheating indicators detected ({len(indicators)} indicators). "
        
        # List main concerns
        types = set(ind.type for ind in indicators)
        summary += f"Concerns: {', '.join(types)}."
        
        return summary

# Global instance
cheating_detector = CheatingDetector()