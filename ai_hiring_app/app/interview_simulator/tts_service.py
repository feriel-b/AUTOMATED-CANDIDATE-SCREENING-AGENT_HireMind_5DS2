"""Text-to-Speech service for AI interview simulator."""

import os
import tempfile
from pathlib import Path
from typing import Optional
import hashlib

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False


class TTSService:
    """Text-to-Speech service using gTTS."""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize TTS service with optional cache directory."""
        if cache_dir is None:
            cache_dir = Path(tempfile.gettempdir()) / "interview_tts_cache"
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        if not GTTS_AVAILABLE:
            raise ImportError(
                "gTTS not installed. Install with: pip install gTTS"
            )
    
    def _get_cache_path(self, text: str, lang: str = "en") -> Path:
        """Generate cache file path based on text hash."""
        text_hash = hashlib.md5(f"{text}_{lang}".encode()).hexdigest()
        return self.cache_dir / f"{text_hash}.mp3"
    
    def generate_speech(
        self, 
        text: str, 
        lang: str = "en",
        slow: bool = False
    ) -> Path:
        """
        Generate speech audio from text.
        
        Args:
            text: Text to convert to speech
            lang: Language code (default: 'en')
            slow: Use slower speech rate
        
        Returns:
            Path to generated audio file (MP3)
        """
        # Check cache first
        cache_path = self._get_cache_path(text, lang)
        if cache_path.exists():
            return cache_path
        
        # Generate new audio
        tts = gTTS(text=text, lang=lang, slow=slow)
        tts.save(str(cache_path))
        
        return cache_path
    
    def clear_cache(self):
        """Clear all cached audio files."""
        for file in self.cache_dir.glob("*.mp3"):
            file.unlink()


# Global instance
_tts_service: Optional[TTSService] = None


def get_tts_service() -> TTSService:
    """Get or create global TTS service instance."""
    global _tts_service
    if _tts_service is None:
        _tts_service = TTSService()
    return _tts_service
