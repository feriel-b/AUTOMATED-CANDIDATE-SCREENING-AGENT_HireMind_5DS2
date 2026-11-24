import os
from huggingface_hub import InferenceClient
import re
import json
from io import BytesIO
import docx
import pypdf

# Initialize Hugging Face Inference Client
client = InferenceClient(
    provider="hf-inference",
    api_key="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",
)

def extract_text_from_pdf(file_bytes: bytes) -> str:
    pdf_reader = pypdf.PdfReader(BytesIO(file_bytes))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = docx.Document(BytesIO(file_bytes))
    return "\n".join([para.text for para in doc.paragraphs])

def extract_name_with_hf(text: str):
    """Use NER model to extract person name"""
    text_chunk = text[:1000]  # Limit text length
    
    try:
        result = client.token_classification(
            text_chunk,
            model="dbmdz/bert-large-cased-finetuned-conll03-english",
        )
        
        # Look for PERSON entities
        for entity in result:
            if entity.entity_group == 'PER':
                return entity.word
    
    except Exception as e:
        print(f"NER API failed: {e}")
    
    # Fallback: look for name-like patterns in first few lines
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    for line in lines[:3]:
        words = line.split()
        if 2 <= len(words) <= 4 and all(word[0].isupper() for word in words):
            if not any(word.lower() in ['resume', 'cv', 'curriculum'] for word in words):
                return line
    
    return None

def extract_email(text: str):
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    match = re.search(email_pattern, text)
    return match.group(0) if match else None

def extract_phone(text: str):
    phone_patterns = [
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        r'\+\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
    ]
    
    for pattern in phone_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None

def extract_skills_with_hf(text: str):
    """Use zero-shot classification to detect skills"""
    skill_categories = {
        "programming": ["Python", "Java", "JavaScript", "C++", "C#", "Ruby", "Go", "Swift", "Kotlin", "TypeScript"],
        "web_frameworks": ["React", "Angular", "Vue", "Node.js", "Django", "Flask", "Spring", "Express", "FastAPI"],
        "databases": ["SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "Oracle", "SQLite", "NoSQL"],
        "cloud_tools": ["AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Git", "Jenkins", "Linux", "Windows"],
        "data_science": ["Machine Learning", "Data Science", "TensorFlow", "PyTorch", "Pandas", "NumPy", "AI", "Artificial Intelligence"],
        "soft_skills": ["Leadership", "Communication", "Teamwork", "Problem Solving", "Project Management", "Planning", "Agile", "Scrum"]
    }
    
    found_skills = []
    text_chunk = text[:1500]
    
    for category, skills in skill_categories.items():
        try:
            result = client.zero_shot_classification(
                text_chunk,
                candidate_labels=skills,
                model="facebook/bart-large-mnli",
            )
            
            # Add skills with high confidence
            for label, score in zip(result.labels, result.scores):
                if score > 0.7:
                    found_skills.append(label)
                    
        except Exception as e:
            print(f"Zero-shot classification failed for {category}: {e}")
            # Fallback: simple keyword matching
            for skill in skills:
                if skill.lower() in text.lower() and skill not in found_skills:
                    found_skills.append(skill)
    
    # Additional keyword matching as backup
    all_skills = [skill for skills in skill_categories.values() for skill in skills]
    for skill in all_skills:
        if re.search(rf'\b{re.escape(skill)}\b', text, re.IGNORECASE):
            if skill not in found_skills:
                found_skills.append(skill)
    
    return list(set(found_skills))  # Remove duplicates

def generate_summary_with_hf(text: str):
    """Generate professional summary using summarization model"""
    text_chunk = text[:1024]
    
    try:
        result = client.summarization(
            text_chunk,
            model="facebook/bart-large-cnn",
            max_length=150,
            min_length=50,
        )
        return result.summary_text
    except Exception as e:
        print(f"Summarization failed: {e}")
        return "Experienced professional with strong technical skills."

def extract_experience_with_hf(text: str):
    """Extract experience information using NER"""
    organizations = []
    
    try:
        result = client.token_classification(
            text[:1500],
            model="dbmdz/bert-large-cased-finetuned-conll03-english",
        )
        
        for entity in result:
            if entity.entity_group == 'ORG':
                organizations.append(entity.word)
                
    except Exception as e:
        print(f"Experience extraction failed: {e}")
    
    # Also look for experience section with regex
    experience_keywords = ['experience', 'work history', 'employment', 'professional experience']
    lines = text.split('\n')
    experience_lines = []
    
    in_experience_section = False
    for line in lines:
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in experience_keywords):
            if len(line_lower.split()) <= 4:  # Likely a section header
                in_experience_section = True
                continue
        
        if in_experience_section and line.strip():
            # Stop at next major section
            if line_lower and len(line_lower.split()) <= 3 and any(
                sec in line_lower for sec in ['education', 'skills', 'projects', 'certifications']
            ):
                break
            experience_lines.append(line.strip())
            if len(experience_lines) > 5:
                break
    
    return {
        "companies": organizations[:3],
        "experience_preview": experience_lines[:3] if experience_lines else ["Experience details extracted from resume"]
    }

def parse_resume(file_bytes: bytes, filename: str) -> dict:
    print("Using Hugging Face InferenceClient for resume parsing...")
    
    # Extract text
    text = ""
    if filename.endswith(".pdf"):
        text = extract_text_from_pdf(file_bytes)
    elif filename.endswith(".docx"):
        text = extract_text_from_docx(file_bytes)
    else:
        return {"error": "Unsupported file type"}

    if not text.strip():
        return {"error": "No text could be extracted from the document"}

    print(f"Extracted text length: {len(text)} characters")
    print("Calling Hugging Face APIs with InferenceClient...")
    
    # Extract information using HF APIs
    name = extract_name_with_hf(text)
    email = extract_email(text)
    phone = extract_phone(text)
    skills = extract_skills_with_hf(text)
    summary = generate_summary_with_hf(text)
    experience = extract_experience_with_hf(text)
    
    print(f"Found {len(skills)} skills: {skills}")
    print("AI parsing complete!")
    
    return {
        "name": name,
        "email": email,
        "phone": phone,
        "skills": skills,
        "professional_summary": summary,
        "experience": experience,
        "companies": experience.get("companies", []),
        "raw_text_preview": text[:500] + "...",
        "parsing_method": "Hugging Face InferenceClient"
    }

# Test function
def test_parsing():
    """Test the parser with sample resume text"""
    sample_resume = """
    JOHN DOE
    Senior Software Engineer
    Phone: (555) 123-4567
    Email: john.doe@email.com
    
    PROFESSIONAL SUMMARY
    Experienced software engineer with 5+ years in full-stack development. 
    Strong expertise in Python, JavaScript, React, and cloud technologies.
    
    EXPERIENCE
    Senior Software Engineer - Tech Company Inc. (2020-Present)
    - Developed scalable web applications using React and Node.js
    - Led a team of 5 developers in agile environment
    - Implemented CI/CD pipelines with Docker and Kubernetes
    
    Software Developer - Startup Co. (2018-2020)
    - Built RESTful APIs with Python and Flask
    - Managed AWS infrastructure and databases
    
    SKILLS
    Programming: Python, JavaScript, Java, SQL
    Frameworks: React, Node.js, Django, TensorFlow
    Tools: Docker, AWS, Git, Kubernetes
    """
    
    result = parse_resume(
        sample_resume.encode('utf-8'), 
        "test_resume.txt"
    )
    print("PARSING RESULT:")
    print(json.dumps(result, indent=2))

# Run test if executed directly
if __name__ == "__main__":
    test_parsing()