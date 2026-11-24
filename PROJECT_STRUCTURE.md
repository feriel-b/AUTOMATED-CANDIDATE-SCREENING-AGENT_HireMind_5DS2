# 🎯 HireMind - Complete Project Structure

## 📁 Directory Tree

```
AUTOATED-CANDIDATE-SCREENING-AGENT_HireMind_5DS2-youssef/
│
├── 📘 QUICK_START.md                    # Fast setup guide
├── 📘 INTERVIEW_SIMULATOR_README.md     # Complete documentation
├── 📘 .gitignore                        # Git ignore rules
│
├── ai_hiring_app/                       # Backend Application
│   ├── docker-compose.yml               # Multi-container orchestration
│   ├── Dockerfile                       # Container build config (UPDATED)
│   ├── requirements.txt                 # Python dependencies (UPDATED)
│   │
│   └── app/                             # Main application
│       ├── __init__.py
│       ├── main.py                      # FastAPI app (UPDATED with interview endpoints)
│       ├── models.py                    # Database ORM models
│       ├── schemas.py                   # Pydantic schemas (UPDATED with VoiceAnalysisResult)
│       ├── database.py                  # PostgreSQL connection
│       │
│       ├── ai_modules/                  # Original AI features
│       │   ├── __init__.py
│       │   ├── resume_parser.py         # Resume parsing (spaCy)
│       │   └── matching_engine.py       # Candidate ranking algorithm
│       │
│       └── interview_simulator/         # ✨ NEW: Interview Module
│           ├── __init__.py
│           └── voice_analyzer.py        # Voice stress detection AI
│
└── frontend/                            # ✨ NEW: React Frontend
    ├── package.json                     # Node dependencies
    │
    ├── public/
    │   └── index.html                   # HTML template
    │
    └── src/
        ├── index.js                     # React entry point
        ├── index.css                    # Global styles
        ├── App.js                       # Main app component
        ├── App.css                      # App styles
        │
        └── components/
            ├── VoiceRecorder.js         # Audio recording interface
            ├── VoiceRecorder.css        # Recorder styles
            ├── StressResults.js         # Results visualization
            └── StressResults.css        # Results styles
```

---

## 🎨 Feature Breakdown

### ✅ **Original Features (Existing)**
| Feature | Location | Technology |
|---------|----------|------------|
| Resume Upload & Parsing | `ai_modules/resume_parser.py` | spaCy NLP, PyPDF, python-docx |
| Job Posting Management | `main.py` endpoints | FastAPI, PostgreSQL |
| Candidate Ranking | `ai_modules/matching_engine.py` | Set-based matching algorithm |
| Database Storage | `models.py`, `database.py` | SQLAlchemy ORM, PostgreSQL |

### ✨ **New Features (Phase 1)**
| Feature | Location | Technology |
|---------|----------|------------|
| Voice Recording | `frontend/components/VoiceRecorder.js` | MediaRecorder API |
| Stress Detection | `interview_simulator/voice_analyzer.py` | Wav2Vec2, HuggingFace Transformers |
| Results Visualization | `frontend/components/StressResults.js` | React, CSS animations |
| Audio Processing | `voice_analyzer.py` | TorchAudio, Librosa |

---

## 🔌 API Endpoints Overview

### **Original Endpoints**
```
GET  /                                    # Welcome message
POST /jobs/                               # Create job posting
GET  /jobs/                               # List all jobs
POST /upload/resume/                      # Upload & parse resume
GET  /jobs/{job_id}/candidates/rank      # Ranked candidates for job
```

### **New Interview Endpoints**
```
POST /interview/analyze-voice             # Analyze voice stress
GET  /interview/health                    # Module health check
```

---

## 🗄️ Database Schema

### **Existing Tables**
```sql
jobs
├── id (PK)
├── title
├── description
└── required_skills (ARRAY)

candidates
├── id (PK)
├── name
├── email (UNIQUE)
├── skills (ARRAY)
└── raw_text
```

### **Future Tables (Phase 3)**
```sql
interview_sessions (planned)
├── id (PK)
├── candidate_id (FK)
├── job_id (FK)
├── start_time
└── end_time

interview_responses (planned)
├── id (PK)
├── session_id (FK)
├── question_id (FK)
├── audio_url
├── stress_score
├── duration
└── analysis_results (JSON)
```

---

## 🧠 ML Models Used

| Model | Purpose | Size | Load Time |
|-------|---------|------|-----------|
| **en_core_web_sm** | Resume NER | ~12 MB | <1s |
| **Wav2Vec2 Base** | Audio embeddings | ~360 MB | ~5s |
| **StudentNet** | Stress classification | ~1 MB | <1s |

**Total ML footprint:** ~373 MB

---

## 🚀 Deployment Ports

| Service | Port | Protocol |
|---------|------|----------|
| FastAPI Backend | 8000 | HTTP |
| React Frontend | 3000 | HTTP |
| PostgreSQL | 5433 (host) / 5432 (container) | TCP |

---

## 📦 Dependencies Summary

### **Backend**
- **Web**: FastAPI, Uvicorn, Pydantic
- **Database**: SQLAlchemy, psycopg2-binary
- **NLP**: spaCy
- **ML**: PyTorch, TorchAudio, Transformers
- **Audio**: librosa, soundfile, audioread
- **Files**: python-multipart, PyPDF, python-docx

### **Frontend**
- **Core**: React 18, ReactDOM
- **HTTP**: Axios
- **Charts**: Recharts (for future analytics)
- **Build**: react-scripts

---

## 🔄 Data Flow

### **Resume Screening Flow (Original)**
```
Upload Resume → Parse PDF/DOCX → Extract (Name, Email, Skills)
→ Save to PostgreSQL → Match against Jobs → Return Ranked List
```

### **Interview Analysis Flow (New)**
```
Record Audio → Upload WebM/WAV → Preprocess Audio → Extract Wav2Vec2 Embeddings
→ Predict Stress → Return Analysis → Visualize Results
```

---

## 🎯 Technology Stack Summary

```
┌─────────────────────────────────────────┐
│          FRONTEND (React)               │
│  • Audio Recording (MediaRecorder)      │
│  • Real-time UI Updates                 │
│  • Results Visualization                │
└──────────────┬──────────────────────────┘
               │ HTTP/REST API
┌──────────────▼──────────────────────────┐
│       BACKEND (FastAPI + AI)            │
│  • Resume Parser (spaCy)                │
│  • Voice Analyzer (Wav2Vec2/StudentNet) │
│  • Matching Engine                      │
│  • API Endpoints                        │
└──────────────┬──────────────────────────┘
               │ SQLAlchemy ORM
┌──────────────▼──────────────────────────┐
│        DATABASE (PostgreSQL)            │
│  • Jobs Table                           │
│  • Candidates Table                     │
│  • Persistent Storage                   │
└─────────────────────────────────────────┘
```

---

## 📊 File Statistics

| Category | Files | Lines of Code (approx) |
|----------|-------|------------------------|
| Backend Python | 8 | ~650 |
| Frontend React | 8 | ~550 |
| Config Files | 4 | ~100 |
| Documentation | 3 | ~600 |
| **Total** | **23** | **~1,900** |

---

## 🎓 Learning Resources

**Technologies You're Using:**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [PyTorch Audio](https://pytorch.org/audio/stable/index.html)
- [HuggingFace Transformers](https://huggingface.co/docs/transformers)
- [spaCy NLP](https://spacy.io/usage)

**AI Models:**
- [Wav2Vec2 Paper](https://arxiv.org/abs/2006.11477)
- [Voice Stress Model](https://huggingface.co/forwarder1121/voice-based-stress-recognition)

---

## 🔮 Roadmap

- [x] **Phase 1**: Voice Stress Analysis ✅
- [ ] **Phase 2**: Advanced Audio Features (pauses, fillers)
- [ ] **Phase 3**: Question Bank & Session Management
- [ ] **Phase 4**: Answer Quality Analysis (speech-to-text + NLP)
- [ ] **Phase 5**: Video Analysis (eye contact, body language)
- [ ] **Phase 6**: Full Interview Reports & Coaching

---

**Current Status:** Phase 1 Complete! 🎉

**Next Step:** Run the application and test it!
