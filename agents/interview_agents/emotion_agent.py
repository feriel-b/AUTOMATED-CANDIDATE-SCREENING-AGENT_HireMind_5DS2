"""
Emotion Detector Agent using Ollama Phi4-Mini.
"""

from langchain_core.tools import Tool
from typing import List, Dict
import sys
import os
import json

#sys.path.append(os.path.join(os.path.dirname(__file__), '../../services/interview_simulator'))

from services.interview_simulator.emotion_detector import emotion_detector
from core.base_agent import InterviewBaseAgent

class EmotionAgent(InterviewBaseAgent):
    """Agent specialized in emotion detection from video."""
    
    def __init__(self):
        super().__init__(agent_name="Emotion_Analyst", temperature=0.5)
    
    def _define_tools(self) -> List:
        return [
            Tool(
                name="detect_emotions",
                func=self._detect_emotions,
                description="Detect facial emotions throughout video. Input: video file path"
            ),
            Tool(
                name="analyze_emotion_trends",
                func=self._analyze_trends,
                description="Identify emotion patterns over time. Input: JSON emotion timeline"
            ),
            Tool(
                name="flag_concerning_emotions",
                func=self._flag_concerns,
                description="Flag concerning emotional patterns. Input: JSON emotion data"
            )
        ]
    
    def _get_system_prompt(self) -> str:
        return """You are an emotion recognition specialist.

Your capabilities:
- Detect 7 basic emotions: happy, sad, angry, fear, surprise, disgust, neutral
- Track emotional changes over time
- Identify emotional authenticity vs. forced expressions
- Flag concerning patterns (excessive fear/anger)

Context matters: Some nervousness is normal in interviews."""
    
    def _detect_emotions(self, video_path: str) -> str:
        """Detect emotions from video."""
        try:
            emotions = emotion_detector.analyze_video(video_path)
            return json.dumps(emotions, indent=2)
        except Exception as e:
            return f"Emotion detection error: {str(e)}"
    
    def _analyze_trends(self, emotion_timeline_json: str) -> str:
        """Analyze emotion trends."""
        try:
            timeline = json.loads(emotion_timeline_json)
            
            if not timeline:
                return "No emotion data to analyze"
            
            # Count dominant emotions
            emotion_counts = {}
            for frame in timeline:
                emotion = frame.get("dominant_emotion", "neutral")
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
            total = len(timeline)
            trends = {k: f"{(v/total)*100:.1f}%" for k, v in emotion_counts.items()}
            
            return f"Emotion distribution: {json.dumps(trends, indent=2)}"
            
        except Exception as e:
            return f"Trend analysis error: {str(e)}"
    
    def _flag_concerns(self, emotions_json: str) -> str:
        """Flag concerning patterns."""
        try:
            emotions = json.loads(emotions_json)
            concerns = []
            
            # Check for excessive negative emotions
            negative_count = sum(1 for e in emotions if e.get("dominant_emotion") in ["angry", "fear", "sad"])
            if negative_count / len(emotions) > 0.5:
                concerns.append("High level of negative emotions detected")
            
            # Check for sustained fear/anxiety
            fear_count = sum(1 for e in emotions if e.get("dominant_emotion") == "fear")
            if fear_count / len(emotions) > 0.3:
                concerns.append("Sustained anxiety/fear detected")
            
            return json.dumps({"concerns": concerns if concerns else ["No concerning patterns"]})
            
        except Exception as e:
            return f"Concern flagging error: {str(e)}"