"""
Prosody Analyzer using librosa.

Prosody = rhythm, stress, and intonation of speech.
We measure: speaking rate, pauses, energy (loudness), pitch variance.
"""

import librosa
import numpy as np
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class ProsodyAnalyzer:
    """
    Analyzes speech prosody from audio files.
    
    Metrics:
    - Speaking rate (words per minute)
    - Pause ratio (fraction of time spent silent)
    - Energy mean/variance (loudness patterns)
    - Pitch mean/variance (tone variability)
    """
    
    def analyze(self, audio_path: str, transcript: str) -> Dict[str, float]:
        """
        Extract prosody features from audio.
        
        Args:
            audio_path: Path to audio file (WAV preferred)
            transcript: Text transcript (used to count words)
            
        Returns:
            Dictionary of prosody metrics
        """
        logger.info(f"Analyzing prosody: {audio_path}")
        
        # Load audio
        y, sr = librosa.load(audio_path, sr=16000)  # Resample to 16kHz
        duration = librosa.get_duration(y=y, sr=sr)
        
        # 1. Speaking rate (words per minute)
        word_count = len(transcript.split())
        speaking_rate = (word_count / duration) * 60 if duration > 0 else 0
        
        # 2. Pause detection
        # Use RMS energy to detect silent regions
        rms = librosa.feature.rms(y=y)[0]
        threshold = np.mean(rms) * 0.3  # 30% of mean energy
        silent_frames = np.sum(rms < threshold)
        total_frames = len(rms)
        pause_ratio = silent_frames / total_frames if total_frames > 0 else 0
        
        # 3. Energy (loudness) statistics
        energy_mean = float(np.mean(rms))
        energy_variance = float(np.var(rms))
        
        # 4. Pitch statistics (using yin algorithm)
        try:
            f0 = librosa.yin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
            # Remove unvoiced frames (pitch=0)
            f0_voiced = f0[f0 > 0]
            
            if len(f0_voiced) > 0:
                pitch_mean = float(np.mean(f0_voiced))
                pitch_variance = float(np.var(f0_voiced))
            else:
                pitch_mean = 0.0
                pitch_variance = 0.0
        except Exception as e:
            logger.warning(f"Pitch extraction failed: {e}")
            pitch_mean = 0.0
            pitch_variance = 0.0
        
        metrics = {
            "speaking_rate": round(speaking_rate, 1),
            "pause_ratio": round(pause_ratio, 3),
            "energy_mean": round(energy_mean, 4),
            "energy_variance": round(energy_variance, 4),
            "pitch_mean": round(pitch_mean, 1),
            "pitch_variance": round(pitch_variance, 1),
            "duration": round(duration, 2)
        }
        
        logger.info(f"✅ Prosody analysis complete: {metrics}")
        return metrics

# Global instance
prosody_analyzer = ProsodyAnalyzer()