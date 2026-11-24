"""
Timing Analyzer for Cheating Detection.

Detects unnatural pause patterns that suggest:
- Typing into ChatGPT (regular 3-5s pauses)
- Reading pre-written text (unnaturally fluent)
- External assistance (long pauses while getting help)
"""

import librosa
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class TimingAnalyzer:
    """
    Analyze speech timing patterns for cheating indicators.
    
    Detects:
    1. Typing patterns (regular pauses every few words)
    2. Unnatural fluency (reading from script)
    3. Long pauses (getting external help)
    """
    
    def __init__(self):
        """Initialize timing analyzer."""
        logger.info("Initializing Timing Analyzer...")
        
        # Parameters
        self.frame_length = 2048
        self.hop_length = 512
        self.silence_threshold = 0.01  # Energy threshold for silence
        self.min_pause_duration = 0.5  # Minimum pause length (seconds)
        
        # Typing pattern detection
        self.TYPING_PAUSE_MIN = 2.0  # seconds
        self.TYPING_PAUSE_MAX = 6.0  # seconds
        self.TYPING_REGULARITY_THRESHOLD = 0.3  # Low std = regular pattern
        
        # Fluency detection
        self.NATURAL_PAUSE_RATIO = 0.2  # Natural speech has ~20% pauses
        self.FLUENCY_THRESHOLD = 0.1  # <10% pauses = too fluent
        
        logger.info("✅ Timing Analyzer initialized")
    
    def analyze_pauses(
        self,
        audio_path: str,
        transcript: Optional[str] = None
    ) -> Dict:
        """
        Analyze pause patterns in audio.
        
        Args:
            audio_path: Path to audio file
            transcript: Optional transcript for word-level timing
            
        Returns:
            Pause analysis results
        """
        logger.info(f"Analyzing pause patterns: {audio_path}")
        
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=16000)
            duration = librosa.get_duration(y=y, sr=sr)
            
            if duration < 10.0:
                logger.warning("Audio too short for pause analysis")
                return self._get_default_result()
            
            # Detect pauses
            pauses = self._detect_pauses(y, sr)
            
            if len(pauses) < 3:
                logger.info("Insufficient pauses for pattern detection")
                return {
                    'typing_pattern_detected': False,
                    'too_fluent': True,
                    'avg_pause': 0.0,
                    'pause_ratio': 0.0,
                    'num_pauses': len(pauses)
                }
            
            # Calculate metrics
            pause_durations = [p['duration'] for p in pauses]
            pause_intervals = [p['interval'] for p in pauses]
            
            avg_pause = float(np.mean(pause_durations))
            std_pause = float(np.std(pause_durations))
            avg_interval = float(np.mean(pause_intervals))
            std_interval = float(np.std(pause_intervals))
            
            # Calculate pause ratio (pause time / total time)
            total_pause_time = sum(pause_durations)
            pause_ratio = total_pause_time / duration
            
            # Detect typing pattern
            typing_detected = self._detect_typing_pattern(
                pause_intervals,
                avg_interval,
                std_interval
            )
            
            # Detect unnatural fluency
            too_fluent = pause_ratio < self.FLUENCY_THRESHOLD
            
            result = {
                'typing_pattern_detected': typing_detected,
                'too_fluent': too_fluent,
                'avg_pause': round(avg_pause, 2),
                'std_pause': round(std_pause, 2),
                'avg_interval': round(avg_interval, 2),
                'std_interval': round(std_interval, 2),
                'pause_ratio': round(pause_ratio, 3),
                'num_pauses': len(pauses),
                'pause_timeline': pauses[:20]  # Sample for visualization
            }
            
            logger.info(f"✅ Timing analysis: typing={typing_detected}, fluent={too_fluent}")
            return result
            
        except Exception as e:
            logger.error(f"Timing analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return self._get_default_result()
    
    def _detect_pauses(
        self,
        y: np.ndarray,
        sr: int
    ) -> List[Dict]:
        """
        Detect pauses (silence periods) in audio.
        
        Args:
            y: Audio time series
            sr: Sample rate
            
        Returns:
            List of pause dicts with start, end, duration, interval
        """
        # Calculate frame-level energy (RMS)
        rms = librosa.feature.rms(
            y=y,
            frame_length=self.frame_length,
            hop_length=self.hop_length
        )[0]
        
        # Convert frame indices to time
        times = librosa.frames_to_time(
            np.arange(len(rms)),
            sr=sr,
            hop_length=self.hop_length
        )
        
        # Detect silence frames (below threshold)
        is_silence = rms < self.silence_threshold
        
        # Find contiguous silence regions
        pauses = []
        in_pause = False
        pause_start = 0
        last_speech_end = 0
        
        for i, (time, silent) in enumerate(zip(times, is_silence)):
            if silent and not in_pause:
                # Start of pause
                in_pause = True
                pause_start = time
            elif not silent and in_pause:
                # End of pause
                in_pause = False
                pause_end = time
                pause_duration = pause_end - pause_start
                
                # Only record significant pauses
                if pause_duration >= self.min_pause_duration:
                    interval = pause_start - last_speech_end
                    
                    pauses.append({
                        'start': round(pause_start, 2),
                        'end': round(pause_end, 2),
                        'duration': round(pause_duration, 2),
                        'interval': round(max(interval, 0), 2)  # Time since last pause
                    })
                
                last_speech_end = pause_end
        
        logger.debug(f"Detected {len(pauses)} significant pauses")
        return pauses
    
    def _detect_typing_pattern(
        self,
        pause_intervals: List[float],
        avg_interval: float,
        std_interval: float
    ) -> bool:
        """
        Detect if pause pattern suggests typing into ChatGPT.
        
        Typing pattern characteristics:
        - Regular intervals (3-5 seconds between pauses)
        - Low variance (mechanical regularity)
        - Multiple occurrences
        
        Args:
            pause_intervals: List of inter-pause intervals
            avg_interval: Average interval
            std_interval: Standard deviation of intervals
            
        Returns:
            True if typing pattern detected
        """
        if len(pause_intervals) < 4:
            return False
        
        # Check if intervals are in typing range
        in_typing_range = [
            self.TYPING_PAUSE_MIN <= interval <= self.TYPING_PAUSE_MAX
            for interval in pause_intervals
        ]
        
        typing_ratio = sum(in_typing_range) / len(in_typing_range)
        
        # Check regularity (low coefficient of variation)
        cv = std_interval / avg_interval if avg_interval > 0 else 1.0
        is_regular = cv < self.TYPING_REGULARITY_THRESHOLD
        
        # Typing pattern if:
        # - Most intervals in typing range
        # - Regular pattern
        typing_detected = typing_ratio > 0.6 and is_regular
        
        if typing_detected:
            logger.info(f"Typing pattern detected: ratio={typing_ratio:.2f}, cv={cv:.2f}")
        
        return typing_detected
    
    def _get_default_result(self) -> Dict:
        """Return default result when analysis fails."""
        return {
            'typing_pattern_detected': False,
            'too_fluent': False,
            'avg_pause': 0.0,
            'std_pause': 0.0,
            'avg_interval': 0.0,
            'std_interval': 0.0,
            'pause_ratio': 0.0,
            'num_pauses': 0,
            'pause_timeline': []
        }

# Global instance
timing_analyzer = TimingAnalyzer()