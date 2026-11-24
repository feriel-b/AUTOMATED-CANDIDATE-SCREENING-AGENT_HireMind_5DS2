import spacy
import re
from io import BytesIO
import docx
import pypdf

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(file_bytes: bytes) -> str:
    pdf_reader = pypdf.PdfReader(BytesIO(file_bytes))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = docx.Document(BytesIO(file_bytes))
    return "\n".join([para.text for para in doc.paragraphs])

def extract_name(text: str):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None

def extract_email(text: str):
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    match = re.search(email_pattern, text)
    return match.group(0) if match else None

def extract_skills(text: str, skills_list: list):
    found_skills = set()
    for skill in skills_list:
        if re.search(r"\b" + re.escape(skill) + r"\b", text, re.IGNORECASE):
            found_skills.add(skill)
    return list(found_skills)

def parse_resume(file_bytes: bytes, filename: str) -> dict:
    text = ""
    if filename.endswith(".pdf"):
        text = extract_text_from_pdf(file_bytes)
    elif filename.endswith(".docx"):
        text = extract_text_from_docx(file_bytes)
    else:
        return {"error": "Unsupported file type"}

    name = extract_name(text)
    email = extract_email(text)
    
    SKILLS = ["Python", "JavaScript", "React", "Node.js", "SQL", "AWS", "Machine Learning", "FastAPI"]
    skills = extract_skills(text, SKILLS)
    
    return {
        "name": name,
        "email": email,
        "skills": skills,
        "raw_text": text[:500] + "..."
    }