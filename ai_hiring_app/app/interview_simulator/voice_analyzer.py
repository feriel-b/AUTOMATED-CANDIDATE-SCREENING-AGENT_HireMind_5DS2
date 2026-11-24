"""
Voice Stress Analyzer Module
Uses Wav2Vec2 for audio embeddings and HuggingFace stress recognition model
to analyze candidate's stress levels during interview responses.
"""

import torch
import torch.nn.functional as F
import torch.nn as nn
import torchaudio
from transformers import AutoConfig, AutoModelForAudioClassification
from huggingface_hub import hf_hub_download
import importlib.util
from typing import Dict, Tuple
import os
from typing import Dict, Tuple
import io
import logging
import subprocess
import shutil
import wave
import numpy as np
import librosa
import whisper
import imageio_ffmpeg
from scipy import signal
import re
# Try to import WebRTC VAD from either canonical package or Windows wheels
try:
    import webrtcvad as _webrtcvad  # Robust Voice Activity Detection
except Exception:
    try:
        import webrtcvad_wheels as _webrtcvad  # Fallback module name on Windows
    except Exception as _vad_err:
        _webrtcvad = None

# Normalize to a single name
webrtcvad = _webrtcvad

logger = logging.getLogger(__name__)


class VoiceStressAnalyzer:
    """
    Analyzes voice recordings to detect stress levels using:
    1. Wav2Vec2 (base) for audio feature extraction
    2. StudentNet model for stress classification
    """
    
    def __init__(self):
        """Initialize the analyzer with required models"""
        logger.info("Initializing Voice Stress Analyzer...")
        
        # Load Wav2Vec2 model for embedding extraction
        try:
            self.w2v_bundle = torchaudio.pipelines.WAV2VEC2_BASE
            self.w2v_model = self.w2v_bundle.get_model()
            self.w2v_model.eval()
            logger.info("✓ Wav2Vec2 model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Wav2Vec2: {e}")
            raise
        
        # Load stress recognition model from HuggingFace (dynamic import of custom code)
        try:
            logger.info("Loading stress recognition model from Hugging Face via dynamic import...")
            repo = "forwarder1121/voice-based-stress-recognition"

            # 1) Download the custom models.py from the repo (pin to main to avoid unexpected changes)
            code_path = hf_hub_download(repo_id=repo, filename="models.py", revision="main")

            # 2) Dynamically load it as a Python module
            spec = importlib.util.spec_from_file_location("hf_models", code_path)
            if spec is None or spec.loader is None:
                raise RuntimeError("Failed to create import spec for Hugging Face models.py")
            hf_models = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(hf_models)

            # 3) Instantiate config and model defined in the repo
            config = hf_models.StressConfig()
            self.stress_model = hf_models.StudentForAudioClassification(config)
            self.stress_model.eval()

            # Read expected input dimension from config if present
            self.expected_embed_dim = (
                getattr(config, "input_dim", None)
                or getattr(config, "in_features", None)
                or getattr(config, "hidden_size", None)
                or 512
            )
            # Try to infer expected input dimension from the model architecture
            inferred_dim = self._infer_model_input_dim()
            if inferred_dim and inferred_dim != self.expected_embed_dim:
                logger.info(
                    f"Overriding expected embedding dim from config ({self.expected_embed_dim}) to inferred {inferred_dim}"
                )
                self.expected_embed_dim = inferred_dim
            logger.info(
                f"✓ Stress recognition model loaded successfully (expected embedding dim: {self.expected_embed_dim})"
            )
        except Exception as e:
            logger.error(f"Failed to load stress model: {e}")
            raise
        
        # Expected sample rate from Wav2Vec2
        self.expected_sample_rate = self.w2v_bundle.sample_rate
        logger.info(f"Expected audio sample rate: {self.expected_sample_rate} Hz")
        
        # Initialize Whisper ASR model for transcript analysis (Phase 2)
        try:
            logger.info("Loading Whisper ASR model for transcript analysis...")
            self.whisper_model = whisper.load_model("base")  # Light model for fast inference
            logger.info("✓ Whisper ASR model loaded successfully")
        except Exception as e:
            logger.warning(f"Whisper ASR model loading failed: {e}. Transcript features will be disabled.")
            self.whisper_model = None

        # Initialize WebRTC VAD if available
        if webrtcvad is not None:
            try:
                # Aggressiveness: 0 (least aggressive) to 3 (most). 2 is a good default.
                self.vad = webrtcvad.Vad(2)
                mod_name = getattr(webrtcvad, "__name__", "webrtcvad")
                logger.info(f"✓ WebRTC VAD initialized from {mod_name} (aggressiveness=2)")
            except Exception as e:
                logger.warning(f"WebRTC VAD init failed: {e}")
                self.vad = None
        else:
            logger.warning("WebRTC VAD not available. Falling back to librosa-based speech detection.")
            self.vad = None

    def try_enable_vad(self, aggressiveness: int = 2) -> bool:
        """
        Attempt to (re)initialize WebRTC VAD at runtime, e.g., after installing the package
        without restarting the server. Returns True if VAD becomes available.
        """
        try:
            global webrtcvad
            if self.vad is not None:
                return True
            # Try importing if module not yet available
            if webrtcvad is None:
                import importlib
                try:
                    webrtcvad = importlib.import_module("webrtcvad")
                except Exception:
                    try:
                        webrtcvad = importlib.import_module("webrtcvad_wheels")
                    except Exception:
                        webrtcvad = None
            if webrtcvad is None:
                return False
            self.vad = webrtcvad.Vad(int(aggressiveness))
            mod_name = getattr(webrtcvad, "__name__", "webrtcvad")
            logger.info(f"✓ WebRTC VAD enabled at runtime from {mod_name} (aggressiveness={aggressiveness})")
            return True
        except Exception as e:
            logger.warning(f"Runtime VAD enable failed: {e}")
            self.vad = None
            return False
    
    def preprocess_audio(self, audio_bytes: bytes) -> Tuple[torch.Tensor, int]:
        """
        Load and preprocess audio from bytes
        
        Args:
            audio_bytes: Raw audio file bytes (WAV, MP3, etc.)
        
        Returns:
            Tuple of (waveform tensor, sample_rate)
        """
        try:
            # Try fast path: load audio directly from bytes
            waveform, sample_rate = torchaudio.load(io.BytesIO(audio_bytes))
            
            # Convert stereo to mono if necessary
            if waveform.shape[0] > 1:
                waveform = torch.mean(waveform, dim=0, keepdim=True)
            
            # Resample if necessary
            if sample_rate != self.expected_sample_rate:
                logger.info(f"Resampling from {sample_rate} Hz to {self.expected_sample_rate} Hz")
                resampler = torchaudio.transforms.Resample(
                    orig_freq=sample_rate,
                    new_freq=self.expected_sample_rate
                )
                waveform = resampler(waveform)
            
            return waveform, self.expected_sample_rate
            
        except Exception as e:
            # Fallback: decode with ffmpeg from stdin -> 16kHz mono WAV bytes, then load with torchaudio
            logger.warning(f"Direct byte load failed ({e}); falling back to ffmpeg decode")
            try:
                # Resolve ffmpeg binary: prefer imageio-ffmpeg bundled exe, fall back to system PATH
                try:
                    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
                except Exception:
                    ffmpeg_exe = shutil.which("ffmpeg") or "ffmpeg"

                ffmpeg_cmd = [
                    ffmpeg_exe,
                    "-hide_banner",
                    "-loglevel", "error",
                    "-nostdin",
                    "-i", "pipe:0",           # read input from stdin
                    "-f", "wav",               # output format WAV
                    "-acodec", "pcm_s16le",    # 16-bit PCM for easy parsing
                    "-ac", "1",                # mono
                    "-ar", str(self.expected_sample_rate),  # 16kHz
                    "pipe:1"                    # write output to stdout
                ]
                proc = subprocess.run(
                    ffmpeg_cmd,
                    input=audio_bytes,
                    capture_output=True,
                    check=False
                )
                if proc.returncode != 0 or not proc.stdout:
                    stderr = proc.stderr.decode(errors="ignore") if proc.stderr else ""
                    raise RuntimeError(f"ffmpeg decode failed (code {proc.returncode}): {stderr}")

                # Parse WAV bytes using Python stdlib to avoid backend issues
                with wave.open(io.BytesIO(proc.stdout), "rb") as wf:
                    n_channels = wf.getnchannels()
                    sample_rate = wf.getframerate()
                    sampwidth = wf.getsampwidth()
                    n_frames = wf.getnframes()
                    raw = wf.readframes(n_frames)

                if sampwidth != 2:
                    raise RuntimeError(f"Unexpected WAV sample width {sampwidth*8} bits; expected 16-bit PCM")
                # Convert to float32 mono tensor in [-1,1]
                audio_np = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
                if n_channels > 1:
                    audio_np = audio_np.reshape(-1, n_channels).mean(axis=1)
                waveform = torch.from_numpy(audio_np).unsqueeze(0)  # (1, num_samples)

                # sample_rate should already be expected_sample_rate due to ffmpeg args
                if sample_rate != self.expected_sample_rate:
                    logger.info(
                        f"Resampling from {sample_rate} Hz to {self.expected_sample_rate} Hz after ffmpeg decode"
                    )
                    resampler = torchaudio.transforms.Resample(
                        orig_freq=sample_rate,
                        new_freq=self.expected_sample_rate
                    )
                    waveform = resampler(waveform)

                return waveform, self.expected_sample_rate

            except Exception as e2:
                logger.error(f"Error preprocessing audio (ffmpeg fallback failed): {e2}")
                raise ValueError(f"Failed to process audio file: {str(e2)}")
    
    def extract_w2v_embedding(self, waveform: torch.Tensor) -> torch.Tensor:
        """
        Extract 512-dimensional embedding using Wav2Vec2
        
        Args:
            waveform: Audio waveform tensor (1, num_samples)
        
        Returns:
            512-dimensional embedding tensor (1, 512)
        """
        with torch.no_grad():
            # Extract features from Wav2Vec2
            # Returns list of tensors, we take the last layer
            features, _ = self.w2v_model.extract_features(waveform)
            
            # Take the last layer's features and average over time dimension
            # Shape: (batch, time, features) -> (batch, features)
            embedding = features[-1].mean(dim=1)
            
            logger.info(f"Extracted embedding shape: {embedding.shape}")
            return embedding
    
    def predict_stress(self, embedding: torch.Tensor) -> Dict[str, float]:
        """
        Predict stress level from audio embedding
        
        Args:
            embedding: 512-dimensional audio embedding (1, 512)
        
        Returns:
            Dictionary with stress probabilities and classification
        """
        # Ensure embedding matches the model's expected input size
        embedding = self._match_embedding_dim(embedding)

        with torch.no_grad():
            # Get model predictions
            outputs = self.stress_model(embedding)
            
            # Convert logits to probabilities
            probs = F.softmax(outputs.logits, dim=-1)
            
            # Extract probabilities
            not_stressed_prob = float(probs[0, 0])
            stressed_prob = float(probs[0, 1])
            
            # Determine classification
            is_stressed = stressed_prob > not_stressed_prob
            confidence = max(not_stressed_prob, stressed_prob)
            
            return {
                "not_stressed_probability": not_stressed_prob,
                "stressed_probability": stressed_prob,
                "is_stressed": is_stressed,
                "confidence": confidence,
                "stress_level": self._get_stress_level(stressed_prob)
            }

    def _match_embedding_dim(self, embedding: torch.Tensor) -> torch.Tensor:
        """
        Ensure the extracted embedding matches the model's expected input dimension.
        If larger, slice; if smaller, zero-pad.
        """
        exp_dim = getattr(self, "expected_embed_dim", None) or embedding.shape[-1]
        cur_dim = embedding.shape[-1]
        if cur_dim == exp_dim:
            return embedding
        if cur_dim > exp_dim:
            logger.info(f"Adjusting embedding dim by slicing: {cur_dim} -> {exp_dim}")
            return embedding[..., :exp_dim]
        # cur_dim < exp_dim: pad zeros at the end
        logger.info(f"Adjusting embedding dim by padding: {cur_dim} -> {exp_dim}")
        pad_size = exp_dim - cur_dim
        pad = torch.zeros(embedding.shape[0], pad_size, device=embedding.device, dtype=embedding.dtype)
        return torch.cat([embedding, pad], dim=-1)
    
    def _get_stress_level(self, stress_prob: float) -> str:
        """
        Convert stress probability to human-readable level
        
        Args:
            stress_prob: Probability of being stressed (0-1)
        
        Returns:
            Stress level category
        """
        if stress_prob < 0.3:
            return "Low"
        elif stress_prob < 0.6:
            return "Moderate"
        elif stress_prob < 0.8:
            return "High"
        else:
            return "Very High"

    def _infer_model_input_dim(self) -> int:
        """
        Attempt to infer the expected input feature dimension of the stress model by
        scanning for the first nn.Linear layer and returning its in_features.
        Returns None if inference fails.
        """
        try:
            for module in self.stress_model.modules():
                if isinstance(module, nn.Linear):
                    return getattr(module, "in_features", None)
        except Exception:
            return None
        return None

    # ===============================================
    # Phase 2: Advanced Audio Analysis Methods
    # ===============================================

    def analyze_pauses(self, waveform: torch.Tensor, sample_rate: int) -> Dict[str, float]:
        """
        Detect pauses and speech activity intervals in audio.
        Primary method: WebRTC VAD-based segmentation for robust speech_intervals.
        Fallback: librosa.effects.split when VAD is unavailable.
        
        Args:
            waveform: Audio waveform tensor (1, num_samples)
            sample_rate: Sample rate of audio
            
        Returns:
            Dictionary with pause analysis metrics, including speech_intervals
        """
        try:
            # Prefer VAD-based intervals if available
            vad_intervals = self._compute_vad_intervals(waveform, sample_rate)

            if vad_intervals:
                intervals_sec = vad_intervals  # Already in seconds
                total_duration = float(waveform.shape[1] / sample_rate)
                speech_time = sum((seg[1] - seg[0]) for seg in intervals_sec)
                total_pause_time = max(0.0, total_duration - speech_time)
                # Count gaps as pauses
                pause_durations = []
                for i in range(len(intervals_sec) - 1):
                    pause_duration = intervals_sec[i + 1][0] - intervals_sec[i][1]
                    if pause_duration > 0.2:
                        pause_durations.append(pause_duration)
                significant_pause_count = len(pause_durations)
                avg_pause_duration = float(np.mean(pause_durations)) if pause_durations else 0.0

                speech_intervals = [
                    {"start": float(s), "end": float(e)} for (s, e) in intervals_sec
                ]

                return {
                    "total_pause_time": float(total_pause_time),
                    "pause_count": significant_pause_count,
                    "avg_pause_duration": avg_pause_duration,
                    "pause_frequency": float(significant_pause_count / total_duration) if total_duration > 0 else 0.0,
                    "speech_ratio": float(speech_time / total_duration) if total_duration > 0 else 0.0,
                    "speech_intervals": speech_intervals
                }

            # Fallback to librosa if VAD produced no intervals
            audio_np = waveform.squeeze().numpy()
            intervals = librosa.effects.split(audio_np, top_db=20)
            total_duration = len(audio_np) / sample_rate
            if len(intervals) == 0:
                return {
                    "total_pause_time": float(total_duration),
                    "pause_count": 0,
                    "avg_pause_duration": 0.0,
                    "pause_frequency": 0.0,
                    "speech_ratio": 0.0,
                    "speech_intervals": []
                }

            speech_time = sum((end - start) / sample_rate for start, end in intervals)
            total_pause_time = total_duration - speech_time
            pause_durations = []
            for i in range(len(intervals) - 1):
                pause_start = intervals[i][1] / sample_rate
                pause_end = intervals[i + 1][0] / sample_rate
                pause_duration = pause_end - pause_start
                if pause_duration > 0.2:
                    pause_durations.append(pause_duration)
            significant_pause_count = len(pause_durations)
            avg_pause_duration = np.mean(pause_durations) if pause_durations else 0.0

            speech_intervals = [
                {"start": float(start / sample_rate), "end": float(end / sample_rate)}
                for (start, end) in intervals
            ]

            return {
                "total_pause_time": float(total_pause_time),
                "pause_count": significant_pause_count,
                "avg_pause_duration": float(avg_pause_duration),
                "pause_frequency": float(significant_pause_count / total_duration) if total_duration > 0 else 0.0,
                "speech_ratio": float(speech_time / total_duration) if total_duration > 0 else 0.0,
                "speech_intervals": speech_intervals
            }
            
        except Exception as e:
            logger.error(f"Error analyzing pauses: {e}")
            return {
                "total_pause_time": 0.0,
                "pause_count": 0,
                "avg_pause_duration": 0.0,
                "pause_frequency": 0.0,
                "speech_ratio": 1.0,
                "speech_intervals": []
            }

    def _compute_vad_intervals(
        self,
        waveform: torch.Tensor,
        sample_rate: int,
        aggressiveness: int = 2,
        frame_ms: int = 30,
        padding_ms: int = 200,
        min_speech_ms: int = 300,
        pad_edge_ms: int = 50,
    ) -> list:
        """
        Compute speech activity intervals using WebRTC VAD.
        Returns list of (start_sec, end_sec). Empty if VAD unavailable or fails.
        """
        try:
            if self.vad is None:
                return []
            # Update aggressiveness if provided
            try:
                if aggressiveness is not None:
                    self.vad.set_mode(int(aggressiveness))
            except Exception:
                pass

            audio = waveform.squeeze().detach().cpu().numpy()
            # Ensure int16 PCM little-endian for VAD
            audio_int16 = np.clip(audio, -1.0, 1.0)
            audio_int16 = (audio_int16 * 32768).astype(np.int16)
            pcm_bytes = audio_int16.tobytes()

            # Frame sizing
            if sample_rate not in (8000, 16000, 32000, 48000):
                # VAD supports only these rates; resample to 16000 if needed
                audio_rs = librosa.resample(audio, orig_sr=sample_rate, target_sr=16000)
                sample_rate = 16000
                audio_int16 = np.clip(audio_rs, -1.0, 1.0)
                audio_int16 = (audio_int16 * 32768).astype(np.int16)
                pcm_bytes = audio_int16.tobytes()

            bytes_per_sample = 2
            frame_bytes = int(sample_rate * (frame_ms / 1000.0) * bytes_per_sample)
            total_frames = len(pcm_bytes) // frame_bytes
            if total_frames == 0:
                return []

            # Build speech mask per frame
            mask = []
            for i in range(total_frames):
                start = i * frame_bytes
                end = start + frame_bytes
                frame = pcm_bytes[start:end]
                if len(frame) < frame_bytes:
                    break
                try:
                    is_speech = self.vad.is_speech(frame, sample_rate)
                except Exception:
                    is_speech = False
                mask.append(bool(is_speech))

            if not any(mask):
                return []

            # Merge frames into segments allowing brief silences
            allow_silence = max(1, int(round(padding_ms / frame_ms)))
            min_frames = max(1, int(round(min_speech_ms / frame_ms)))
            pad_frames = max(0, int(round(pad_edge_ms / frame_ms)))

            segments = []
            in_seg = False
            seg_start = 0
            silence_run = 0
            for i, is_sp in enumerate(mask):
                if is_sp:
                    if not in_seg:
                        in_seg = True
                        seg_start = i
                    silence_run = 0
                else:
                    if in_seg:
                        silence_run += 1
                        if silence_run > allow_silence:
                            seg_end = i - silence_run + 1
                            if seg_end - seg_start >= min_frames:
                                segments.append((seg_start, seg_end))
                            in_seg = False
                            silence_run = 0
            if in_seg:
                seg_end = len(mask)
                if seg_end - seg_start >= min_frames:
                    segments.append((seg_start, seg_end))

            # Convert to seconds and pad edges
            frame_sec = frame_ms / 1000.0
            total_dur = float(len(pcm_bytes) / (bytes_per_sample * sample_rate))
            out = []
            for (fs, fe) in segments:
                start_sec = max(0.0, (fs - pad_frames) * frame_sec)
                end_sec = min(total_dur, (fe + pad_frames) * frame_sec)
                if end_sec - start_sec >= frame_sec:  # at least one frame long
                    out.append((float(start_sec), float(end_sec)))

            # Merge overlaps after padding
            if not out:
                return []
            out.sort(key=lambda x: x[0])
            merged = [out[0]]
            for s, e in out[1:]:
                last_s, last_e = merged[-1]
                if s <= last_e + 1e-6:
                    merged[-1] = (last_s, max(last_e, e))
                else:
                    merged.append((s, e))
            return merged
        except Exception as e:
            logger.error(f"VAD interval computation failed: {e}")
            return []

    def analyze_speech_rate(self, waveform: torch.Tensor, sample_rate: int, transcript: str = None) -> Dict[str, float]:
        """
        Analyze speech rate and tempo.
        
        Args:
            waveform: Audio waveform tensor
            sample_rate: Sample rate of audio
            transcript: Optional transcript for word-based analysis
            
        Returns:
            Dictionary with speech rate metrics
        """
        try:
            # Basic duration analysis
            duration = waveform.shape[1] / sample_rate
            
            # Estimate syllables using audio onset detection if no transcript
            if transcript is None:
                audio_np = waveform.squeeze().numpy()
                onset_frames = librosa.onset.onset_detect(y=audio_np, sr=sample_rate, units='time')
                estimated_syllables = len(onset_frames)
                estimated_words = max(1, estimated_syllables // 2)  # Rough estimate: 2 syllables per word
            else:
                # Use transcript for accurate word count
                words = transcript.strip().split()
                estimated_words = len([w for w in words if w.isalpha()])  # Only count actual words
            
            # Calculate speech rate metrics
            words_per_minute = (estimated_words / duration) * 60 if duration > 0 else 0
            
            # Classify speech rate
            if words_per_minute < 100:
                speech_rate_category = "slow"
            elif words_per_minute > 180:
                speech_rate_category = "fast"
            else:
                speech_rate_category = "normal"
            
            return {
                "words_per_minute": float(words_per_minute),
                "estimated_word_count": estimated_words,
                "duration_seconds": float(duration),
                "speech_rate_category": speech_rate_category
            }
            
        except Exception as e:
            logger.error(f"Error analyzing speech rate: {e}")
            duration = waveform.shape[1] / sample_rate
            return {
                "words_per_minute": 0.0,
                "estimated_word_count": 0,
                "duration_seconds": float(duration),
                "speech_rate_category": "unknown"
            }

    def analyze_pitch_variation(self, waveform: torch.Tensor, sample_rate: int) -> Dict[str, float]:
        """
        Analyze pitch variation and fundamental frequency characteristics.
        
        Args:
            waveform: Audio waveform tensor
            sample_rate: Sample rate of audio
            
        Returns:
            Dictionary with pitch analysis metrics
        """
        try:
            audio_np = waveform.squeeze().numpy()
            
            # Extract pitch using librosa
            f0, voiced_flag, voiced_probs = librosa.pyin(
                audio_np,
                fmin=librosa.note_to_hz('C2'),  # ~65 Hz
                fmax=librosa.note_to_hz('C7'),  # ~2093 Hz
                sr=sample_rate
            )
            
            # Remove unvoiced frames (NaN values)
            f0_voiced = f0[~np.isnan(f0)]
            
            if len(f0_voiced) == 0:
                return {
                    "mean_pitch": 0.0,
                    "pitch_std": 0.0,
                    "pitch_range": 0.0,
                    "pitch_jitter": 0.0,
                    "voiced_ratio": 0.0,
                    "pitch_category": "unknown"
                }
            
            # Calculate pitch statistics
            mean_pitch = float(np.mean(f0_voiced))
            pitch_std = float(np.std(f0_voiced))
            pitch_range = float(np.max(f0_voiced) - np.min(f0_voiced))
            voiced_ratio = float(len(f0_voiced) / len(f0))
            
            # Calculate pitch jitter (local pitch variation)
            if len(f0_voiced) > 1:
                pitch_diffs = np.abs(np.diff(f0_voiced))
                pitch_jitter = float(np.mean(pitch_diffs))
            else:
                pitch_jitter = 0.0
            
            # Categorize pitch variation
            if pitch_std < 10:
                pitch_category = "monotone"
            elif pitch_std > 50:
                pitch_category = "highly_variable"
            else:
                pitch_category = "normal"
            
            return {
                "mean_pitch": mean_pitch,
                "pitch_std": pitch_std,
                "pitch_range": pitch_range,
                "pitch_jitter": pitch_jitter,
                "voiced_ratio": voiced_ratio,
                "pitch_category": pitch_category
            }
            
        except Exception as e:
            logger.error(f"Error analyzing pitch variation: {e}")
            return {
                "mean_pitch": 0.0,
                "pitch_std": 0.0,
                "pitch_range": 0.0,
                "pitch_jitter": 0.0,
                "voiced_ratio": 0.0,
                "pitch_category": "unknown"
            }

    def analyze_transcript_features(self, transcript: str) -> Dict[str, any]:
        """
        Enhanced linguistic analysis with nervous phrase detection.
        
        Args:
            transcript: Speech-to-text transcript
            
        Returns:
            Dictionary with comprehensive transcript analysis metrics
        """
        try:
            if not transcript or not transcript.strip():
                return {
                    "filler_word_count": 0,
                    "filler_word_ratio": 0.0,
                    "repetition_count": 0,
                    "hedge_word_count": 0,
                    "nervous_phrase_count": 0,
                    "apology_count": 0,
                    "emergency_stress_detected": False,
                    "transcript_available": False
                }
            
            original_transcript = transcript
            transcript = transcript.lower().strip()
            words = transcript.split()
            total_words = len(words)
            
            # Enhanced filler words detection with more comprehensive patterns
            filler_words = ['uh', 'um', 'ah', 'er', 'like', 'you know', 'so', 'well', 'oh', 'hmm', 'actually', 'basically']
            hedge_words = ['i think', 'maybe', 'perhaps', 'sort of', 'kind of', 'i guess', 'probably', 'i mean']
            
            # NEW: Nervous phrases and panic indicators
            nervous_phrases = [
                'oh boy', 'oh no', 'oh god', 'oh dear', 'oh my',
                'get me off', 'get me out', 'i can\'t', 'help me',
                'this is bad', 'i\'m nervous', 'i\'m scared'
            ]
            
            # NEW: Apology and hesitation indicators (enhanced detection)
            apology_words = ['sorry', 'apologize', 'my bad', 'excuse me', 'pardon', 'i\'m sorry']
            hesitation_patterns = ['i did not prepare', 'what i should say', 'i want to say', 'let me think']
            
            # Count filler words with improved detection
            filler_count = 0
            filler_breakdown = {}
            
            # Standard filler words
            for filler in filler_words:
                if ' ' in filler:  # Multi-word fillers
                    count = transcript.count(filler)
                    filler_count += count
                    if count > 0:
                        filler_breakdown[filler] = count
                else:  # Single word fillers
                    count = words.count(filler)
                    filler_count += count
                    if count > 0:
                        filler_breakdown[filler] = count
            
            # Count hedge words as fillers
            for hedge in hedge_words:
                count = transcript.count(hedge)
                filler_count += count
                if count > 0:
                    filler_breakdown[hedge] = count
            
            # Count hesitation patterns as fillers
            for hesitation in hesitation_patterns:
                count = transcript.count(hesitation)
                filler_count += count
                if count > 0:
                    filler_breakdown[hesitation] = count
            
            # Enhanced repetition detection (count as fillers)
            repetition_count = 0
            # Detect phrase repetitions like "my name is my name is"
            words_lower = [w.lower() for w in words]
            for i in range(len(words_lower) - 2):
                # Check for 2-3 word phrase repetitions
                phrase_2 = ' '.join(words_lower[i:i+2])
                phrase_3 = ' '.join(words_lower[i:i+3])
                
                # Look for immediate repetition of 2-word phrases
                if i + 3 < len(words_lower):
                    next_phrase_2 = ' '.join(words_lower[i+2:i+4])
                    if phrase_2 == next_phrase_2:
                        repetition_count += 1
                        filler_count += 2  # Count repeated words as fillers
                        filler_breakdown[f"repeated: {phrase_2}"] = 1
                
                # Look for immediate repetition of 3-word phrases  
                if i + 5 < len(words_lower):
                    next_phrase_3 = ' '.join(words_lower[i+3:i+6])
                    if phrase_3 == next_phrase_3:
                        repetition_count += 1
                        filler_count += 3  # Count repeated words as fillers
                        filler_breakdown[f"repeated: {phrase_3}"] = 1
            
            # Also check for simple consecutive word repetitions
            for i in range(len(words) - 1):
                if words[i].lower() == words[i + 1].lower() and len(words[i]) > 2:
                    repetition_count += 1
                    filler_count += 1
                    filler_breakdown[f"repeated: {words[i].lower()}"] = filler_breakdown.get(f"repeated: {words[i].lower()}", 0) + 1
            
            # NEW: Count nervous phrases
            nervous_count = 0
            detected_nervous_phrases = []
            nervous_phrase_breakdown = {}
            for phrase in nervous_phrases:
                count = transcript.count(phrase)
                nervous_count += count
                if count > 0:
                    detected_nervous_phrases.append(phrase)
                    nervous_phrase_breakdown[phrase] = count
            
            # NEW: Count apologies (including enhanced detection)
            apology_count = 0
            for apology in apology_words:
                count = transcript.count(apology)
                apology_count += count
                if count > 0:
                    filler_breakdown[f"apology: {apology}"] = count
            
            # Calculate total hedge count for compatibility
            hedge_count = sum(filler_breakdown.get(hedge, 0) for hedge in hedge_words)
            
            # Detect repetitions (consecutive repeated words)
            repetition_count = 0
            for i in range(len(words) - 1):
                if words[i] == words[i + 1] and len(words[i]) > 2:  # Avoid counting short words
                    repetition_count += 1
            
            # Calculate ratios
            filler_ratio = filler_count / total_words if total_words > 0 else 0.0
            
            # NEW: Emergency stress detection patterns
            emergency_stress_detected = False
            stress_indicators = []
            
            # Pattern 1: High filler density (>15% in short clips)
            if filler_ratio > 0.15 and total_words < 30:
                emergency_stress_detected = True
                stress_indicators.append("high_filler_density")
            
            # Pattern 2: Nervous phrases detected
            if nervous_count > 0:
                emergency_stress_detected = True
                stress_indicators.append("nervous_phrases")
            
            # Pattern 3: Multiple apologies
            if apology_count >= 2:
                emergency_stress_detected = True
                stress_indicators.append("multiple_apologies")
                
            # Pattern 4: Extreme filler concentration (>20%)
            if filler_ratio > 0.20:
                emergency_stress_detected = True
                stress_indicators.append("extreme_fillers")
            
            return {
                "filler_word_count": filler_count,
                "filler_word_ratio": float(filler_ratio),
                "filler_breakdown": filler_breakdown,
                "repetition_count": repetition_count,
                "hedge_word_count": hedge_count,
                "nervous_phrase_count": nervous_count,
                "detected_nervous_phrases": detected_nervous_phrases,
                "nervous_phrase_breakdown": nervous_phrase_breakdown,
                "apology_count": apology_count,
                "emergency_stress_detected": emergency_stress_detected,
                "stress_indicators": stress_indicators,
                "total_words": total_words,
                "transcript_available": True,
                "transcript_text": original_transcript[:200] + "..." if len(original_transcript) > 200 else original_transcript,
                "full_transcript": original_transcript  # Add full transcript for "Show Full Text" feature
            }
            
        except Exception as e:
            logger.error(f"Error analyzing transcript: {e}")
            return {
                "filler_word_count": 0,
                "filler_word_ratio": 0.0,
                "repetition_count": 0,
                "hedge_word_count": 0,
                "nervous_phrase_count": 0,
                "apology_count": 0,
                "emergency_stress_detected": False,
                "transcript_available": False
            }

    def generate_transcript(self, waveform: torch.Tensor, sample_rate: int):
        """
        Generate speech transcript using Whisper ASR.
        
        Args:
            waveform: Audio waveform tensor
            sample_rate: Sample rate of audio
            
        Returns:
            (transcript_text, segments) where segments is a list of {start, end, text}
        """
        try:
            if self.whisper_model is None:
                logger.warning("Whisper model not available for transcription")
                return "", []
            
            # Convert to numpy and ensure correct sample rate for Whisper (16kHz)
            audio_np = waveform.squeeze().numpy()
            
            if sample_rate != 16000:
                # Resample to 16kHz for Whisper
                audio_np = librosa.resample(audio_np, orig_sr=sample_rate, target_sr=16000)
            
            # Generate transcript
            result = self.whisper_model.transcribe(audio_np)
            transcript = result.get("text", "").strip()
            segments = []
            for seg in result.get("segments", []) or []:
                try:
                    s = float(seg.get("start", 0.0))
                    e = float(seg.get("end", 0.0))
                    t = str(seg.get("text", "").strip())
                    if t:
                        segments.append({"start": s, "end": e, "text": t})
                except Exception:
                    continue
            
            logger.info(f"Generated transcript: {transcript[:100]}..." if len(transcript) > 100 else f"Generated transcript: {transcript}")
            return transcript, segments
            
        except Exception as e:
            logger.error(f"Error generating transcript: {e}")
            return "", []
    
    def analyze_audio(self, audio_bytes: bytes) -> Dict[str, any]:
        """
        Complete pipeline: process audio and return comprehensive analysis
        
        Args:
            audio_bytes: Raw audio file bytes
        
        Returns:
            Dictionary with complete analysis results including Phase 2 features
        """
        try:
            # Step 1: Preprocess audio
            logger.info("Step 1: Preprocessing audio...")
            waveform, sample_rate = self.preprocess_audio(audio_bytes)
            
            # Step 2: Extract embedding for stress analysis
            logger.info("Step 2: Extracting audio features...")
            embedding = self.extract_w2v_embedding(waveform)
            
            # Step 3: Predict stress (Phase 1)
            logger.info("Step 3: Analyzing stress levels...")
            stress_results = self.predict_stress(embedding)
            
            # Step 4: Phase 2 Advanced Audio Analysis
            logger.info("Step 4: Performing advanced audio analysis...")
            
            # Generate transcript for linguistic analysis
            transcript, asr_segments = self.generate_transcript(waveform, sample_rate)
            
            # Pause analysis
            pause_analysis = self.analyze_pauses(waveform, sample_rate)
            
            # Speech rate analysis
            speech_rate_analysis = self.analyze_speech_rate(waveform, sample_rate, transcript)
            
            # Pitch variation analysis
            pitch_analysis = self.analyze_pitch_variation(waveform, sample_rate)
            
            # Transcript features (filler words, repetitions)
            transcript_analysis = self.analyze_transcript_features(transcript)
            # Attach ASR segments for downstream timeline alignment
            if isinstance(transcript_analysis, dict):
                transcript_analysis["segments"] = asr_segments
            
            # Combine all analyses
            comprehensive_results = {
                # Phase 1: Stress Detection
                **stress_results,
                
                # Phase 2: Advanced Audio Features
                "pause_analysis": pause_analysis,
                "speech_rate_analysis": speech_rate_analysis,
                "pitch_analysis": pitch_analysis,
                "transcript_analysis": transcript_analysis,
                
                # Metadata
                "sample_rate": sample_rate,
                "duration_seconds": float(waveform.shape[1] / sample_rate),
                "analysis_version": "phase2"
            }
            
            # Calculate composite nervousness score
            nervousness_score = self._calculate_nervousness_score(
                stress_results, pause_analysis, speech_rate_analysis, 
                pitch_analysis, transcript_analysis
            )
            comprehensive_results["nervousness_score"] = nervousness_score

            # Derive a final combined stress probability/label that respects heuristics
            duration = comprehensive_results["duration_seconds"]
            model_prob = stress_results.get("stressed_probability", 0.0)
            # Weight heuristics more for short clips
            if duration <= 20:
                combined_prob = max(model_prob, 0.7 * nervousness_score + 0.3 * model_prob)
            else:
                combined_prob = 0.5 * model_prob + 0.5 * nervousness_score

            # Emergency: if transcript flagged emergency or nervousness very high, force high prob
            if transcript_analysis.get("emergency_stress_detected", False) or nervousness_score >= 0.85:
                combined_prob = max(combined_prob, 0.9)

            combined_prob = float(min(1.0, max(0.0, combined_prob)))
            combined_is_stressed = combined_prob >= 0.5
            combined_level = self._get_stress_level(combined_prob)

            # Preserve raw model outputs for transparency
            comprehensive_results["model_outputs"] = {
                "stressed_probability": model_prob,
                "not_stressed_probability": stress_results.get("not_stressed_probability", 0.0),
                "is_stressed": stress_results.get("is_stressed", False),
                "confidence": stress_results.get("confidence", model_prob if model_prob >= 0.5 else 1.0 - model_prob),
                "stress_level": stress_results.get("stress_level", self._get_stress_level(model_prob)),
            }

            # Set final verdict fields and also align top-level for UI compatibility
            comprehensive_results["final_stressed_probability"] = combined_prob
            comprehensive_results["final_is_stressed"] = combined_is_stressed
            comprehensive_results["final_stress_level"] = combined_level
            comprehensive_results["confidence"] = max(combined_prob, 1.0 - combined_prob)

            # Align legacy/top-level fields to reflect the combined verdict
            comprehensive_results["stressed_probability"] = combined_prob
            comprehensive_results["is_stressed"] = combined_is_stressed
            comprehensive_results["stress_level"] = combined_level
            
            logger.info(
                f"✓ Comprehensive analysis complete: ML={stress_results['stress_level']} ({model_prob:.2f}), "
                f"Final={combined_level} ({combined_prob:.2f}), Nervousness={nervousness_score:.2f}"
            )
            return comprehensive_results
            
        except Exception as e:
            logger.error(f"Error during comprehensive audio analysis: {e}")
            raise

    def _calculate_nervousness_score(self, stress_results: Dict, pause_analysis: Dict, 
                                   speech_rate_analysis: Dict, pitch_analysis: Dict, 
                                   transcript_analysis: Dict) -> float:
        """
        Calculate a composite nervousness score with Phase 2.5 heuristic boost.
        Enhanced algorithm with rule-based overrides for extreme stress indicators.
        
        Returns:
            Float between 0.0 (calm) and 1.0 (very nervous)
        """
        try:
            # Base weighted scoring
            score = 0.0
            
            # Extract key metrics
            pause_frequency = pause_analysis.get("pause_frequency", 0.0)
            wpm = speech_rate_analysis.get("words_per_minute", 120)
            pitch_category = pitch_analysis.get("pitch_category", "normal")
            pitch_range = pitch_analysis.get("pitch_range", 0)  # Fixed key name
            filler_ratio = transcript_analysis.get("filler_word_ratio", 0.0)
            total_words = transcript_analysis.get("total_words", 0)
            audio_duration = speech_rate_analysis.get("duration_seconds", 30.0)  # Fixed to get from speech_rate_analysis
            
            # NEW: Phase 2.6 Emergency Stress Detection
            emergency_stress = transcript_analysis.get("emergency_stress_detected", False)
            nervous_phrases = transcript_analysis.get("nervous_phrase_count", 0)
            apology_count = transcript_analysis.get("apology_count", 0)
            
            # EMERGENCY OVERRIDE: Detect obvious stress patterns that ML model misses
            emergency_override = False
            override_reason = []
            
            # Emergency Pattern 1: "Get me off" type panic phrases
            if nervous_phrases > 0:
                emergency_override = True
                override_reason.append("panic_phrases")
            
            # Emergency Pattern 2: Multiple stress indicators in short audio
            if audio_duration <= 25:  # Short clips
                stress_count = 0
                if pause_frequency >= 0.7: stress_count += 1
                if wpm <= 60: stress_count += 1
                if filler_ratio >= 0.12: stress_count += 1
                if pitch_category == "highly_variable" or "very variable" in pitch_category.lower(): stress_count += 1
                if apology_count >= 1: stress_count += 1
                
                if stress_count >= 3:
                    emergency_override = True
                    override_reason.append("multiple_indicators")
            
            # Emergency Pattern 3: Extreme filler density
            if filler_ratio >= 0.25:  # 25%+ fillers
                emergency_override = True
                override_reason.append("extreme_fillers")
                
            # Emergency Pattern 4: Very high pause frequency
            if pause_frequency >= 1.0:  # 1+ pauses per second
                emergency_override = True
                override_reason.append("extreme_pauses")
            
            # If emergency stress detected, override with high score
            if emergency_override:
                emergency_score = 0.85 + min(0.15, len(override_reason) * 0.05)
                logger.warning(f"EMERGENCY STRESS OVERRIDE ACTIVATED - Score: {emergency_score:.3f}, "
                             f"Reasons: {override_reason}, Original ML score would be: "
                             f"{stress_results.get('stressed_probability', 0.0):.3f}")
                return float(emergency_score)
            
            # Stress component (35% weight - reduced to make room for heuristics)
            stress_weight = 0.35
            score += stress_results.get("stressed_probability", 0.0) * stress_weight
            
            # Enhanced pause component (25% weight - increased)
            pause_weight = 0.25
            if pause_frequency > 0.8:  # More than 0.8 pauses per second
                pause_score = 1.0
            elif pause_frequency > 0.5:
                pause_score = 0.7 + (pause_frequency - 0.5) * 1.0  # 0.5-0.8 -> 0.7-1.0
            else:
                pause_score = min(1.0, pause_frequency * 1.4)  # More aggressive scaling
            score += pause_score * pause_weight
            
            # Enhanced speech rate component (20% weight - increased)
            speech_weight = 0.20
            if wpm > 180:
                speech_score = min(1.0, (wpm - 180) / 60)
            elif wpm < 60:  # Lowered threshold for very slow speech
                speech_score = min(1.0, (60 - wpm) / 30)  # More aggressive for very slow
            elif wpm < 80:
                speech_score = (80 - wpm) / 40  # Gradual increase for slow speech
            else:
                speech_score = 0.0
            score += speech_score * speech_weight
            
            # Enhanced pitch variation component (15% weight)
            pitch_weight = 0.15
            if pitch_category == "highly_variable" or pitch_range > 800:
                pitch_score = 0.9
            elif pitch_category == "monotone":
                pitch_score = 0.4
            else:
                pitch_score = 0.1
            score += pitch_score * pitch_weight
            
            # Filler words component (5% weight - reduced but more aggressive)
            filler_weight = 0.05
            if filler_ratio > 0.15:  # More than 15% fillers
                filler_score = 1.0
            elif filler_ratio > 0.08:  # More than 8% fillers
                filler_score = 0.6 + (filler_ratio - 0.08) * 5.7  # Scale to 1.0
            else:
                filler_score = min(1.0, filler_ratio * 7.5)  # More aggressive scaling
            score += filler_score * filler_weight
            
            # PHASE 2.5 HEURISTIC BOOST - Rule-based overrides for extreme cases
            heuristic_boost = 0.0
            
            # Short audio with high stress concentration
            if audio_duration <= 20:  # Short clips need special handling
                concentration_factor = 1.0
                
                # High pause density boost
                if pause_frequency >= 0.8:
                    concentration_factor += 0.3
                    
                # Very slow speech boost  
                if wpm <= 50:
                    concentration_factor += 0.25
                    
                # High filler density boost
                if filler_ratio >= 0.12:
                    concentration_factor += 0.2
                    
                # Extreme pitch variation boost
                if pitch_range > 1000:
                    concentration_factor += 0.15
                    
                # Apply concentration multiplier to short clips
                if concentration_factor > 1.2:
                    heuristic_boost = min(0.3, (concentration_factor - 1.0) * 0.5)
            
            # Multi-indicator stress pattern detection
            stress_indicators = 0
            if pause_frequency > 0.6: stress_indicators += 1
            if wpm < 70: stress_indicators += 1  
            if filler_ratio > 0.08: stress_indicators += 1
            if pitch_category == "highly_variable": stress_indicators += 1
            
            # Boost for multiple simultaneous stress indicators
            if stress_indicators >= 3:
                heuristic_boost += 0.2
            elif stress_indicators >= 2:
                heuristic_boost += 0.1
                
            # Apply heuristic boost
            final_score = score + heuristic_boost
            
            # Ensure score boundaries
            final_score = min(1.0, max(0.0, final_score))
            
            logger.info(f"Nervousness Scoring - Base: {score:.3f}, Boost: {heuristic_boost:.3f}, "
                       f"Final: {final_score:.3f} | Indicators: pauses={pause_frequency:.2f}/s, "
                       f"wpm={wpm}, filler={filler_ratio:.2%}, pitch={pitch_category}")
                       
            return float(final_score)
            
        except Exception as e:
            logger.error(f"Error calculating nervousness score: {e}")
            return 0.5  # Default moderate score


# Singleton instance to avoid reloading models on every request
_analyzer_instance = None

def get_voice_analyzer() -> VoiceStressAnalyzer:
    """
    Get or create singleton instance of VoiceStressAnalyzer
    This ensures models are loaded only once
    """
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = VoiceStressAnalyzer()
    return _analyzer_instance
