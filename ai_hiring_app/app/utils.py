# In app/utils.py
print("--- RUNNING utils.py (IMPROVED AI LOGIC - FINAL SKILLS FIX) ---")

import os
import re
import requests
from typing import List
from io import BytesIO
import docx
import pypdf

# --- Setup ---
HUGGINGFACE_API_KEY = os.environ.get("HUGGINGFACE_API_KEY")

QA_API_URL = "https://api-inference.huggingface.co/models/google-bert/bert-large-uncased-whole-word-masking-finetuned-squad"
SUMMARIZATION_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

# =============================================================
# SKILL LISTS MOVED TO TOP-LEVEL FOR GLOBAL ACCESS
# =============================================================
TECH_SKILLS = ["Python", "Java", "C++", "SQL", "AWS", "Docker", "Kubernetes", "React", "Node.js", "Django", "Flask", "TensorFlow", "PyTorch", "Git", "Linux"]
SOFT_SKILLS = ["Management", "Leadership", "Communication", "Problem Solving", "Teamwork", "Project Management", "Agile", "Scrum", "Client Relations", "Coordination"]


# --- Reusable API Functions ---
def query_api(api_url, payload, timeout=25):
    try:
        response = requests.post(api_url, headers=HEADERS, json=payload, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        error_info = "Unknown API Error"
        try:
            error_info = response.json().get("error", str(e))
        except:
            pass
        print(f"API call to {api_url} failed: {error_info}")
        return {"error": error_info}

def generate_summary(text: str) -> str:
    prompt = f"Summarize the following resume's 'Career Summary' section in one or two sentences. Do not add any information not present in that section.\n\nResume Text:\n\"\"\"{text[:1024]}\"\"\""
    output = query_api(SUMMARIZATION_API_URL, {"inputs": prompt})
    if "error" in output:
        print(f"AI summary error: {output.get('error')}")
        return "AI summary is being generated. Please wait."
    return output[0].get('summary_text', "Could not generate summary.")

def ask_question(context: str, question: str) -> str:
    output = query_api(QA_API_URL, {"inputs": {"question": question, "context": context}})
    if "error" in output: return None
    return output.get('answer') if output.get('score', 0) > 0.1 else None

# --- Main Parsing Function ---
def parse_resume(file_bytes: bytes, filename: str) -> dict:
    print("--- INSIDE THE IMPROVED PARSE_RESUME w/ BETTER LOGIC ---")
    
    raw_text = ""
    try:
        if filename.endswith(".pdf"):
            reader = pypdf.PdfReader(BytesIO(file_bytes))
            raw_text = "".join(page.extract_text() or "" for page in reader.pages)
        elif filename.endswith(".docx"):
            raw_text = "\n".join([p.text for p in docx.Document(BytesIO(file_bytes)).paragraphs])
        else:
            return {"error": "Unsupported file type."}
    except Exception as e:
        return {"error": f"Could not read file content: {e}"}

    context = raw_text[:4000]
    if not context:
        return {"error": "Could not extract any text from the document."}

    # --- HYBRID EXTRACTION ---
    name = ask_question(context, "What is the candidate's full name?")
    if not name:
        name_match = re.search(r"^([A-Z][a-z'’]+)\s([A-Z]\.\s)?([A-Z][a-z'’]+)", context.strip())
        name = name_match.group(0) if name_match else None

    email = ask_question(context, "What is the email address?")
    if not email:
        email_match = re.search(r"\b[A-Za-z0--9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", context)
        email = email_match.group(0) if email_match else None

    phone = ask_question(context, "What is the phone number?")
    education = ask_question(context, "What is the name of the university?")
    location = ask_question(context, "What city and state is listed in the address?")
    experience = ask_question(context, "How many years of experience are mentioned in the career summary?")
    current_title = ask_question(context, "What is the job title listed for the most recent employment history date?")

    # This now correctly references the global skill lists
    all_skills = TECH_SKILLS + SOFT_SKILLS
    skills_list = {skill for skill in all_skills if re.search(r"\b" + re.escape(skill) + r"\b", raw_text, re.IGNORECASE)}
    
    summary = generate_summary(raw_text)

    return {
        "full_name": name, "email": email, "phone": phone,
        "location": location, "current_title": current_title, "experience": experience,
        "skills": sorted(list(skills_list)),
        "education": education, "professional_summary": summary, "raw_text": raw_text[:2000]
    }

# --- Unchanged Function ---
def calculate_match_score(candidate_skills: List[str], job_skills: List[str]) -> int:
    if not job_skills or not candidate_skills: return 0
    common_skills = set(c.lower() for c in candidate_skills) & set(j.lower() for j in job_skills)
    return int((len(common_skills) / len(job_skills)) * 100)