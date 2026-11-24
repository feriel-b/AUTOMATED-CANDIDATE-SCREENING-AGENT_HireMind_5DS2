"""
Question Bank Manager.

Loads and manages interview questions from JSON file.
Provides filtering by category, difficulty, and random selection.
"""

import json
import random
from pathlib import Path
from typing import List, Optional, Dict
import logging

logger = logging.getLogger(__name__)

class QuestionBank:
    """
    Manages the interview question database.
    
    This class loads questions from JSON and provides methods to:
    - Get questions by category/difficulty
    - Get random questions for a session
    - Retrieve specific questions by ID
    """
    
    def __init__(self, qa_bank_path: str = "data/qa_bank.json"):
        """
        Initialize question bank from JSON file.
        
        Args:
            qa_bank_path: Path to JSON file with questions
        """
        self.qa_bank_path = Path(qa_bank_path)
        self.questions: List[Dict] = []
        self.metadata: Dict = {}
        
        self._load_questions()
    
    def _load_questions(self):
        """
        Load questions from JSON file.
        
        If file doesn't exist, create it using the script.
        """
        if not self.qa_bank_path.exists():
            logger.warning(f"Q&A bank not found at {self.qa_bank_path}")
            logger.info("Creating default question bank...")
            
            # Create parent directory
            self.qa_bank_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Run the create_qa_bank script
            try:
                from scripts.create_qa_bank import create_qa_bank
                create_qa_bank()
            except ImportError:
                logger.error("Could not import create_qa_bank script")
                # Create minimal default questions
                self._create_default_questions()
                return
        
        # Load JSON
        try:
            with open(self.qa_bank_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.questions = data.get("questions", [])
            self.metadata = data.get("metadata", {})
            
            logger.info(f"Loaded {len(self.questions)} questions from {self.qa_bank_path}")
        except Exception as e:
            logger.error(f"Failed to load questions: {e}")
            self._create_default_questions()
    
    def _create_default_questions(self):
        """Create minimal default questions if file doesn't exist."""
        default_data = {
            "metadata": {
                "version": "1.0",
                "total_questions": 10,
                "categories": ["Python", "Algorithms", "System Design", "Behavioral"]
            },
            "questions": [
                {
                    "id": 1,
                    "question": "What is the difference between a list and a tuple in Python?",
                    "category": "Python",
                    "difficulty": "easy",
                    "expected_keywords": ["mutable", "immutable", "list", "tuple"]
                },
                {
                    "id": 2,
                    "question": "Explain how Python's GIL (Global Interpreter Lock) works.",
                    "category": "Python",
                    "difficulty": "medium",
                    "expected_keywords": ["GIL", "threads", "CPython", "concurrency"]
                },
                {
                    "id": 3,
                    "question": "What are Python decorators and how do they work?",
                    "category": "Python",
                    "difficulty": "medium",
                    "expected_keywords": ["decorator", "wrapper", "function", "@"]
                },
                {
                    "id": 4,
                    "question": "Explain the time complexity of binary search.",
                    "category": "Algorithms",
                    "difficulty": "easy",
                    "expected_keywords": ["O(log n)", "binary", "sorted", "divide"]
                },
                {
                    "id": 5,
                    "question": "How would you design a URL shortening service like bit.ly?",
                    "category": "System Design",
                    "difficulty": "hard",
                    "expected_keywords": ["hash", "database", "scalability", "redirect"]
                },
                {
                    "id": 6,
                    "question": "Tell me about a time you faced a challenging bug. How did you solve it?",
                    "category": "Behavioral",
                    "difficulty": "medium",
                    "expected_keywords": ["debugging", "problem-solving", "approach"]
                },
                {
                    "id": 7,
                    "question": "What is the difference between REST and GraphQL?",
                    "category": "System Design",
                    "difficulty": "medium",
                    "expected_keywords": ["REST", "GraphQL", "API", "query"]
                },
                {
                    "id": 8,
                    "question": "Explain the difference between merge sort and quick sort.",
                    "category": "Algorithms",
                    "difficulty": "medium",
                    "expected_keywords": ["merge", "quick", "O(n log n)", "pivot"]
                },
                {
                    "id": 9,
                    "question": "How do you handle conflicts in a team?",
                    "category": "Behavioral",
                    "difficulty": "easy",
                    "expected_keywords": ["communication", "collaboration", "resolution"]
                },
                {
                    "id": 10,
                    "question": "What are Python generators and when would you use them?",
                    "category": "Python",
                    "difficulty": "hard",
                    "expected_keywords": ["yield", "iterator", "memory", "lazy"]
                }
            ]
        }
        
        # Save to file
        self.qa_bank_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.qa_bank_path, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, indent=2)
        
        self.questions = default_data["questions"]
        self.metadata = default_data["metadata"]
        
        logger.info(f"Created default question bank with {len(self.questions)} questions")
    
    def get_question_by_id(self, question_id: int) -> Optional[Dict]:
        """
        Retrieve a specific question by ID.
        
        Args:
            question_id: Question ID to retrieve
            
        Returns:
            Question dict or None if not found
        """
        for question in self.questions:
            if question["id"] == question_id:
                return question
        
        logger.warning(f"Question ID {question_id} not found")
        return None
    
    def get_questions_by_category(
        self,
        category: str,
        difficulty: Optional[str] = None
    ) -> List[Dict]:
        """
        Filter questions by category and/or difficulty.
        
        Args:
            category: Category to filter by (e.g., "Python", "Algorithms")
            difficulty: Difficulty level ("easy", "medium", "hard")
            
        Returns:
            List of matching questions
        """
        filtered = [q for q in self.questions if q["category"] == category]
        
        # Filter by difficulty
        if difficulty:
            filtered = [
                q for q in filtered
                if q["difficulty"].lower() == difficulty.lower()
            ]
        
        logger.info(f"Filtered {len(filtered)} questions (category={category}, difficulty={difficulty})")
        return filtered
    
    def get_random_questions(
        self,
        num_questions: int = 5,
        categories: Optional[List[str]] = None,
        difficulty: Optional[str] = None,
        seed: Optional[int] = None
    ) -> List[Dict]:
        """
        Get random questions for an interview session.
        
        Args:
            num_questions: Number of questions to return
            categories: Filter by categories
            difficulty: Filter by difficulty
            seed: Random seed for reproducibility (optional)
            
        Returns:
            List of random questions
        """
        # Get filtered questions
        available = self.questions
        
        if categories:
            available = [q for q in available if q["category"] in categories]
        
        if difficulty:
            available = [q for q in available if q["difficulty"].lower() == difficulty.lower()]
        
        if not available:
            logger.error("No questions match the criteria")
            return []
        
        # Set random seed if provided (useful for testing)
        if seed is not None:
            random.seed(seed)
        
        # Sample random questions
        num_to_select = min(num_questions, len(available))
        selected = random.sample(available, num_to_select)
        
        logger.info(f"Selected {num_to_select} random questions")
        return selected
    
    def get_all_categories(self) -> List[str]:
        """
        Get list of all available categories.
        
        Returns:
            List of category names
        """
        return self.metadata.get("categories", [])
    
    def get_total_questions(self) -> int:
        """
        Get total number of questions in the bank.
        
        Returns:
            Total question count
        """
        return len(self.questions)

# Global instance (singleton pattern)
# This is loaded once when the app starts
qa_bank = QuestionBank()

# Also export as question_bank for backward compatibility
question_bank = qa_bank