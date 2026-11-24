"""
Voice Stress Analyzer using Praat-Parselmouth.

Analyzes voice quality to detect stress/anxiety indicators:
- Jitter: Pitch instability (higher = more stress)
- Shimmer: Amplitude instability
- HNR: Harmonics-to-Noise Ratio (lower = more stress)
"""

import parselmouth
from parselmouth.praat import call
import numpy as np
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class StressAnalyzer:
    """
    Analyzes voice stress indicators from audio.
    
    Based on research in speech pathology and psychology.
    Stress manifests as increased pitch variability and voice quality issues.
    """
    
    def analyze(self, audio_path: str) -> Dict[str, float]:
        """
        Extract voice stress metrics from audio.
        
        Args:
            audio_path: Path to audio file (WAV preferred)
            
        Returns:
            Dictionary with stress metrics:
            - stress_score: Overall stress level (0-1, higher = more stressed)
            - pitch_mean: Average pitch in Hz
            - pitch_variance: Pitch variability
            - jitter: Local pitch perturbation (instability)
            - shimmer: Local amplitude perturbation
            - hnr: Harmonics-to-Noise Ratio (voice quality)
        """
        logger.info(f"Analyzing voice stress: {audio_path}")
        
        try:
            # Load audio using Parselmouth (Praat wrapper)
            sound = parselmouth.Sound(audio_path)
            
            # Extract pitch (fundamental frequency F0)
            pitch = sound.to_pitch()
            
            # Get pitch values
            pitch_values = pitch.selected_array['frequency']
            pitch_values = pitch_values[pitch_values > 0]  # Remove unvoiced frames
            
            if len(pitch_values) == 0:
                logger.warning("No voiced segments found in audio")
                return self._get_default_metrics()
            
            # 1. Pitch statistics
            pitch_mean = float(np.mean(pitch_values))
            pitch_std = float(np.std(pitch_values))
            pitch_variance = pitch_std ** 2
            
            # 2. Jitter (local pitch perturbation)
            # Measures cycle-to-cycle pitch variability
            # Normal speech: 0.5-1.5%, Stressed: >2%
            point_process = call(sound, "To PointProcess (periodic, cc)", 75, 600)
            jitter = call(point_process, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3)
            
            # 3. Shimmer (local amplitude perturbation)
            # Measures cycle-to-cycle amplitude variability
            # Normal speech: 2-5%, Stressed: >6%
            shimmer = call([sound, point_process], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
            
            # 4. HNR (Harmonics-to-Noise Ratio)
            # Measures voice quality (clarity vs. breathiness)
            # Normal speech: 15-25 dB, Stressed: <12 dB
            harmonicity = sound.to_harmonicity()
            hnr = call(harmonicity, "Get mean", 0, 0)
            
            # 5. Calculate overall stress score (0-1)
            stress_score = self._calculate_stress_score(
                jitter, shimmer, hnr, pitch_std, pitch_mean
            )
            
            metrics = {
                "stress_score": round(stress_score, 3),
                "pitch_mean": round(pitch_mean, 1),
                "pitch_variance": round(pitch_variance, 1),
                "jitter": round(jitter * 100, 3),  # Convert to percentage
                "shimmer": round(shimmer * 100, 3),  # Convert to percentage
                "hnr": round(hnr, 2)
            }
            
            logger.info(f"✅ Stress analysis complete: stress_score={stress_score:.2f}")
            return metrics
        
        except Exception as e:
            logger.error(f"Stress analysis failed: {e}")
            return self._get_default_metrics()
    
    def _calculate_stress_score(
        self,
        jitter: float,
        shimmer: float,
        hnr: float,
        pitch_std: float,
        pitch_mean: float
    ) -> float:
        """
        Calculate overall stress score from individual metrics.
        
        Weighted combination of:
        - High jitter → more stress
        - High shimmer → more stress
        - Low HNR → more stress
        - High pitch variance → more stress
        
        Returns:
            Stress score between 0 (calm) and 1 (very stressed)
        """
        # Normalize jitter (0.5% = calm, 3% = very stressed)
        jitter_score = min((jitter * 100 - 0.5) / 2.5, 1.0)
        jitter_score = max(jitter_score, 0.0)
        
        # Normalize shimmer (3% = calm, 8% = very stressed)
        shimmer_score = min((shimmer * 100 - 3.0) / 5.0, 1.0)
        shimmer_score = max(shimmer_score, 0.0)
        
        # Normalize HNR (25 dB = calm, 10 dB = very stressed)
        hnr_score = min((25 - hnr) / 15.0, 1.0)
        hnr_score = max(hnr_score, 0.0)
        
        # Normalize pitch variance
        # Expected std: 20-40 Hz for calm speech, >60 Hz for stressed
        pitch_var_score = min((pitch_std - 20) / 40, 1.0)
        pitch_var_score = max(pitch_var_score, 0.0)
        
        # Weighted combination (jitter and shimmer are most important)
        stress_score = (
            0.35 * jitter_score +
            0.30 * shimmer_score +
            0.20 * hnr_score +
            0.15 * pitch_var_score
        )
        
        return min(stress_score, 1.0)
    
    def _get_default_metrics(self) -> Dict[str, float]:
        """
        Return default metrics when analysis fails.
        
        Returns:
            Dictionary with zero/neutral values
        """
        return {
            "stress_score": 0.0,
            "pitch_mean": 0.0,
            "pitch_variance": 0.0,
            "jitter": 0.0,
            "shimmer": 0.0,
            "hnr": 0.0
        }

# Global instance
stress_analyzer = StressAnalyzer()