"""Lightweight AI-generated text detection with optional ML perplexity.

This module provides a best-effort detector:
- If transformers+torch are available, uses a small causal LM (distilgpt2) to
  compute perplexity, then maps that to an AI-likelihood.
- Always computes heuristic features (contractions, sentence length variance,
  punctuation diversity) to refine the score or to use as fallback when ML is
  unavailable (common on Windows without torch).

Caveat: AI text detection is inherently unreliable. Treat results as a
probabilistic signal, not definitive proof.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Dict, Optional

ML_AVAILABLE = True
try:
    import torch  # type: ignore
    from transformers import AutoTokenizer, AutoModelForCausalLM  # type: ignore
except Exception:  # pragma: no cover - environment-dependent
    ML_AVAILABLE = False
    AutoTokenizer = None  # type: ignore
    AutoModelForCausalLM = None  # type: ignore
    torch = None  # type: ignore


_CONTRACTION_RE = re.compile(r"\b(\w+)'(re|m|s|ve|d|ll|t)\b", re.IGNORECASE)
_SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
_WORD_RE = re.compile(r"\b\w+\b", re.UNICODE)
_PUNCT_RE = re.compile(r"[\,\.;:!\?\-\(\)\[\]\{\}\"'`/]", re.UNICODE)


@dataclass
class DetectResult:
    ai_probability: float
    confidence: float
    method: str
    features: Dict[str, Any]
    explanation: str


class AITextDetector:
    def __init__(self, model_id: str = "distilgpt2") -> None:
        self.model_id = model_id
        self._tokenizer = None
        self._model = None
        self._ml_ready = False
        if ML_AVAILABLE:
            try:
                self._tokenizer = AutoTokenizer.from_pretrained(model_id)
                self._model = AutoModelForCausalLM.from_pretrained(model_id)
                self._model.eval()
                self._ml_ready = True
            except Exception:
                # Model load failed (e.g., no internet or missing torch); fallback to heuristics
                self._tokenizer = None
                self._model = None
                self._ml_ready = False

    # ---------------------------- Heuristics ----------------------------
    def _compute_heuristics(self, text: str) -> Dict[str, Any]:
        text = text.strip()
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
        words = _WORD_RE.findall(text)
        punct = _PUNCT_RE.findall(text)

        n_sent = len(sentences)
        n_words = len(words)
        n_punct = len(punct)

        sent_lengths = [len(_WORD_RE.findall(s)) for s in sentences] or [0]
        avg_sent_len = (sum(sent_lengths) / max(1, len(sent_lengths)))
        std_sent_len = (sum((l - avg_sent_len) ** 2 for l in sent_lengths) / max(1, len(sent_lengths))) ** 0.5

        contractions = _CONTRACTION_RE.findall(text)
        contraction_ratio = len(contractions) / max(1, n_words)

        punct_types = set(punct)
        punct_diversity = len(punct_types)

        unique_words = len(set(w.lower() for w in words))
        type_token_ratio = unique_words / max(1, n_words)

        return {
            "n_sentences": n_sent,
            "n_words": n_words,
            "avg_sentence_len": avg_sent_len,
            "std_sentence_len": std_sent_len,
            "contraction_ratio": contraction_ratio,
            "punctuation_diversity": punct_diversity,
            "type_token_ratio": type_token_ratio,
        }

    def _heuristics_ai_score(self, feats: Dict[str, Any]) -> float:
        # Start from neutral 0.5 and adjust with small weights.
        score = 0.5
        # Very low contractions -> slightly more AI-like
        cr = feats.get("contraction_ratio", 0.0)
        if cr < 0.01:
            score += 0.12
        elif cr < 0.03:
            score += 0.07
        # Low sentence length variance with relatively long sentences -> AI-like
        std_len = feats.get("std_sentence_len", 0.0)
        avg_len = feats.get("avg_sentence_len", 0.0)
        if avg_len >= 14 and std_len <= 4:
            score += 0.12
        elif avg_len >= 12 and std_len <= 3:
            score += 0.07
        # Low punctuation diversity -> AI-like
        pdiv = feats.get("punctuation_diversity", 0)
        if pdiv <= 1:
            score += 0.05
        elif pdiv <= 2:
            score += 0.03
        # Extremely high type-token ratio could be AI-like (overly varied), but weak signal
        ttr = feats.get("type_token_ratio", 0.0)
        if ttr >= 0.6:
            score += 0.03
        # Clamp to [0.05, 0.95]
        return max(0.05, min(0.95, score))

    # ------------------------------ ML ---------------------------------
    def _perplexity(self, text: str) -> Optional[float]:
        if not self._ml_ready or not self._tokenizer or not self._model:
            return None
        try:
            enc = self._tokenizer(text, return_tensors="pt")
            if enc.input_ids.shape[-1] < 4:
                return None
            with torch.no_grad():
                out = self._model(**enc, labels=enc.input_ids)
                loss = float(out.loss.detach().cpu().item())
            ppl = math.exp(loss)
            return float(ppl)
        except Exception:
            return None

    def _map_ppl_to_ai_prob(self, ppl: float) -> float:
        # Piecewise mapping based on rough empirical ranges
        if ppl <= 25:
            return 0.9
        if ppl <= 45:
            # 25->0.9 down to 45->0.4
            return 0.9 - (ppl - 25) * (0.5 / 20)
        if ppl <= 80:
            # 45->0.4 down to 80->0.1
            return 0.4 - (ppl - 45) * (0.3 / 35)
        return 0.05

    # ------------------------------ API --------------------------------
    def detect(self, text: str) -> DetectResult:
        text = (text or "").strip()
        if not text:
            return DetectResult(
                ai_probability=0.0,
                confidence=0.1,
                method="empty",
                features={},
                explanation="No text provided."
            )

        feats = self._compute_heuristics(text)
        n_words = feats["n_words"]

        ml_ppl = self._perplexity(text)
        if ml_ppl is not None:
            ai_prob_ml = self._map_ppl_to_ai_prob(ml_ppl)
            # Blend with heuristics lightly (80% ML, 20% heur)
            ai_prob_heur = self._heuristics_ai_score(feats)
            ai_prob = 0.8 * ai_prob_ml + 0.2 * ai_prob_heur
            # Confidence increases with text length and ML availability
            conf = max(0.2, min(0.95, 0.6 + (min(n_words, 300) / 300) * 0.35))
            expl = (
                f"Perplexity={ml_ppl:.1f}. Lower perplexity suggests more AI-like text. "
                f"Heuristics adjusted the score based on contractions, sentence variability, and punctuation diversity."
            )
            method = "ml_perplexity+heuristics"
        else:
            ai_prob = self._heuristics_ai_score(feats)
            conf = max(0.15, min(0.6, 0.25 + (min(n_words, 200) / 200) * 0.3))
            expl = (
                "ML model unavailable; using heuristic signals (contractions, sentence variability, punctuation diversity). "
                "Result is less reliable."
            )
            method = "heuristics_only"

        return DetectResult(
            ai_probability=float(round(ai_prob, 4)),
            confidence=float(round(conf, 4)),
            method=method,
            features={**feats, **({"perplexity": ml_ppl} if ml_ppl is not None else {})},
            explanation=expl,
        )


_detector: Optional[AITextDetector] = None


@lru_cache(maxsize=1)
def get_ai_text_detector() -> AITextDetector:
    global _detector
    if _detector is None:
        _detector = AITextDetector()
    return _detector
