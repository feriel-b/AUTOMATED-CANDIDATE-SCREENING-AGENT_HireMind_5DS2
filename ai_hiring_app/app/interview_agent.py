print("--- LOADING AI INTERVIEW AGENT MODULE (FINAL, SIMPLEST FIX) ---")

import os
import requests
from typing import List, Dict

# --- Simplified Imports ---
from deepgram import DeepgramClient
from elevenlabs import ElevenLabs

# --- Configuration ---
DEEPGRAM_API_KEY = os.environ.get("DEEPGRAM_API_KEY")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
HUGGINGFACE_API_KEY = os.environ.get("HUGGINGFACE_API_KEY")

LLM_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

# --- Initialize Clients ---
deepgram = DeepgramClient(api_key=DEEPGRAM_API_KEY)
elevenlabs = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# --- Core Agent Functions ---
def transcribe_audio(audio_bytes: bytes) -> str:
    """Uses Deepgram to transcribe an entire audio clip."""
    try:
        source = {"buffer": audio_bytes, "mimetype": "audio/webm"}

        # Simplified Deepgram v3 API usage
        response = deepgram.listen.prerecorded.transcribe_file(
            source,
            options={"smart_format": True, "model": "nova-2"}
        )

        transcript = response["results"]["channels"][0]["alternatives"][0]["transcript"]
        return transcript if transcript else "I couldn't hear anything."
    except Exception as e:
        print(f"Deepgram transcription failed: {e}")
        import traceback
        traceback.print_exc()
        return "Error during transcription."

def generate_next_question(job_description: str, conversation_history: List[Dict]) -> str:
    """Generate the next question based on the job description and conversation."""
    history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
    prompt = (
        f"You are an AI interviewer for a job with this description: \"{job_description}\". "
        f"Based on the conversation history, ask the next relevant and concise question.\n\n"
        f"History:\n{history_str}\n\nAI Interviewer:"
    )

    try:
        response = requests.post(
            LLM_API_URL,
            headers=HEADERS,
            json={"inputs": prompt, "parameters": {"max_new_tokens": 50}}
        )
        response.raise_for_status()
        generated_text = response.json()[0]['generated_text']
        new_question = generated_text.split("AI Interviewer:")[-1].strip()
        return new_question or "Could you please elaborate on that?"
    except Exception as e:
        print(f"LLM question generation failed: {e}")
        return "Thank you, that's all the questions I have for now."

def convert_text_to_speech(text: str) -> bytes:
    """Converts text to speech using ElevenLabs."""
    try:
        audio_bytes = elevenlabs.generate(
            text=text,
            voice="Rachel",
            model="eleven_multilingual_v2"
        )
        return audio_bytes
    except Exception as e:
        print(f"ElevenLabs text-to-speech failed: {e}")
        return f"Error generating audio.".encode("utf-8")
