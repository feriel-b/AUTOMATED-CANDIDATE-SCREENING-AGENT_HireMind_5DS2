"""Question bank service for AI interview simulator."""

import json
import random
from pathlib import Path
from typing import List, Dict, Optional
from functools import lru_cache


class QuestionBank:
    """Manages interview questions from JSON file."""
    
    def __init__(self, json_path: str = None):
        """Initialize question bank from JSON file."""
        if json_path is None:
            json_path = Path(__file__).parent / "interview_qa_extracted.json"
        
        with open(json_path, 'r', encoding='utf-8') as f:
            self.questions: List[Dict] = json.load(f)
        
        # Build indices for fast lookup
        self._build_indices()
    
    def _build_indices(self):
        """Build role and category indices."""
        self.roles = sorted(list(set(q.get('role', '') for q in self.questions if q.get('role'))))
        self.categories = sorted(list(set(q.get('category', '') for q in self.questions if q.get('category'))))
        
        # Index by role
        self.by_role = {}
        for q in self.questions:
            role = q.get('role', '')
            if role:
                if role not in self.by_role:
                    self.by_role[role] = []
                self.by_role[role].append(q)
        
        # Index by category
        self.by_category = {}
        for q in self.questions:
            cat = q.get('category', '')
            if cat:
                if cat not in self.by_category:
                    self.by_category[cat] = []
                self.by_category[cat].append(q)
    
    def get_roles(self) -> List[str]:
        """Get all unique roles."""
        return self.roles
    
    def get_categories(self, role: Optional[str] = None) -> List[str]:
        """Get all categories, optionally filtered by role."""
        if role:
            questions = self.by_role.get(role, [])
            cats = sorted(list(set(q.get('category', '') for q in questions if q.get('category'))))
            return cats
        return self.categories
    
    def get_questions(
        self,
        role: Optional[str] = None,
        category: Optional[str] = None,
        categories: Optional[List[str]] = None,
        limit: Optional[int] = None,
        shuffle: bool = False
    ) -> List[Dict]:
        """
        Get questions filtered by role and/or category.
        
        Args:
            role: Filter by role
            category: Filter by category
            limit: Maximum number of questions to return
            shuffle: Randomize question order
        
        Returns:
            List of question dictionaries
        """
        result = self.questions
        
        # Filter by role
        if role:
            result = [q for q in result if q.get('role') == role]
        
        # Filter by categories (multi) or single category
        if categories:
            categories_set = set(categories)
            result = [q for q in result if q.get('category') in categories_set]
        elif category:
            result = [q for q in result if q.get('category') == category]
        
        # Shuffle if requested
        if shuffle:
            result = random.sample(result, len(result))
        
        # Limit results
        if limit:
            result = result[:limit]
        
        return result
    
    def get_random_question(
        self,
        role: Optional[str] = None,
        category: Optional[str] = None,
        categories: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """Get a random question matching filters."""
        questions = self.get_questions(role=role, category=category, categories=categories)
        if questions:
            return random.choice(questions)
        return None

    def find_question(self, question_text: str) -> Optional[Dict]:
        """Find a question dict by exact text match (case-sensitive fallback to case-insensitive)."""
        if not question_text:
            return None
        # Try exact match first
        for q in self.questions:
            if q.get('question') == question_text:
                return q
        # Fallback case-insensitive
        qlow = question_text.strip().lower()
        for q in self.questions:
            if (q.get('question', '').strip().lower()) == qlow:
                return q
        return None


# Global instance
_question_bank: Optional[QuestionBank] = None


@lru_cache(maxsize=1)
def get_question_bank() -> QuestionBank:
    """Get or create global question bank instance."""
    global _question_bank
    if _question_bank is None:
        _question_bank = QuestionBank()
    return _question_bank
