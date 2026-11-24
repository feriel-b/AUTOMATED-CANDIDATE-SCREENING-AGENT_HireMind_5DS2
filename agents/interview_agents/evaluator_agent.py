"""
Evaluator Agent using Ollama Phi4-Mini.
"""

from langchain_core.tools import tool
from typing import List
import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.interview_simulator.evaluator import evaluator  
from core.base_agent import InterviewBaseAgent
import logging

logger = logging.getLogger(__name__)

class EvaluatorAgent(InterviewBaseAgent):
    """Agent specialized in comprehensive answer evaluation."""
    
    def __init__(self):
        super().__init__(
            agent_name="Senior_Evaluator",
            temperature=0.4
        )
    
    def _define_tools(self) -> List:
        """Define tools using @tool decorator."""
        
        @tool
        def evaluate_technical_answer(
            question: str,
            answer: str,
            expected_keywords: str
        ) -> str:
            """
            Evaluate technical accuracy and completeness.
            
            Args:
                question: Interview question
                answer: Candidate answer
                expected_keywords: Expected technical keywords (comma-separated)
                
            Returns:
                JSON string with technical evaluation
            """
            try:
                result = evaluator.evaluate_answer(
                    question=question,
                    answer=answer,
                    expected_keywords=expected_keywords.split(',')
                )
                
                return json.dumps({
                    'technical_score': result['scores']['technical_accuracy'],
                    'completeness': result['scores']['completeness'],
                    'keyword_coverage': result['keyword_coverage'],
                    'feedback': result['detailed_feedback']['technical']
                })
            except Exception as e:
                return json.dumps({'error': str(e)})
        
        @tool
        def analyze_communication_quality(
            answer: str,
            prosody_data: dict
        ) -> str:
            """
            Analyze communication quality (clarity, structure, delivery).
            
            Args:
                answer: Answer text
                prosody_data: Voice quality metrics
                
            Returns:
                Communication analysis
            """
            try:
                # Analyze structure
                sentences = answer.split('.')
                avg_sentence_length = len(answer.split()) / max(len(sentences), 1)
                
                # Communication score
                clarity_score = min(100, 100 - abs(avg_sentence_length - 20) * 2)
                
                return json.dumps({
                    'clarity_score': round(clarity_score, 1),
                    'structure': 'good' if len(sentences) > 2 else 'needs_improvement',
                    'voice_quality': prosody_data.get('overall_quality', 'unknown'),
                    'feedback': 'Clear and well-structured' if clarity_score > 70 else 'Consider more concise responses'
                })
            except Exception as e:
                return json.dumps({'error': str(e)})
        
        @tool
        def assess_confidence_level(
            emotion_data: dict,
            prosody_data: dict
        ) -> str:
            """
            Assess candidate confidence from emotion and voice analysis.
            
            Args:
                emotion_data: Facial emotion analysis
                prosody_data: Voice quality metrics
                
            Returns:
                Confidence assessment
            """
            try:
                # Combine signals
                stress_level = emotion_data.get('stress_level', 0)
                voice_stability = prosody_data.get('stability_score', 50)
                
                confidence = (100 - stress_level * 100 + voice_stability) / 2
                
                return json.dumps({
                    'confidence_score': round(confidence, 1),
                    'stress_indicators': stress_level > 0.3,
                    'voice_stability': voice_stability,
                    'overall_impression': 'confident' if confidence > 70 else 'moderately confident' if confidence > 50 else 'nervous'
                })
            except Exception as e:
                return json.dumps({'error': str(e)})
        
        return [
            evaluate_technical_answer,
            analyze_communication_quality,
            assess_confidence_level
        ]
    
    def _get_system_prompt(self) -> str:
        return """You are a Senior Technical Interviewer and Evaluator with 15+ years of experience.

Your role is to provide comprehensive, fair, and constructive evaluation of interview answers.

EVALUATION CRITERIA:

1. TECHNICAL ACCURACY (40%):
   - Correctness of information
   - Depth of understanding
   - Use of appropriate terminology
   - Keyword coverage

2. COMPLETENESS (30%):
   - All aspects of question addressed
   - Sufficient detail and examples
   - Logical flow and structure

3. COMMUNICATION (20%):
   - Clarity of explanation
   - Appropriate pace and tone
   - Confidence in delivery
   - Professional language

4. PROBLEM-SOLVING (10%):
   - Analytical approach
   - Creative thinking
   - Practical application

OUTPUT FORMAT:
- Overall score (0-100)
- Category scores (technical, completeness, communication, confidence)
- Strengths (2-3 points)
- Areas for improvement (2-3 points)
- Specific actionable feedback
- Final recommendation (Strong Pass, Pass, Borderline, Fail)

Be fair, constructive, and specific. Focus on growth, not just criticism."""

# Global instance
evaluator_agent = EvaluatorAgent()