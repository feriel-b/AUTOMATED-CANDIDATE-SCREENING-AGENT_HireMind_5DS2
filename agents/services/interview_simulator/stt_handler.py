"""
Speech-to-Text Handler using Vosk.

Vosk is an offline speech recognition toolkit that runs on CPU.
It converts audio/video files to text transcripts.
"""

import json
import wave
import logging
from pathlib import Path
from typing import Optional
import subprocess
import os

# Vosk imports
from vosk import Model, KaldiRecognizer

logger = logging.getLogger(__name__)

class SpeechToTextHandler:
    """
    Handles speech-to-text conversion using Vosk.
    
    Vosk supports:
    - Multiple languages (we use English)
    - Offline processing (no API calls)
    - CPU-friendly models
    """
    
    def __init__(self, model_path: str = "data/vosk_models/vosk-model-small-en-us-0.15"):
        """
        Initialize Vosk speech recognition model.
        
        Args:
            model_path: Path to Vosk model directory
        """
        self.model_path = Path(model_path)
        
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Vosk model not found at {self.model_path}. "
                f"Run: python scripts/download_models.py"
            )
        
        logger.info(f"Loading Vosk model from {self.model_path}")
        self.model = Model(str(self.model_path))
        logger.info("✅ Vosk model loaded successfully")
    
    def transcribe_audio(
        self,
        audio_path: str,
        sample_rate: int = 16000
    ) -> str:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file (WAV format, 16kHz mono)
            sample_rate: Audio sample rate (Vosk works best with 16kHz)
            
        Returns:
            Transcript text
        """
        audio_path = Path(audio_path)
        
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Convert to WAV if needed (Vosk requires WAV format)
        if audio_path.suffix.lower() != '.wav':
            logger.info(f"Converting {audio_path.suffix} to WAV format...")
            audio_path = self._convert_to_wav(audio_path)
        
        logger.info(f"Transcribing: {audio_path}")
        
        # Open audio file
        wf = wave.open(str(audio_path), "rb")
        
        # Verify audio format
        if wf.getnchannels() != 1:
            logger.warning(f"Audio has {wf.getnchannels()} channels, converting to mono...")
            wf.close()
            audio_path = self._convert_to_mono(audio_path)
            wf = wave.open(str(audio_path), "rb")
        
        if wf.getframerate() != sample_rate:
            logger.warning(f"Audio sample rate is {wf.getframerate()}Hz, expected {sample_rate}Hz")
            # Vosk can handle different sample rates, but 16kHz is optimal
        
        # Create recognizer
        recognizer = KaldiRecognizer(self.model, wf.getframerate())
        recognizer.SetWords(True)  # Get word-level timestamps
        
        # Process audio in chunks
        transcript_parts = []
        
        while True:
            data = wf.readframes(4000)  # Read 4000 frames at a time
            if len(data) == 0:
                break
            
            if recognizer.AcceptWaveform(data):
                # Partial result (end of sentence)
                result = json.loads(recognizer.Result())
                if result.get("text"):
                    transcript_parts.append(result["text"])
        
        # Get final result
        final_result = json.loads(recognizer.FinalResult())
        if final_result.get("text"):
            transcript_parts.append(final_result["text"])
        
        wf.close()
        
        # Combine all parts
        full_transcript = " ".join(transcript_parts).strip()
        
        logger.info(f"✅ Transcription complete ({len(full_transcript)} characters)")
        return full_transcript
    
    def extract_audio_from_video(self, video_path: str) -> str:
        """
        Extract audio track from video file using ffmpeg.
        
        Args:
            video_path: Path to video file (MP4, AVI, etc.)
            
        Returns:
            Path to extracted WAV file
        """
        video_path = Path(video_path)
        output_path = video_path.parent / f"{video_path.stem}_audio.wav"
        
        logger.info(f"Extracting audio from {video_path}")
        
        # Use ffmpeg to extract audio
        # -vn: no video
        # -acodec pcm_s16le: 16-bit PCM audio
        # -ar 16000: 16kHz sample rate
        # -ac 1: mono
        cmd = [
            "ffmpeg",
            "-i", str(video_path),
            "-vn",  # No video
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            "-y",  # Overwrite output
            str(output_path)
        ]
        
        try:
            subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            logger.info(f"✅ Audio extracted to {output_path}")
            return str(output_path)
        
        except subprocess.CalledProcessError as e:
            logger.error(f"ffmpeg failed: {e.stderr.decode()}")
            raise RuntimeError("Failed to extract audio from video")
        except FileNotFoundError:
            raise RuntimeError(
                "ffmpeg not found. Install with: "
                "sudo apt install ffmpeg (Linux) or brew install ffmpeg (Mac)"
            )
    
    def _convert_to_wav(self, audio_path: Path) -> Path:
        """
        Convert audio file to WAV format using ffmpeg.
        
        Args:
            audio_path: Path to input audio file
            
        Returns:
            Path to converted WAV file
        """
        output_path = audio_path.parent / f"{audio_path.stem}_converted.wav"
        
        cmd = [
            "ffmpeg",
            "-i", str(audio_path),
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            "-y",
            str(output_path)
        ]
        
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output_path
    
    def _convert_to_mono(self, audio_path: Path) -> Path:
        """
        Convert stereo audio to mono.
        
        Args:
            audio_path: Path to stereo WAV file
            
        Returns:
            Path to mono WAV file
        """
        output_path = audio_path.parent / f"{audio_path.stem}_mono.wav"
        
        cmd = [
            "ffmpeg",
            "-i", str(audio_path),
            "-ac", "1",  # 1 audio channel (mono)
            "-y",
            str(output_path)
        ]
        
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output_path

# Global instance
stt_handler = SpeechToTextHandler()