"""
Emotion Detector using DeepFace and OpenCV.

Analyzes facial expressions from video to detect 7 emotions:
angry, disgust, fear, happy, sad, surprise, neutral
"""

import cv2
import numpy as np
from deepface import DeepFace
import logging
from typing import List, Dict, Optional
from pathlib import Path
import os

logger = logging.getLogger(__name__)

class EmotionDetector:
    """
    Detects emotions from video using facial expression recognition.
    
    Uses DeepFace with pre-trained CNN models (VGG-Face, Facenet).
    Processes videos at configurable frame rate (default: 1 FPS).
    """
    
    def __init__(
        self,
        sample_rate: float = 1.0,  # Process 1 frame per second
        model_name: str = "Facenet",  # Options: VGG-Face, Facenet, OpenFace
        confidence_threshold: float = 0.6  # Minimum confidence to report
    ):
        """
        Initialize emotion detector.
        
        Args:
            sample_rate: Frames per second to process (lower = faster)
            model_name: DeepFace model to use
            confidence_threshold: Minimum confidence threshold
        """
        self.sample_rate = sample_rate
        self.model_name = model_name
        self.confidence_threshold = confidence_threshold
        
        logger.info(f"Emotion detector initialized (model={model_name}, rate={sample_rate} FPS)")
    
    def analyze_video(self, video_path: str) -> List[Dict]:
        """
        Analyze emotions throughout a video.
        
        Args:
            video_path: Path to video file (MP4, AVI, etc.)
            
        Returns:
            List of emotion results with timestamps
            [
                {
                    "timestamp": "00:03",
                    "emotion": "happy",
                    "confidence": 0.85,
                    "all_emotions": {"happy": 0.85, "neutral": 0.10, ...}
                },
                ...
            ]
        """
        video_path = Path(video_path)
        
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        logger.info(f"Analyzing emotions from video: {video_path}")
        
        # Open video
        cap = cv2.VideoCapture(str(video_path))
        
        if not cap.isOpened():
            raise RuntimeError(f"Failed to open video: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        logger.info(f"Video: {fps} FPS, {total_frames} frames, {duration:.1f}s duration")
        
        # Calculate frame interval (e.g., sample_rate=1.0 → every 30th frame at 30 FPS)
        frame_interval = int(fps / self.sample_rate) if self.sample_rate > 0 else 30
        
        emotion_timeline = []
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Only process frames at specified interval
            if frame_count % frame_interval == 0:
                timestamp = self._format_timestamp(frame_count / fps)
                
                # Analyze this frame
                emotion_result = self._analyze_frame(frame, timestamp)
                
                if emotion_result:
                    emotion_timeline.append(emotion_result)
            
            frame_count += 1
        
        cap.release()
        
        logger.info(f"✅ Emotion analysis complete: {len(emotion_timeline)} frames analyzed")
        return emotion_timeline
    
    def _analyze_frame(self, frame: np.ndarray, timestamp: str) -> Optional[Dict]:
        """
        Analyze emotions in a single video frame.
        
        Args:
            frame: Video frame (numpy array)
            timestamp: Time in video (e.g., "00:15")
            
        Returns:
            Emotion result dict or None if no face detected
        """
        try:
            # DeepFace.analyze expects BGR image (OpenCV format)
            # enforce_detection=False allows processing even if face is small/unclear
            result = DeepFace.analyze(
                frame,
                actions=['emotion'],
                enforce_detection=False,
                detector_backend='opencv',  # Fastest detector
                silent=True
            )
            
            # DeepFace returns a list (one entry per face)
            if isinstance(result, list):
                result = result[0]  # Take first face
            
            emotion_scores = result['emotion']
            dominant_emotion = result['dominant_emotion']
            confidence = emotion_scores[dominant_emotion] / 100.0  # Convert to 0-1
            
            # Only return if confidence exceeds threshold
            if confidence < self.confidence_threshold:
                logger.debug(f"Low confidence at {timestamp}: {confidence:.2f}")
                return None
            
            return {
                "timestamp": timestamp,
                "emotion": dominant_emotion,
                "confidence": round(confidence, 2),
                "all_emotions": {
                    k: round(v / 100.0, 2) for k, v in emotion_scores.items()
                }
            }
        
        except Exception as e:
            logger.debug(f"No face detected at {timestamp}: {e}")
            return None
    
    def get_dominant_emotions(self, emotion_timeline: List[Dict]) -> Dict[str, float]:
        """
        Calculate overall emotion distribution from timeline.
        
        Args:
            emotion_timeline: List of emotion results from analyze_video()
            
        Returns:
            Dictionary with emotion percentages
            {"happy": 0.45, "neutral": 0.30, ...}
        """
        if not emotion_timeline:
            return {}
        
        # Count occurrences of each emotion
        emotion_counts = {}
        for result in emotion_timeline:
            emotion = result['emotion']
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # Convert to percentages
        total = len(emotion_timeline)
        emotion_percentages = {
            emotion: round(count / total, 2)
            for emotion, count in emotion_counts.items()
        }
        
        return emotion_percentages
    
    def _format_timestamp(self, seconds: float) -> str:
        """
        Format seconds as MM:SS timestamp.
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Formatted string (e.g., "02:35")
        """
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

# Global instance
emotion_detector = EmotionDetector()