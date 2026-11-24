"""
Perplexity-based AI Text Detection.

Uses linguistic features to detect AI-generated text (GPT, Claude, etc.)
"""

import re
from typing import Dict
import logging
import numpy as np

logger = logging.getLogger(__name__)

class PerplexityChecker:
    """
    Detect AI-generated text using perplexity and linguistic features.
    
    AI-generated text typically has:
    - Low perplexity (very predictable)
    - Uniform sentence length
    - Lack of grammatical errors
    - Overly formal vocabulary
    """
    
    def __init__(self):
        """Initialize perplexity checker."""
        logger.info("Initializing Perplexity Checker...")
        
        # Thresholds based on empirical testing
        self.LOW_PERPLEXITY_THRESHOLD = 30.0
        self.HIGH_UNIFORMITY_THRESHOLD = 0.15
        
        logger.info("✅ Perplexity Checker initialized")
    
    def check_text(self, text: str) -> Dict:
        """
        Check if text is likely AI-generated.
        
        Args:
            text: Text to analyze
            
        Returns:
            Analysis results with AI probability
        """
        logger.info("Checking text for AI generation...")
        
        # Calculate features
        perplexity = self._estimate_perplexity(text)
        uniformity = self._calculate_sentence_uniformity(text)
        formality = self._calculate_formality_score(text)
        error_rate = self._calculate_error_rate(text)
        
        # Calculate AI probability
        ai_probability = self._calculate_ai_probability(
            perplexity, uniformity, formality, error_rate
        )
        
        is_likely_ai = ai_probability > 0.6
        
        return {
            'is_likely_ai': is_likely_ai,
            'ai_probability': round(ai_probability, 3),
            'perplexity': round(perplexity, 2),
            'uniformity': round(uniformity, 3),
            'formality': round(formality, 3),
            'error_rate': round(error_rate, 3)
        }
    
    def _estimate_perplexity(self, text: str) -> float:
        """
        Estimate perplexity using simple n-gram model.
        
        True perplexity requires a language model, but we can approximate
        using vocabulary diversity and word frequency.
        
        Args:
            text: Input text
            
        Returns:
            Estimated perplexity score
        """
        words = text.lower().split()
        
        if len(words) < 10:
            return 100.0  # Default high perplexity for short text
        
        # Calculate vocabulary diversity (type-token ratio)
        unique_words = len(set(words))
        total_words = len(words)
        diversity = unique_words / total_words
        
        # Calculate bigram entropy (simplified)
        bigrams = [tuple(words[i:i+2]) for i in range(len(words)-1)]
        unique_bigrams = len(set(bigrams))
        bigram_diversity = unique_bigrams / max(len(bigrams), 1)
        
        # Estimate perplexity
        # Higher diversity → higher perplexity (more human-like)
        perplexity = 100 * (diversity + bigram_diversity) / 2
        
        return perplexity
    
    def _calculate_sentence_uniformity(self, text: str) -> float:
        """
        Calculate sentence length uniformity.
        
        AI text tends to have very uniform sentence lengths.
        
        Args:
            text: Input text
            
        Returns:
            Uniformity score (0=varied, 1=uniform)
        """
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 2:
            return 0.0
        
        lengths = [len(s.split()) for s in sentences]
        
        # Calculate coefficient of variation (lower = more uniform)
        mean_length = np.mean(lengths)
        std_length = np.std(lengths)
        
        if mean_length == 0:
            return 0.0
        
        cv = std_length / mean_length
        
        # Convert to uniformity score (inverse of variation)
        uniformity = max(0, 1 - cv)
        
        return uniformity
    
    def _calculate_formality_score(self, text: str) -> float:
        """
        Calculate formality score.
        
        AI text tends to be more formal.
        
        Args:
            text: Input text
            
        Returns:
            Formality score (0=informal, 1=formal)
        """
        # Formal indicators
        formal_words = {
            'however', 'therefore', 'thus', 'furthermore', 'moreover',
            'consequently', 'nevertheless', 'accordingly', 'hence',
            'utilize', 'implement', 'facilitate', 'demonstrate'
        }
        
        # Informal indicators
        informal_words = {
            'gonna', 'wanna', 'kinda', 'sorta', 'yeah', 'nope',
            'pretty', 'really', 'very', 'totally', 'basically'
        }
        
        words = set(text.lower().split())
        
        formal_count = len(words & formal_words)
        informal_count = len(words & informal_words)
        
        total = formal_count + informal_count
        
        if total == 0:
            return 0.5  # Neutral
        
        formality = formal_count / total
        
        return formality
    
    def _calculate_error_rate(self, text: str) -> float:
        """
        Calculate grammatical error rate.
        
        AI text typically has very few errors.
        
        Args:
            text: Input text
            
        Returns:
            Error rate (0=no errors, 1=many errors)
        """
        # Simple heuristics (real implementation would use grammar checker)
        
        # Check for common errors
        errors = 0
        
        # Multiple spaces
        if '  ' in text:
            errors += text.count('  ')
        
        # Missing capitalization after period
        sentences = re.split(r'[.!?]', text)
        for sent in sentences[1:]:  # Skip first sentence
            sent = sent.strip()
            if sent and sent[0].islower():
                errors += 1
        
        # Rough error rate
        words = len(text.split())
        error_rate = errors / max(words, 1)
        
        return min(error_rate, 1.0)
    
    def _calculate_ai_probability(
        self,
        perplexity: float,
        uniformity: float,
        formality: float,
        error_rate: float
    ) -> float:
        """
        Calculate overall AI generation probability.
        
        Args:
            perplexity: Text perplexity score
            uniformity: Sentence uniformity
            formality: Formality score
            error_rate: Grammatical error rate
            
        Returns:
            AI probability (0-1)
        """
        # AI characteristics:
        # - Low perplexity
        # - High uniformity
        # - High formality
        # - Low error rate
        
        scores = []
        
        # Perplexity score (lower = more AI-like)
        if perplexity < self.LOW_PERPLEXITY_THRESHOLD:
            scores.append((self.LOW_PERPLEXITY_THRESHOLD - perplexity) / self.LOW_PERPLEXITY_THRESHOLD)
        else:
            scores.append(0.0)
        
        # Uniformity score
        if uniformity > self.HIGH_UNIFORMITY_THRESHOLD:
            scores.append((uniformity - self.HIGH_UNIFORMITY_THRESHOLD) / (1 - self.HIGH_UNIFORMITY_THRESHOLD))
        else:
            scores.append(0.0)
        
        # Formality score (high formality = more AI-like)
        scores.append(formality)
        
        # Error rate (low errors = more AI-like)
        scores.append(1.0 - error_rate)
        
        # Weighted average
        weights = [0.4, 0.3, 0.2, 0.1]  # Perplexity and uniformity are most important
        
        ai_probability = sum(s * w for s, w in zip(scores, weights))
        
        return min(ai_probability, 1.0)

# Global instance
perplexity_checker = PerplexityChecker()