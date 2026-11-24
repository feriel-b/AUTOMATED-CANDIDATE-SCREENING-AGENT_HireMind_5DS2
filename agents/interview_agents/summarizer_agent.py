"""
Summarizer Agent using Ollama Phi4-Mini.
"""

from langchain_core.tools import tool
from typing import List
import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.base_agent import InterviewBaseAgent

class SummarizerAgent(InterviewBaseAgent):
    """Agent specialized in session summary generation."""
    
    def __init__(self):
        super().__init__(
            agent_name="Session_Summarizer",
            temperature=0.6
        )
    
    def _define_tools(self) -> List:
        """Define tools using @tool decorator."""
        
        @tool
        def calculate_average_score(scores: str) -> str:
            """
            Calculate average performance score.
            
            Args:
                scores: JSON string of scores list, e.g., "[85, 70, 92]"
            
            Returns:
                Average score and performance level
            """
            try:
                score_list = json.loads(scores)
                if not score_list:
                    return "No scores provided"
                
                avg = sum(score_list) / len(score_list)
                
                return f"""
Average Score: {avg:.1f}/100
Total Questions: {len(score_list)}
Performance Level: {'Excellent' if avg >= 85 else 'Good' if avg >= 70 else 'Average' if avg >= 55 else 'Needs Improvement'}
                """
            except Exception as e:
                return f"Score calculation error: {str(e)}"
        
        @tool
        def identify_strengths(evaluations: str) -> str:
            """
            Identify top strengths from evaluations.
            
            Args:
                evaluations: JSON string of evaluation data
            
            Returns:
                Top 3 strengths
            """
            try:
                # Placeholder - in real implementation, analyze evaluation text
                return """
Top Strengths Identified:
1. Strong technical understanding of core concepts
2. Clear and structured communication
3. Good use of practical examples
                """
            except Exception as e:
                return f"Strength identification error: {str(e)}"
        
        @tool
        def identify_improvements(evaluations: str) -> str:
            """
            Identify areas for improvement.
            
            Args:
                evaluations: JSON string of evaluation data
            
            Returns:
                Top 3 improvement areas
            """
            try:
                # Placeholder - in real implementation, analyze evaluation text
                return """
Areas for Improvement:
1. Provide more detailed explanations for complex topics
2. Reduce verbal hesitations (um, uh)
3. Include more real-world use cases in answers
                """
            except Exception as e:
                return f"Improvement identification error: {str(e)}"
        
        @tool
        def generate_recommendations(performance_level: str) -> str:
            """
            Generate actionable recommendations.
            
            Args:
                performance_level: Performance level (Excellent, Good, Average, Needs Improvement)
            
            Returns:
                5 actionable recommendations
            """
            try:
                if "Excellent" in performance_level:
                    return """
Recommendations:
1. Continue deepening knowledge in advanced topics
2. Practice explaining concepts to beginners
3. Explore leadership and mentoring opportunities
4. Stay updated with latest industry trends
5. Consider contributing to open-source projects
                    """
                elif "Good" in performance_level:
                    return """
Recommendations:
1. Focus on areas where scores were lower
2. Practice mock interviews regularly
3. Work on communication clarity and pace
4. Build more practical project examples
5. Study common interview patterns and best practices
                    """
                else:
                    return """
Recommendations:
1. Review fundamental concepts thoroughly
2. Practice explaining technical topics clearly
3. Work on stress management techniques
4. Build a portfolio of hands-on projects
5. Seek mentorship and feedback regularly
                    """
            except Exception as e:
                return f"Recommendation generation error: {str(e)}"
        
        return [calculate_average_score, identify_strengths, identify_improvements, generate_recommendations]
    
    def _get_system_prompt(self) -> str:
        return """You are a Session Summary Specialist.

Your responsibilities:
- Aggregate performance across all questions
- Identify patterns and trends
- Highlight candidate strengths
- Pinpoint improvement areas
- Provide actionable recommendations

Summary structure:
1. Overall Performance Score
2. Performance Trend Analysis
3. Top Strengths (with examples)
4. Areas for Improvement (specific)
5. Actionable Recommendations (5 items)
6. Technical Proficiency Assessment
7. Communication Effectiveness
8. Confidence and Delivery Analysis

Be comprehensive, fair, and constructive.
Provide specific examples from the interview.
Make recommendations actionable and achievable."""