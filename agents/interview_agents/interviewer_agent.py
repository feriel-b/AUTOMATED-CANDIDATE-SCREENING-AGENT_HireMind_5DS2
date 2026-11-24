"""
Interviewer Agent using Ollama Phi4-Mini.
"""

from langchain_core.tools import tool
from typing import List
import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.interview_simulator.qa_bank import qa_bank  # ← Fixed import
from core.base_agent import InterviewBaseAgent

class InterviewerAgent(InterviewBaseAgent):
    """Agent specialized in question selection and interview management."""
    
    def __init__(self):
        super().__init__(
            agent_name="Senior_Interviewer",
            temperature=0.8
        )
    
    def _define_tools(self) -> List:
        """Define tools using @tool decorator."""
        
        @tool
        def select_interview_question(category: str, difficulty: str = "medium") -> str:
            """
            Select an interview question from the database.
            
            Args:
                category: Question category (e.g., "Python", "Algorithms")
                difficulty: Question difficulty ("easy", "medium", "hard")
            
            Returns:
                JSON string with question details
            """
            try:
                questions = qa_bank.get_questions_by_category(category, difficulty)
                if questions:
                    question = questions[0]
                    return json.dumps({
                        "id": question.get("id"),
                        "question": question.get("question"),
                        "category": question.get("category"),
                        "difficulty": question.get("difficulty")
                    })
                else:
                    return json.dumps({"error": f"No questions found for {category}/{difficulty}"})
            except Exception as e:
                return json.dumps({"error": str(e)})
        
        @tool
        def get_available_categories() -> str:
            """Get list of all available question categories."""
            try:
                categories = qa_bank.get_all_categories()
                return json.dumps({"categories": categories})
            except Exception as e:
                return json.dumps({"error": str(e)})
        
        @tool
        def adjust_difficulty(current_score: float) -> str:
            """
            Suggest difficulty adjustment based on candidate score.
            
            Args:
                current_score: Candidate's current score (0-100)
            
            Returns:
                Recommended difficulty level
            """
            if current_score >= 80:
                return "hard"
            elif current_score >= 50:
                return "medium"
            else:
                return "easy"
        
        return [select_interview_question, get_available_categories, adjust_difficulty]
    
    def _get_system_prompt(self) -> str:
        return """You are a Senior Technical Interviewer with 10+ years of experience.

Your responsibilities:
- Select appropriate questions based on candidate level
- Adjust difficulty dynamically based on performance
- Ensure fair and comprehensive technical assessment

Guidelines:
- Start with medium difficulty
- Increase difficulty if candidate scores >80%
- Decrease difficulty if candidate scores <50%
- Cover multiple technical areas
- Provide diverse question types"""