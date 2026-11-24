"""
CV Parser for Avatar Generation.

Extracts structured data from CV/resume files:
- Personal info (name, role)
- Skills and technologies
- Experience level
- Domain/industry
- Professional summary
"""

import re
import json
from typing import Dict, List, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class CVParser:
    """
    Parse CV files (PDF, DOCX, TXT) and extract structured data.
    
    Extracts:
    - Name, role, title
    - Skills (technical, soft)
    - Experience level (Junior/Mid/Senior)
    - Domain (Tech, Business, Creative, etc.)
    - Years of experience
    """
    
    def __init__(self):
        """Initialize CV parser."""
        logger.info("Initializing CV Parser...")
        
        # Skill categories
        self.TECH_SKILLS = {
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'php',
            'react', 'angular', 'vue', 'node', 'django', 'flask', 'spring',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins',
            'sql', 'mongodb', 'postgresql', 'redis', 'elasticsearch',
            'machine learning', 'deep learning', 'ai', 'nlp', 'computer vision',
            'data science', 'tensorflow', 'pytorch', 'scikit-learn'
        }
        
        self.SOFT_SKILLS = {
            'leadership', 'communication', 'teamwork', 'problem solving',
            'analytical', 'critical thinking', 'project management',
            'agile', 'scrum', 'collaboration', 'presentation'
        }
        
        # Domain keywords
        self.DOMAINS = {
            'tech': ['software', 'developer', 'engineer', 'programmer', 'data scientist', 'devops', 'architect'],
            'business': ['manager', 'consultant', 'analyst', 'strategy', 'operations', 'product manager'],
            'creative': ['designer', 'ux', 'ui', 'artist', 'creative', 'graphic', 'multimedia'],
            'academic': ['professor', 'researcher', 'scientist', 'phd', 'postdoc', 'academic'],
            'healthcare': ['doctor', 'nurse', 'medical', 'physician', 'healthcare', 'clinical'],
            'finance': ['accountant', 'financial', 'banker', 'investment', 'analyst', 'cpa']
        }
        
        # Seniority keywords
        self.SENIORITY_KEYWORDS = {
            'junior': ['junior', 'associate', 'entry', 'intern', 'trainee', '0-2 years'],
            'mid': ['mid', 'intermediate', 'professional', '3-5 years', '2-4 years'],
            'senior': ['senior', 'lead', 'principal', 'staff', 'expert', '5+ years', '6+ years'],
            'executive': ['director', 'vp', 'chief', 'cto', 'ceo', 'head of', 'president']
        }
        
        logger.info("✅ CV Parser initialized")
    
    def parse(self, cv_path: str) -> Dict:
        """
        Parse CV file and extract structured data.
        
        Args:
            cv_path: Path to CV file (PDF, DOCX, TXT)
            
        Returns:
            Structured CV data
        """
        logger.info(f"Parsing CV: {cv_path}")
        
        try:
            # Read file content
            text = self._read_file(cv_path)
            
            if not text:
                logger.error("Failed to extract text from CV")
                return self._get_default_cv_data()
            
            # Extract structured data
            cv_data = {
                'name': self._extract_name(text),
                'role': self._extract_role(text),
                'summary': self._extract_summary(text),
                'skills': self._extract_skills(text),
                'domain': self._extract_domain(text),
                'seniority': self._extract_seniority(text),
                'years_experience': self._extract_years_experience(text),
                'technologies': self._extract_technologies(text),
                'education': self._extract_education(text)
            }
            
            logger.info(f"✅ CV parsed: {cv_data['name']}, {cv_data['role']}")
            return cv_data
            
        except Exception as e:
            logger.error(f"CV parsing failed: {e}")
            import traceback
            traceback.print_exc()
            return self._get_default_cv_data()
    
    def _read_file(self, file_path: str) -> str:
        """
        Read text from file (supports PDF, DOCX, TXT).
        
        Args:
            file_path: Path to file
            
        Returns:
            Extracted text
        """
        path = Path(file_path)
        extension = path.suffix.lower()
        
        try:
            if extension == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            elif extension == '.pdf':
                import pdfplumber
                text = ""
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() or ""
                return text
            
            elif extension in ['.docx', '.doc']:
                from docx import Document
                doc = Document(file_path)
                text = "\n".join([para.text for para in doc.paragraphs])
                return text
            
            else:
                logger.warning(f"Unsupported file format: {extension}")
                return ""
                
        except Exception as e:
            logger.error(f"File reading failed: {e}")
            return ""
    
    def _extract_name(self, text: str) -> str:
        """Extract candidate name (usually first line)."""
        lines = text.split('\n')
        
        # Name is typically in first 3 lines
        for line in lines[:3]:
            line = line.strip()
            # Simple heuristic: name is short, has capitals, no special chars
            if line and len(line.split()) <= 4 and line[0].isupper():
                # Check if it looks like a name (not email, phone, etc.)
                if not re.search(r'[@\d\(\)]', line):
                    return line
        
        return "Candidate"
    
    def _extract_role(self, text: str) -> str:
        """Extract job role/title."""
        text_lower = text.lower()
        
        # Common role patterns
        role_patterns = [
            r'(?:^|\n)([A-Z][a-z]+(?: [A-Z][a-z]+)*(?: Engineer| Developer| Designer| Manager| Analyst| Scientist))',
            r'(?:role|position|title)[:：]\s*([^\n]+)',
        ]
        
        for pattern in role_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                role = match.group(1).strip()
                if len(role.split()) <= 6:  # Reasonable role length
                    return role
        
        # Fallback: check domain keywords
        for domain, keywords in self.DOMAINS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return keyword.title()
        
        return "Professional"
    
    def _extract_summary(self, text: str) -> str:
        """Extract professional summary."""
        # Look for summary section
        summary_patterns = [
            r'(?:summary|profile|about|objective)[:：]\s*([^\n]+(?:\n[^\n]+){0,3})',
        ]
        
        for pattern in summary_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                summary = match.group(1).strip()
                # Limit to 200 chars
                return summary[:200] + ('...' if len(summary) > 200 else '')
        
        # Fallback: use first paragraph after name
        paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 50]
        if paragraphs:
            return paragraphs[0][:200]
        
        return ""
    
    def _extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract technical and soft skills."""
        text_lower = text.lower()
        
        found_tech_skills = []
        found_soft_skills = []
        
        # Find technical skills
        for skill in self.TECH_SKILLS:
            if skill in text_lower:
                found_tech_skills.append(skill)
        
        # Find soft skills
        for skill in self.SOFT_SKILLS:
            if skill in text_lower:
                found_soft_skills.append(skill)
        
        return {
            'technical': found_tech_skills[:10],  # Top 10
            'soft': found_soft_skills[:5]
        }
    
    def _extract_domain(self, text: str) -> str:
        """Extract professional domain."""
        text_lower = text.lower()
        
        domain_scores = {domain: 0 for domain in self.DOMAINS.keys()}
        
        for domain, keywords in self.DOMAINS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    domain_scores[domain] += 1
        
        # Return domain with highest score
        best_domain = max(domain_scores, key=domain_scores.get)
        
        return best_domain if domain_scores[best_domain] > 0 else 'tech'
    
    def _extract_seniority(self, text: str) -> str:
        """Extract seniority level."""
        text_lower = text.lower()
        
        # Check for seniority keywords
        for level, keywords in self.SENIORITY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return level
        
        # Fallback: estimate from years of experience
        years = self._extract_years_experience(text)
        
        if years < 2:
            return 'junior'
        elif years < 5:
            return 'mid'
        elif years < 10:
            return 'senior'
        else:
            return 'executive'
    
    def _extract_years_experience(self, text: str) -> int:
        """Extract years of experience."""
        # Look for patterns like "5 years", "3+ years", "2-4 years"
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of)?\s*experience',
            r'experience[:\s]+(\d+)\+?\s*years?',
            r'(\d+)-(\d+)\s*years?'
        ]
        
        years_found = []
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # Range like "2-4 years"
                    years_found.append(int(match[0]))
                else:
                    years_found.append(int(match))
        
        return max(years_found) if years_found else 0
    
    def _extract_technologies(self, text: str) -> List[str]:
        """Extract technology stack."""
        text_lower = text.lower()
        
        # Extended tech list
        technologies = {
            'python', 'java', 'javascript', 'typescript', 'react', 'angular',
            'node.js', 'django', 'flask', 'spring boot', 'docker', 'kubernetes',
            'aws', 'azure', 'gcp', 'tensorflow', 'pytorch', 'mongodb', 'postgresql'
        }
        
        found = []
        for tech in technologies:
            if tech in text_lower:
                found.append(tech)
        
        return found[:8]  # Top 8
    
    def _extract_education(self, text: str) -> List[str]:
        """Extract education degrees."""
        degrees = []
        
        degree_patterns = [
            r'(Bachelor|Master|PhD|MBA|B\.S\.|M\.S\.|B\.A\.|M\.A\.)[^\n]{0,50}',
            r'(University|College|Institute)[^\n]{0,50}'
        ]
        
        for pattern in degree_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            degrees.extend(matches[:3])  # Max 3
        
        return degrees
    
    def _get_default_cv_data(self) -> Dict:
        """Return default CV data when parsing fails."""
        return {
            'name': 'Candidate',
            'role': 'Professional',
            'summary': '',
            'skills': {'technical': [], 'soft': []},
            'domain': 'tech',
            'seniority': 'mid',
            'years_experience': 0,
            'technologies': [],
            'education': []
        }

# Global instance
cv_parser = CVParser()