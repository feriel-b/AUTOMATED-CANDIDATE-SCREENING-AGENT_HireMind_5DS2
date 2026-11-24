# In app/utils.py
print("--- RUNNING UTILS MODULE (HUGGINGFACE_HUB CLIENT) ---")

import os
import re
from typing import List, Dict, Optional
from io import BytesIO
import docx
import pypdf
from huggingface_hub import InferenceClient

# --- Setup ---
HF_API_KEY = "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"

# --- Initialize the official client ---
if HF_API_KEY:
    client = InferenceClient(token=HF_API_KEY)
else:
    print("FATAL ERROR: HF_TOKEN environment variable not set in docker-compose.yml.")
    client = None

# --- STABLE, WORKING HUGGING FACE MODELS ---
QA_MODEL = "deepset/xlm-roberta-large-squad2"
SUMMARY_MODEL = "facebook/bart-large-cnn"

# --- Comprehensive Skill Lists ---
TECH_SKILLS = [
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Ruby", "Go", "Rust", "Swift", 
    "Kotlin", "PHP", "HTML", "CSS", "SQL", "NoSQL", "R", "MATLAB", "Scala", "Perl",
    "React", "Angular", "Vue", "Node.js", "Express", "Django", "Flask", "FastAPI", "Spring", 
    "React Native", "Flutter", "jQuery", "Bootstrap", "Tailwind CSS", "SASS", "LESS",
    "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "Pandas", "NumPy", "Matplotlib", "Seaborn",
    "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Terraform", "Ansible", "Jenkins",
    "Git", "GitHub", "GitLab", "JIRA", "Confluence", "Linux", "Unix", "Windows", "MacOS",
    "MongoDB", "PostgreSQL", "MySQL", "Redis", "Kafka", "RabbitMQ", "Elasticsearch", "Firebase",
    "REST API", "GraphQL", "gRPC", "Microservices", "CI/CD", "DevOps", "Agile", "Scrum"
]

SOFT_SKILLS = [
    "Leadership", "Management", "Team Leadership", "Project Management", "Product Management",
    "Communication", "Verbal Communication", "Written Communication", "Public Speaking",
    "Problem Solving", "Critical Thinking", "Analytical Skills", "Decision Making",
    "Teamwork", "Collaboration", "Team Collaboration", "Cross-functional Collaboration",
    "Time Management", "Organization", "Planning", "Strategic Planning",
    "Creativity", "Innovation", "Adaptability", "Flexibility", "Resilience",
    "Presentation", "Negotiation", "Conflict Resolution", "Stakeholder Management",
    "Mentoring", "Coaching", "Training", "Knowledge Sharing",
    "Customer Service", "Client Management", "Relationship Building"
]

# =============================================================
# ENHANCED PARSING FUNCTIONS
# =============================================================

def extract_phone_advanced(text: str) -> str:
    """Advanced phone number extraction with multiple patterns"""
    phone_patterns = [
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US format: (123) 456-7890
        r'\+\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # International
        r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',  # Simple: 123-456-7890
        r'\(\d{3}\)\s*\d{3}[-.\s]?\d{4}',  # (123)456-7890
        r'\d{3}\.\d{3}\.\d{4}',  # 123.456.7890
        r'\d{10}',  # 1234567890
    ]
    
    for pattern in phone_patterns:
        matches = re.findall(pattern, text)
        if matches:
            # Return the first valid phone number found
            return matches[0]
    
    return "Not found"

def extract_skills_comprehensive(text: str) -> List[str]:
    """Extract skills using both regex and AI enhancement"""
    found_skills = set()
    text_lower = text.lower()
    
    # Method 1: Direct regex matching
    for skill in TECH_SKILLS + SOFT_SKILLS:
        if re.search(rf'\b{re.escape(skill)}\b', text, re.IGNORECASE):
            found_skills.add(skill)
    
    # Method 2: AI-enhanced skill detection for ambiguous cases
    try:
        # Look for skill sections in the text
        skill_sections = re.findall(r'(?:skills|technologies|expertise).*?(?=\n\s*\n|\n[A-Z]|\Z)', text, re.IGNORECASE | re.DOTALL)
        
        for section in skill_sections[:2]:  # Check first 2 skill sections
            # Use AI to extract skills from skill sections
            response = client.question_answering(
                question="List all technical skills and programming languages mentioned",
                context=section,
                model=QA_MODEL
            )
            if response.answer and response.answer.lower() not in ['none', 'not found', '']:
                # Parse the AI response for skill names
                ai_skills = [s.strip() for s in response.answer.split(',') if s.strip()]
                for skill in ai_skills:
                    # Match AI-extracted skills with our known skills
                    for known_skill in TECH_SKILLS + SOFT_SKILLS:
                        if known_skill.lower() in skill.lower() or skill.lower() in known_skill.lower():
                            found_skills.add(known_skill)
    except Exception as e:
        print(f"AI skill enhancement failed: {e}")
    
    return sorted(list(found_skills))

def generate_professional_summary(text: str) -> str:
    """Generate a professional summary using AI"""
    try:
        # Use summarization model for better results
        summary = client.summarization(
            text[:2000],  # Limit text length
            model=SUMMARY_MODEL,
            max_length=150,
            min_length=50,
        )
        return summary.summary_text
    except Exception as e:
        print(f"AI summary generation failed: {e}")
        # Fallback: create a basic summary from key sections
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Look for summary/objective section
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in ['summary', 'objective', 'profile']):
                if i + 1 < len(lines) and lines[i + 1]:
                    return lines[i + 1][:200] + "..."
        
        # Use first substantial paragraph
        for line in lines:
            if len(line.split()) > 15:  # Reasonable paragraph length
                return line[:200] + "..."
        
        return "Experienced professional with demonstrated skills and expertise."

def extract_experience_details(text: str) -> str:
    """Extract comprehensive experience information"""
    try:
        # Method 1: Use AI to summarize experience
        response = client.question_answering(
            question="Summarize the work experience and job history in 2-3 sentences",
            context=text[:3000],
            model=QA_MODEL
        )
        
        if response.answer and response.answer.lower() not in ['none', 'not found', '']:
            return response.answer
        
    except Exception as e:
        print(f"AI experience extraction failed: {e}")
    
    # Method 2: Extract experience section with regex
    experience_sections = re.findall(
        r'(?:experience|work history|employment).*?(?=\n\s*\n|\n(?:education|skills|projects)|\Z)', 
        text, 
        re.IGNORECASE | re.DOTALL
    )
    
    if experience_sections:
        # Take the first experience section and clean it up
        experience_text = experience_sections[0]
        # Remove the section header
        experience_text = re.sub(r'^(experience|work history|employment).*?\n', '', experience_text, flags=re.IGNORECASE)
        # Limit length and clean up
        experience_text = ' '.join(experience_text.split()[:100]) + "..."
        return experience_text
    
    # Method 3: Fallback - extract job titles and companies
    job_patterns = [
        r'([A-Z][a-zA-Z\s]+(?:Engineer|Developer|Manager|Analyst|Specialist|Director)) at ([A-Z][a-zA-Z\s&]+)',
        r'([A-Z][a-zA-Z\s]+) - ([A-Z][a-zA-Z\s&]+)',
    ]
    
    jobs = []
    for pattern in job_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            jobs.append(f"{match[0]} at {match[1]}")
    
    if jobs:
        return "Experience includes: " + "; ".join(jobs[:3])
    
    return "Professional experience details extracted from resume"

def extract_education_details(text: str) -> str:
    """Extract education information"""
    try:
        response = client.question_answering(
            question="What degrees, universities, or educational background is mentioned?",
            context=text[:2000],
            model=QA_MODEL
        )
        
        if response.answer and response.answer.lower() not in ['none', 'not found', '']:
            return response.answer
    except Exception as e:
        print(f"AI education extraction failed: {e}")
    
    # Fallback: regex for education section
    education_sections = re.findall(
        r'(?:education|academic).*?(?=\n\s*\n|\n(?:experience|skills)|\Z)', 
        text, 
        re.IGNORECASE | re.DOTALL
    )
    
    if education_sections:
        education_text = education_sections[0]
        education_text = re.sub(r'^(education|academic).*?\n', '', education_text, flags=re.IGNORECASE)
        return ' '.join(education_text.split()[:50]) + "..."
    
    return "Education details extracted from resume"

# =============================================================
# THE MAIN PARSING FUNCTION (Enhanced)
# =============================================================

def parse_resume(file_bytes: bytes, filename: str) -> Dict:
    if not client:
        return {"error": "AI client is not configured due to missing API key."}

    raw_text = ""
    try:
        if filename.endswith(".pdf"):
            reader = pypdf.PdfReader(BytesIO(file_bytes))
            raw_text = "".join(page.extract_text() or "" for page in reader.pages)
        elif filename.endswith(".docx"):
            doc = docx.Document(BytesIO(file_bytes))
            raw_text = "\n".join([p.text for p in doc.paragraphs])
        else: 
            return {"error": "Unsupported file type."}
    except Exception as e:
        return {"error": f"Could not read file content: {e}"}

    if not raw_text.strip(): 
        return {"error": "Could not extract any text from the document."}

    context = raw_text[:5000]
    print("Extracting details with enhanced Hugging Face InferenceClient...")

    try:
        # Extract core information with AI
        name_response = client.question_answering(
            question="What is the full name of the candidate?", 
            context=context, 
            model=QA_MODEL
        )
        name = name_response.answer if name_response.answer else "Not found"
        
        title_response = client.question_answering(
            question="What is the most recent job title or current position?", 
            context=context, 
            model=QA_MODEL
        )
        current_title = title_response.answer if title_response.answer else "Not found"
        
        location_response = client.question_answering(
            question="What city and state or location is mentioned?", 
            context=context, 
            model=QA_MODEL
        )
        location = location_response.answer if location_response.answer else "Not found"
        
    except Exception as e:
        print(f"An AI extraction failed: {e}")
        name, current_title, location = "Not found", "Not found", "Not found"

    # Enhanced extraction for other fields
    email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", raw_text)
    email = email_match.group(0) if email_match else "Not found"
    
    phone = extract_phone_advanced(raw_text)
    skills = extract_skills_comprehensive(raw_text)
    professional_summary = generate_professional_summary(raw_text)
    experience = extract_experience_details(raw_text)
    education = extract_education_details(raw_text)

    print(f"Extraction complete. Found {len(skills)} skills.")
    
    # Return data matching your ProfileCompleteData model
    return {
        "full_name": name,
        "email": email,
        "phone": phone,
        "location": location,
        "current_title": current_title,
        "skills": skills,
        "education": education,
        "professional_summary": professional_summary,
        "experience": experience,
        "raw_text": raw_text[:5000]  # Truncate for database storage
    }

def calculate_match_score(candidate_skills: List[str], job_skills: List[str]) -> int:
    """Calculate match score between candidate skills and job requirements"""
    if not candidate_skills or not job_skills:
        return 0
    
    matched_skills = set(candidate_skills) & set(job_skills)
    score = int((len(matched_skills) / len(job_skills)) * 100) if job_skills else 0
    return min(score, 100)

# Database integration helper
def save_profile_to_db(profile_data: Dict, db_session):
    """Save the parsed profile data to database"""
    from models import Candidate  # Import your actual model
    
    try:
        candidate = Candidate(
            full_name=profile_data.get("full_name"),
            email=profile_data.get("email"),
            phone=profile_data.get("phone"),
            location=profile_data.get("location"),
            current_title=profile_data.get("current_title"),
            skills=profile_data.get("skills", []),
            education=profile_data.get("education"),
            professional_summary=profile_data.get("professional_summary"),
            experience=profile_data.get("experience"),
            raw_text=profile_data.get("raw_text")
        )
        
        db_session.add(candidate)
        db_session.commit()
        return candidate
        
    except Exception as e:
        db_session.rollback()
        print(f"Error saving to database: {e}")
        raise