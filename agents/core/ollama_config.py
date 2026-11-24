"""
Ollama configuration for local LLM usage.
"""

from langchain_ollama import OllamaLLM  # FIXED: Use new import
import logging
import requests
import os

logger = logging.getLogger(__name__)

class OllamaConfig:
    """Centralized Ollama configuration."""
    
    MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "phi4-mini")
    BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    @classmethod
    def get_llm(cls, temperature: float = 0.7) -> OllamaLLM:
        """
        Get Ollama LLM instance.
        
        Args:
            temperature: Generation temperature (0.0-1.0)
            
        Returns:
            Configured Ollama LLM
        """
        return OllamaLLM(
            model=cls.MODEL_NAME,
            base_url=cls.BASE_URL,
            temperature=temperature
        )
    
    @classmethod
    def check_availability(cls) -> bool:
        """
        Check if Ollama server is running.
        
        Returns:
            True if available, False otherwise
        """
        try:
            response = requests.get(f"{cls.BASE_URL}/api/tags")
            response.raise_for_status()
            models = response.json().get("models", [])
            available = any(m["name"].startswith(cls.MODEL_NAME) for m in models)
            
            if available:
                logger.info(f"✅ Ollama {cls.MODEL_NAME} is available")
            else:
                logger.warning(f"⚠️ {cls.MODEL_NAME} not found. Run: ollama pull {cls.MODEL_NAME}")
            
            return available
        except Exception as e:
            logger.error(f"❌ Ollama server not reachable: {e}")
            logger.info("💡 Start Ollama: ollama serve")
            return False


# Test on import
if __name__ == "__main__":
    OllamaConfig.check_availability()