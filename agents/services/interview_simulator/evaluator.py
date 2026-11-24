"""
Answer Evaluator.

Evaluates interview answers on:
1. Relevance: How well the answer matches the question
2. Clarity: Speech quality and coherence
3. Overall score: Weighted combination
"""

import logging
from typing import Dict, List
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class AnswerEvaluator:
    """
    Evaluates interview answers using semantic similarity and prosody metrics.
    
    Scoring components:
    - Relevance: Semantic similarity between answer and expected keywords
    - Clarity: Based on speaking rate, pauses, and transcript length
    - Overall: Weighted combination
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize evaluator with sentence transformer model.
        
        Args:
            model_name: Sentence transformer model for embeddings
        """
        logger.info(f"Loading sentence transformer model: {model_name}")
        self.model = SentenceTransformer(model_name)
        logger.info("✅ Evaluator initialized")
    
    def evaluate_answer(
        self,
        question: Dict,
        transcript: str,
        prosody_metrics: Dict,
        stress_metrics: Dict = None,
        emotion_timeline: List[Dict] = None
    ) -> Dict:
        """
        Evaluate an interview answer comprehensively.
        
        Args:
            question: Question dict from Q&A bank
            transcript: Speech-to-text transcript
            prosody_metrics: Speaking rate, pauses, energy
            stress_metrics: Voice stress indicators (optional)
            emotion_timeline: Emotion detection results (optional)
            
        Returns:
            Dictionary with scores and feedback
        """
        logger.info(f"Evaluating answer for question ID {question['id']}")
        
        # 1. Relevance score (semantic similarity)
        relevance_score = self._calculate_relevance(question, transcript)
        
        # 2. Clarity score (speech quality)
        clarity_score = self._calculate_clarity(transcript, prosody_metrics)
        
        # 3. Overall score (weighted average)
        overall_score = (0.6 * relevance_score) + (0.4 * clarity_score)
        
        # 4. Generate feedback
        feedback = self._generate_feedback(
            relevance_score,
            clarity_score,
            prosody_metrics,
            stress_metrics,
            emotion_timeline
        )
        
        return {
            "relevance_score": round(relevance_score, 1),
            "clarity_score": round(clarity_score, 1),
            "overall_score": round(overall_score, 1),
            "feedback": feedback
        }
    
    def _calculate_relevance(self, question: Dict, transcript: str) -> float:
        """
        Calculate semantic relevance between question and answer.
        
        Uses sentence embeddings to measure how similar the answer is
        to the expected keywords and question topic.
        
        Args:
            question: Question dict with expected_keywords
            transcript: Answer transcript
            
        Returns:
            Relevance score (0-100)
        """
        if not transcript or len(transcript.split()) < 3:
            logger.warning("Transcript too short for relevance evaluation")
            return 0.0
        
        # Get expected keywords from question
        expected_keywords = question.get('expected_keywords', [])
        
        if not expected_keywords:
            # Fallback: compare answer to question text
            logger.debug("No expected keywords, using question text")
            expected_keywords = [question['question']]
        
        # Create embeddings
        answer_embedding = self.model.encode(transcript, convert_to_tensor=True)
        
        # Calculate similarity with each keyword
        similarities = []
        for keyword in expected_keywords:
            keyword_embedding = self.model.encode(keyword, convert_to_tensor=True)
            similarity = self._cosine_similarity(answer_embedding, keyword_embedding)
            similarities.append(similarity)
        
        # Use max similarity (answer should cover at least some keywords)
        max_similarity = max(similarities) if similarities else 0.0
        
        # Convert to 0-100 scale
        # Cosine similarity ranges from -1 to 1, but we expect 0.2 to 0.8 for relevant answers
        # Map [0.2, 0.8] → [0, 100]
        relevance_score = ((max_similarity - 0.2) / 0.6) * 100
        relevance_score = max(0, min(100, relevance_score))  # Clamp to [0, 100]
        
        logger.debug(f"Relevance: {relevance_score:.1f} (similarity={max_similarity:.3f})")
        return relevance_score
    
    def _calculate_clarity(self, transcript: str, prosody_metrics: Dict) -> float:
        """
        Calculate speech clarity based on transcript and prosody.
        
        Factors:
        - Transcript length (too short = incomplete, too long = rambling)
        - Speaking rate (too fast = rushed, too slow = uncertain)
        - Pause ratio (too many pauses = uncertain)
        
        Args:
            transcript: Answer text
            prosody_metrics: Speaking rate, pauses, etc.
            
        Returns:
            Clarity score (0-100)
        """
        score = 100.0  # Start with perfect score
        
        # 1. Transcript length penalty
        word_count = len(transcript.split())
        
        if word_count < 10:
            score -= 30  # Very short answer
        elif word_count < 20:
            score -= 15  # Short answer
        elif word_count > 300:
            score -= 20  # Too long (rambling)
        elif word_count > 200:
            score -= 10  # Somewhat long
        
        # 2. Speaking rate penalty
        speaking_rate = prosody_metrics.get('speaking_rate', 0)
        
        if speaking_rate < 80:
            score -= 20  # Too slow (uncertain)
        elif speaking_rate < 100:
            score -= 10  # Slow
        elif speaking_rate > 200:
            score -= 20  # Too fast (nervous)
        elif speaking_rate > 180:
            score -= 10  # Fast
        
        # 3. Pause ratio penalty
        pause_ratio = prosody_metrics.get('pause_ratio', 0)
        
        if pause_ratio > 0.3:
            score -= 20  # Too many pauses
        elif pause_ratio > 0.2:
            score -= 10  # Some pauses
        
        # 4. Energy variance (monotone penalty)
        energy_variance = prosody_metrics.get('energy_variance', 0)
        
        if energy_variance < 0.01:
            score -= 10  # Very monotone
        
        clarity_score = max(0, min(100, score))  # Clamp to [0, 100]
        
        logger.debug(f"Clarity: {clarity_score:.1f}")
        return clarity_score
    
    def _generate_feedback(
        self,
        relevance_score: float,
        clarity_score: float,
        prosody_metrics: Dict,
        stress_metrics: Dict = None,
        emotion_timeline: List[Dict] = None
    ) -> List[str]:
        """
        Generate human-readable feedback based on scores.
        
        Returns:
            List of feedback strings with emoji indicators
        """
        feedback = []
        
        # Relevance feedback
        if relevance_score >= 80:
            feedback.append("✅ Excellent answer - directly addressed the question")
        elif relevance_score >= 60:
            feedback.append("👍 Good answer - covered key points")
        elif relevance_score >= 40:
            feedback.append("💡 Answer somewhat relevant - consider adding more specific examples")
        else:
            feedback.append("⚠️ Answer may not fully address the question - review question requirements")
        
        # Clarity feedback
        if clarity_score >= 80:
            feedback.append("✅ Very clear and well-structured response")
        elif clarity_score >= 60:
            feedback.append("👍 Clear communication")
        else:
            feedback.append("💡 Try to speak more clearly and avoid long pauses")
        
        # Speaking rate feedback
        speaking_rate = prosody_metrics.get('speaking_rate', 0)
        if speaking_rate > 180:
            feedback.append("⚡ Speaking a bit fast - try to slow down for clarity")
        elif speaking_rate < 100:
            feedback.append("🐌 Speaking slowly - consider increasing your pace slightly")
        
        # Pause feedback
        pause_ratio = prosody_metrics.get('pause_ratio', 0)
        if pause_ratio > 0.25:
            feedback.append("⏸️ Many pauses detected - prepare your thoughts before speaking")
        
        # Stress feedback
        if stress_metrics:
            stress_score = stress_metrics.get('stress_score', 0)
            if stress_score > 0.6:
                feedback.append("😰 High stress detected in voice - take deep breaths and relax")
            elif stress_score > 0.4:
                feedback.append("😌 Slight nervousness detected - this is normal for interviews")
        
        # Emotion feedback
        if emotion_timeline:
            # Calculate dominant emotion
            emotion_counts = {}
            for result in emotion_timeline:
                emotion = result['emotion']
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
            if emotion_counts:
                dominant_emotion = max(emotion_counts, key=emotion_counts.get)
                
                if dominant_emotion == 'happy':
                    feedback.append("😊 Positive facial expressions detected - great enthusiasm!")
                elif dominant_emotion in ['fear', 'sad']:
                    feedback.append("💡 Try to maintain a confident facial expression")
                elif dominant_emotion == 'neutral':
                    feedback.append("😐 Neutral expression - consider showing more engagement")
        
        return feedback
    
    def _cosine_similarity(self, emb1, emb2) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            emb1, emb2: Sentence embeddings (tensors)
            
        Returns:
            Similarity score (-1 to 1)
        """
        import torch
        return torch.nn.functional.cosine_similarity(emb1, emb2, dim=0).item()

# Global instance
answer_evaluator = AnswerEvaluator()
# Export as 'evaluator' for compatibility
evaluator = answer_evaluator