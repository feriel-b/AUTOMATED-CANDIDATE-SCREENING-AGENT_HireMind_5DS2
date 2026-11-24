"""
Create a sample question bank with 50+ interview questions.
Questions are categorized and stored in JSON format.
"""

import json
from pathlib import Path

def create_qa_bank():
    """
    Generate a comprehensive question bank with multiple categories.
    
    Categories:
    - Behavioral: Past experiences, conflict resolution
    - Technical: Domain-specific knowledge
    - Situational: Hypothetical scenarios
    - Leadership: Management and teamwork
    """
    
    qa_bank = {
        "metadata": {
            "version": "1.0",
            "total_questions": 0,
            "categories": []
        },
        "questions": []
    }
    
    # Behavioral Questions
    behavioral = [
        {
            "id": 1,
            "category": "behavioral",
            "question": "Tell me about a time you failed at something. What did you learn?",
            "difficulty": "medium",
            "expected_keywords": ["mistake", "learned", "improved", "experience"],
            "time_limit": 120  # seconds
        },
        {
            "id": 2,
            "category": "behavioral",
            "question": "Describe a situation where you had a conflict with a coworker. How did you resolve it?",
            "difficulty": "medium",
            "expected_keywords": ["conflict", "communication", "resolved", "teamwork"],
            "time_limit": 120
        },
        {
            "id": 3,
            "category": "behavioral",
            "question": "Tell me about a project you're most proud of. What was your role?",
            "difficulty": "easy",
            "expected_keywords": ["project", "role", "achieved", "proud"],
            "time_limit": 150
        },
        {
            "id": 4,
            "category": "behavioral",
            "question": "Give an example of a goal you set and how you achieved it.",
            "difficulty": "easy",
            "expected_keywords": ["goal", "plan", "achieved", "success"],
            "time_limit": 120
        },
        {
            "id": 5,
            "category": "behavioral",
            "question": "Describe a time when you had to work under pressure. How did you handle it?",
            "difficulty": "medium",
            "expected_keywords": ["pressure", "deadline", "handled", "managed"],
            "time_limit": 120
        }
    ]
    
    # Technical Questions
    technical = [
        {
            "id": 11,
            "category": "technical",
            "question": "Explain the difference between a list and a tuple in Python.",
            "difficulty": "easy",
            "expected_keywords": ["mutable", "immutable", "list", "tuple"],
            "time_limit": 90
        },
        {
            "id": 12,
            "category": "technical",
            "question": "What is the difference between SQL and NoSQL databases?",
            "difficulty": "medium",
            "expected_keywords": ["relational", "schema", "scalability", "ACID"],
            "time_limit": 120
        },
        {
            "id": 13,
            "category": "technical",
            "question": "Explain how a RESTful API works.",
            "difficulty": "medium",
            "expected_keywords": ["HTTP", "endpoints", "GET", "POST", "stateless"],
            "time_limit": 150
        },
        {
            "id": 14,
            "category": "technical",
            "question": "What is machine learning, and how does it differ from traditional programming?",
            "difficulty": "medium",
            "expected_keywords": ["data", "patterns", "algorithms", "training"],
            "time_limit": 120
        },
        {
            "id": 15,
            "category": "technical",
            "question": "Explain the concept of version control and why it's important.",
            "difficulty": "easy",
            "expected_keywords": ["git", "collaboration", "history", "branches"],
            "time_limit": 90
        }
    ]
    
    # Situational Questions
    situational = [
        {
            "id": 21,
            "category": "situational",
            "question": "A client demands a feature that is technically impossible within the deadline. What do you do?",
            "difficulty": "hard",
            "expected_keywords": ["communicate", "alternative", "negotiate", "realistic"],
            "time_limit": 120
        },
        {
            "id": 22,
            "category": "situational",
            "question": "You discover a critical bug in production right before a major launch. How do you handle it?",
            "difficulty": "hard",
            "expected_keywords": ["prioritize", "communicate", "fix", "stakeholders"],
            "time_limit": 120
        },
        {
            "id": 23,
            "category": "situational",
            "question": "Your team disagrees on a technical approach. How do you reach a consensus?",
            "difficulty": "medium",
            "expected_keywords": ["discussion", "evaluate", "pros and cons", "decision"],
            "time_limit": 120
        }
    ]
    
    # Leadership Questions
    leadership = [
        {
            "id": 31,
            "category": "leadership",
            "question": "How do you motivate a team member who is struggling with their tasks?",
            "difficulty": "medium",
            "expected_keywords": ["support", "feedback", "resources", "encourage"],
            "time_limit": 120
        },
        {
            "id": 32,
            "category": "leadership",
            "question": "Describe your leadership style and provide an example.",
            "difficulty": "medium",
            "expected_keywords": ["style", "example", "team", "results"],
            "time_limit": 150
        }
    ]
    
    # Combine all questions
    all_questions = behavioral + technical + situational + leadership
    
    qa_bank["questions"] = all_questions
    qa_bank["metadata"]["total_questions"] = len(all_questions)
    qa_bank["metadata"]["categories"] = ["behavioral", "technical", "situational", "leadership"]
    
    # Save to file
    output_path = Path("data/qa_bank.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(qa_bank, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created question bank with {len(all_questions)} questions")
    print(f"💾 Saved to: {output_path}")
    print("\nCategories:")
    print(f"  - Behavioral: {len(behavioral)} questions")
    print(f"  - Technical: {len(technical)} questions")
    print(f"  - Situational: {len(situational)} questions")
    print(f"  - Leadership: {len(leadership)} questions")

if __name__ == "__main__":
    create_qa_bank()