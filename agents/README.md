# 🎓 Interview Intelligence Platform (Enhanced with Video & Emotion Analysis)

> **Beginner-friendly** AI-powered interview practice with **video emotion recognition** and **voice stress detection**.  
> **Runs on CPU** — no GPU required! (31GB free disk space recommended)

## 🎯 What This Does

This project provides two microservices:

### 1. **Interview Simulator** 🎤🎥
   - **Upload video or audio** of your interview answers
   - **Automatic transcription** (speech-to-text via Vosk)
   - **Emotion recognition** from your facial expressions (7 emotions: happy, sad, angry, etc.)
   - **Voice stress analysis** (detect anxiety from pitch/tone variations)
   - **Prosody metrics** (speaking rate, pauses, energy)
   - **Semantic scoring** (relevance, clarity)
   - **Q&A Bank:** 50+ interview questions across categories (technical, behavioral, situational)

### 2. **Cheating Detector** 🕵️
   - **Video analysis:** Detect off-screen glances, multiple faces, face absence
   - **Audio analysis:** Identify AI-generated voices, unnatural speech patterns
   - **Text analysis:** Detect AI-written responses (GPT, ChatGPT patterns)
   - **Timing analysis:** Flag suspiciously fast/perfect responses
   - **Multi-modal scoring:** Combine video, audio, and text signals

**Use Cases:**
- **Job applicants:** Practice interviews with AI feedback on emotions and stress
- **Recruiters:** Screen remote interviews for potential cheating/AI assistance
- **Students:** Learn about computer vision, speech processing, and NLP
- **Researchers:** Benchmark emotion recognition and stress detection algorithms

---

## 🚀 Quick Start (10 Minutes)

### Prerequisites

- **Python 3.10 or 3.11** (check: `python --version`)
- **31GB free disk space** (models + dependencies + sample videos)
- **Webcam** (optional, for recording test videos)
- **Microphone** (optional, for audio-only testing)

### Installation

```bash
# 1. Clone or download this repository
cd interview-intelligence-platform

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Install dependencies (takes 10-15 minutes, downloads ~2-3GB)
pip install --upgrade pip
pip install -r [requirements.txt](http://_vscodecontentref_/1)

# 5. Download speech and emotion models (one-time setup, ~500MB)
python scripts/download_models.py

# 6. Download spaCy English model
python -m spacy download en_core_web_sm

# 7. Create sample Q&A bank
python scripts/create_qa_bank.py

##Run the Services
# Terminal 1: Start Interview Simulator
uvicorn services.interview_simulator.app:app --port 8001 --reload

# Terminal 2: Start Cheating Detector
uvicorn services.cheating_detector.app:app --port 8002 --reload