"""Answer evaluation service using semantic similarity and optional key-point rubric."""

import re
from typing import Dict, List, Optional
from collections import Counter

# Try to import sentence transformers for semantic similarity
try:
    from sentence_transformers import SentenceTransformer, util
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class AnswerEvaluator:
    """Evaluates candidate answers against expected responses."""
    
    def __init__(self, use_ml: bool = True):
        """
        Initialize answer evaluator.
        
        Args:
            use_ml: Use ML-based semantic similarity (requires sentence-transformers)
        """
        self.use_ml = use_ml and SENTENCE_TRANSFORMERS_AVAILABLE
        self.model = None
        
        if self.use_ml:
            try:
                
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                print(f"Failed to load sentence transformer: {e}")
                self.use_ml = False
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        # Lowercase
        text = text.lower()
        return text
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text."""
        # Simple keyword extraction (remove common stopwords)
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'are', 'was', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this',
            'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
        
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [w for w in words if w not in stopwords and len(w) > 2]
        return keywords
    
    def _calculate_keyword_overlap(self, user_text: str, expected_text: str) -> float:
        """Calculate keyword overlap between user and expected answers."""
        user_keywords = set(self._extract_keywords(user_text))
        expected_keywords = set(self._extract_keywords(expected_text))
        
        if not expected_keywords:
            return 0.0
        
        overlap = len(user_keywords & expected_keywords)
        overlap_ratio = overlap / len(expected_keywords)
        
        return min(overlap_ratio, 1.0)
    
    def _calculate_semantic_similarity(self, user_text: str, expected_text: str) -> float:
        """Calculate semantic similarity using ML model."""
        if not self.use_ml or not self.model:
            return 0.0
        
        # Encode texts
        user_emb = self.model.encode(user_text, convert_to_tensor=True)
        expected_emb = self.model.encode(expected_text, convert_to_tensor=True)
        
        # Calculate cosine similarity
        similarity = util.cos_sim(user_emb, expected_emb).item()
        
        return max(0.0, min(similarity, 1.0))

    def _score_key_points(self, user_text: str, key_points: List[str]) -> float:
        """Score coverage of key points (case-insensitive substring match)."""
        if not key_points:
            return 0.0
        user_low = user_text.lower()
        hits = 0
        total = 0
        for kp in key_points:
            kp = (kp or "").strip().lower()
            if not kp:
                continue
            total += 1
            # simple containment; can be improved to fuzzy match later
            if kp in user_low:
                hits += 1
        if total == 0:
            return 0.0
        return min(1.0, hits / total)
    
    def _get_feedback(self, score: float, keyword_score: float) -> Dict[str, str]:
        """Generate qualitative feedback based on scores."""
        if score >= 0.8:
            level = "excellent"
            message = "Outstanding answer! You demonstrated strong understanding of the concepts."
            color = "#22c55e"  # green
        elif score >= 0.6:
            level = "good"
            message = "Good answer! You covered the main points well."
            color = "#3b82f6"  # blue
        elif score >= 0.4:
            level = "fair"
            message = "Fair answer. Consider elaborating more on key concepts."
            color = "#f59e0b"  # orange
        else:
            level = "needs_improvement"
            message = "Your answer could be improved. Review the expected answer and try to cover more key points."
            color = "#ef4444"  # red
        
        return {
            "level": level,
            "message": message,
            "color": color
        }
    
    def evaluate(
        self,
        user_answer: str,
        expected_answer: str,
        question: str = "",
        key_points: Optional[List[str]] = None
    ) -> Dict:
        """
        Evaluate user answer against expected answer.
        
        Args:
            user_answer: User's spoken/transcribed answer
            expected_answer: Expected answer or guidance
            question: Original question (optional, for context)
        
        Returns:
            Dictionary with:
            - score: Overall score (0-100)
            - semantic_score: ML-based similarity (0-100) 
            - keyword_score: Keyword overlap score (0-100)
            - feedback: Qualitative feedback
            - component_scores: Optional detailed scores (coverage/semantic/keywords)
            - method: Scoring approach used
        """
        # Preprocess
        user_clean = self._preprocess_text(user_answer)
        expected_clean = self._preprocess_text(expected_answer)
        
        # Handle empty inputs
        if not user_clean:
            return {
                "score": 0,
                "semantic_score": 0,
                "keyword_score": 0,
                "feedback": {
                    "level": "needs_improvement",
                    "message": "No answer provided.",
                    "color": "#ef4444"
                },
                "method": "empty"
            }
        
        if not expected_clean:
            # No expected answer - just check if user provided something meaningful
            word_count = len(user_clean.split())
            base_score = min(100, word_count * 10)  # 10 points per word, max 100
            return {
                "score": base_score,
                "semantic_score": 0,
                "keyword_score": 0,
                "feedback": self._get_feedback(base_score / 100, 0),
                "method": "length_based"
            }
        
        # Calculate keyword overlap
        keyword_score = self._calculate_keyword_overlap(user_clean, expected_clean)
        
        # Calculate semantic similarity if ML available
        semantic_score = 0.0
        if self.use_ml:
            semantic_score = self._calculate_semantic_similarity(user_clean, expected_clean)
            if key_points:
                coverage = self._score_key_points(user_clean, key_points)
                # Weighted average when rubric present: 60% coverage, 30% semantic, 10% keyword
                overall_score = (coverage * 0.6) + (semantic_score * 0.3) + (keyword_score * 0.1)
                method = "ml_semantic_rubric"
            else:
                # Weighted average: 70% semantic, 30% keyword
                overall_score = (semantic_score * 0.7) + (keyword_score * 0.3)
                method = "ml_semantic"
        else:
            # Fallback to keyword-based with length bonus
            word_count = len(user_clean.split())
            length_bonus = min(0.3, word_count / 100)  # Up to 30% bonus for length
            if key_points:
                coverage = self._score_key_points(user_clean, key_points)
                overall_score = (coverage * 0.8) + (keyword_score * 0.2)
                # small bonus for reasonable length
                overall_score = min(1.0, overall_score + length_bonus * 0.2)
                method = "rubric_keyword_based"
            else:
                overall_score = (keyword_score * 0.7) + length_bonus
                method = "keyword_based"
        
        # Convert to 0-100 scale
        score_percent = int(overall_score * 100)
        semantic_percent = int(semantic_score * 100)
        keyword_percent = int(keyword_score * 100)
        
        result = {
            "score": score_percent,
            "semantic_score": semantic_percent,
            "keyword_score": keyword_percent,
            "feedback": self._get_feedback(overall_score, keyword_score),
            "method": method
        }

        if key_points:
            result["component_scores"] = {
                "coverage": int(self._score_key_points(user_clean, key_points) * 100),
                "semantic": semantic_percent,
                "keywords": keyword_percent,
            }

        return result


# Global instance
_evaluator: AnswerEvaluator = None


def get_answer_evaluator() -> AnswerEvaluator:
    """Get or create global answer evaluator instance."""
    global _evaluator
    if _evaluator is None:
        _evaluator = AnswerEvaluator()
    return _evaluator
