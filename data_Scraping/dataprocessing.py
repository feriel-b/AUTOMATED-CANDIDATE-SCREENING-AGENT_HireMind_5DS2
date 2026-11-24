
import json
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer

# Download required NLTK resources (only run once)
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')

def clean_text(text):
    """Remove unwanted characters, HTML, and normalize spaces."""
    text = re.sub(r'<[^>]+>', '', text)  # remove HTML tags
    text = re.sub(r'[^a-zA-Z0-9\s.,;:!?-]', '', text)  # keep only valid chars
    text = re.sub(r'\s+', ' ', text)  # normalize spaces
    return text.strip()

def process_text(text):
    """Tokenize, clean, stem, and lemmatize text."""
    stop_words = set(stopwords.words('english'))
    stemmer = PorterStemmer()
    lemmatizer = WordNetLemmatizer()
    
    tokens = word_tokenize(text.lower())
    cleaned_tokens = [
        lemmatizer.lemmatize(stemmer.stem(word))
        for word in tokens if word.isalnum() and word not in stop_words
    ]
    return " ".join(cleaned_tokens)

def restructure_description(description):
    """Split description into structured sections."""
    sections = {}
    # Example: match headers like --- COMPANY & JOB DETAILS ---
    parts = re.split(r'---\s*(.*?)\s*---', description)
    
    if len(parts) > 1:
        # even indexes = text, odd indexes = section titles
        for i in range(1, len(parts), 2):
            section_title = parts[i].strip().upper()
            section_text = clean_text(parts[i+1]) if i+1 < len(parts) else ""
            sections[section_title] = process_text(section_text)
    else:
        # fallback: clean entire text
        sections["FULL_TEXT"] = process_text(description)
    
    return sections

# Load dataset
with open("jobicy_remote_jobs_data_structuredv2.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Process each job
for job in data:
    raw_description = job.get("job_description_full", "")
    structured_desc = restructure_description(raw_description)
    job["full_description"] = structured_desc
    # Remove old field if needed
    job.pop("job_description_full", None)

# Save to output file
with open("output_jobicy.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("✅ Processed job descriptions saved to output.json")
