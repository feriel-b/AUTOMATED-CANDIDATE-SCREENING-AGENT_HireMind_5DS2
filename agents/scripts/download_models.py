

"""
Download required models for speech recognition, NLP, and emotion detection.
This script is run once during setup.
"""

import os
import urllib.request
import zipfile
from pathlib import Path

def download_vosk_model():
    """
    Download small English Vosk model (~40MB).
    
    Vosk offers different model sizes:
    - Small (40MB): Fast, 90% accuracy — good for demos
    - Medium (1GB): Better accuracy
    - Large (2GB): Best accuracy, slower
    
    We use the small model for CPU performance.
    """
    model_dir = Path("data/vosk_models")
    model_dir.mkdir(parents=True, exist_ok=True)
    
    model_name = "vosk-model-small-en-us-0.15"
    model_path = model_dir / model_name
    
    if model_path.exists():
        print(f"✅ Vosk model already exists: {model_path}")
        return
    
    print(f"📥 Downloading Vosk model ({model_name})...")
    url = f"https://alphacephei.com/vosk/models/{model_name}.zip"
    zip_path = model_dir / f"{model_name}.zip"
    
    # Download with progress
    def show_progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        percent = min(downloaded / total_size * 100, 100)
        print(f"\rProgress: {percent:.1f}%", end="")
    
    urllib.request.urlretrieve(url, zip_path, show_progress)
    print("\n✅ Download complete!")
    
    # Extract
    print("📦 Extracting...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(model_dir)
    
    # Clean up
    zip_path.unlink()
    print(f"✅ Model ready at: {model_path}")

def download_sentence_transformer():
    """
    Download sentence-transformers model for semantic similarity.
    
    This happens automatically on first use, but we trigger it here
    to avoid delays during first API call.
    """
    print("📥 Downloading sentence-transformers model...")
    from sentence_transformers import SentenceTransformer
    
    # This model is only 80MB and works well on CPU
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("✅ Sentence transformer model cached!")

def setup_deepface():
    """
    Initialize DeepFace to download emotion recognition models.
    
    DeepFace will auto-download models (~200MB total) on first use:
    - Facenet: 92MB (face recognition)
    - Emotion model: 1.2MB (emotion classifier)
    - Age/gender models: ~50MB (optional, we don't use these)
    
    This can take 5-10 minutes on first run.
    """
    print("📥 Setting up DeepFace emotion models...")
    print("(This will download ~200MB of models, may take 5-10 minutes)")
    
    try:
        from deepface import DeepFace
        import numpy as np
        
        # Create a dummy image to trigger model download
        dummy_img = np.zeros((224, 224, 3), dtype=np.uint8)
        
        # This will download the emotion model
        print("  → Downloading emotion recognition model...")
        result = DeepFace.analyze(
            dummy_img, 
            actions=['emotion'],
            enforce_detection=False,  # Skip face detection for dummy image
            silent=True
        )
        print("✅ DeepFace emotion models ready!")
        
    except Exception as e:
        print(f"⚠️ DeepFace setup encountered an issue: {e}")
        print("Don't worry - models will download automatically on first use.")

def download_spacy_model():
    """
    Download spaCy English model for NLP tasks.
    """
    print("📥 Downloading spaCy English model...")
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    print("✅ spaCy model ready!")

def main():
    print("🚀 Setting up Interview Intelligence Platform models...\n")
    print("Total download size: ~2-3 GB")
    print("This may take 15-30 minutes depending on your internet speed.\n")
    
    # Create data directories
    Path("data/uploads").mkdir(parents=True, exist_ok=True)
    Path("data/vosk_models").mkdir(parents=True, exist_ok=True)
    Path("data/deepface_models").mkdir(parents=True, exist_ok=True)
    Path("data/sessions.db").parent.mkdir(parents=True, exist_ok=True)
    
    # Download models
    print("\n" + "="*60)
    print("STEP 1/4: Vosk Speech Model")
    print("="*60)
    download_vosk_model()
    
    print("\n" + "="*60)
    print("STEP 2/4: Sentence Transformers")
    print("="*60)
    download_sentence_transformer()
    
    print("\n" + "="*60)
    print("STEP 3/4: DeepFace Emotion Models")
    print("="*60)
    setup_deepface()
    
    print("\n" + "="*60)
    print("STEP 4/4: spaCy NLP Model")
    print("="*60)
    download_spacy_model()
    
    print("\n" + "="*60)
    print("🎉 Setup complete! All models downloaded.")
    print("="*60)
    print("\nNext steps:")
    print("1. Terminal 1: uvicorn services.interview_simulator.app:app --port 8001")
    print("2. Terminal 2: uvicorn services.cheating_detector.app:app --port 8002")
    print("\nTest with sample video:")
    print("  curl -X POST http://localhost:8001/submit_answer \\")
    print("    -F 'video=@tests/sample_data/sample_video.mp4' \\")
    print("    -F 'question_id=1'")

if __name__ == "__main__":
    main()