"""
Test suite for Cheating Detection System.

Tests:
- AI text detection
- Gaze tracking
- Multi-speaker detection
- Timing analysis
- Complete workflow
"""

import pytest
import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.cheating_detector.detector import cheating_detector
from services.cheating_detector.perplexity_checker import perplexity_checker
from services.cheating_detector.video_analyzer import video_analyzer
from services.cheating_detector.audio_fingerprint import audio_fingerprinter
from services.cheating_detector.timing_analyzer import timing_analyzer
from interview_agents.cheating_detector_agent import CheatingDetectorAgent

import logging
logging.basicConfig(level=logging.INFO)

# ═══════════════════════════════════════════════════════════════
# TEST DATA
# ═══════════════════════════════════════════════════════════════

# AI-generated text (ChatGPT-like)
AI_GENERATED_TEXT = """
Machine learning is a subset of artificial intelligence that enables systems to learn 
and improve from experience without being explicitly programmed. It focuses on the 
development of computer programs that can access data and use it to learn for themselves. 
The process of learning begins with observations or data, such as examples, direct 
experience, or instruction, in order to look for patterns in data and make better 
decisions in the future based on the examples that we provide.
"""

# Human-written text (natural, with errors)
HUMAN_WRITTEN_TEXT = """
So basically, machine learning is like when computers learn stuff on their own, you know? 
They look at a bunch of data and kinda figure out patterns. Like, you dont even have to 
tell them exactly what to do - they just learn from examples. Its pretty cool actually, 
because the more data they see, the better they get at making predictions and stuff. 
I think its gonna be huge for the future.
"""

# ═══════════════════════════════════════════════════════════════
# UNIT TESTS
# ═══════════════════════════════════════════════════════════════

def test_perplexity_checker_ai_text():
    """Test AI text detection with ChatGPT-like text."""
    print("\n" + "="*60)
    print("TEST: AI Text Detection - GPT-generated Text")
    print("="*60)
    
    result = perplexity_checker.check_text(AI_GENERATED_TEXT)
    
    print(f"\nResults:")
    print(f"  AI Probability: {result['ai_probability']*100:.1f}%")
    print(f"  Perplexity: {result['perplexity']:.2f}")
    print(f"  Uniformity: {result['uniformity']*100:.1f}%")
    print(f"  Formality: {result['formality']*100:.1f}%")
    print(f"  Is Likely AI: {result['is_likely_ai']}")
    
    assert result['is_likely_ai'] == True, "Should detect AI-generated text"
    assert result['perplexity'] < 50, "AI text should have low perplexity"
    
    print("\n✅ TEST PASSED: AI text correctly detected")


def test_perplexity_checker_human_text():
    """Test AI text detection with human-written text."""
    print("\n" + "="*60)
    print("TEST: AI Text Detection - Human-written Text")
    print("="*60)
    
    result = perplexity_checker.check_text(HUMAN_WRITTEN_TEXT)
    
    print(f"\nResults:")
    print(f"  AI Probability: {result['ai_probability']*100:.1f}%")
    print(f"  Perplexity: {result['perplexity']:.2f}")
    print(f"  Uniformity: {result['uniformity']*100:.1f}%")
    print(f"  Formality: {result['formality']*100:.1f}%")
    print(f"  Is Likely AI: {result['is_likely_ai']}")
    
    assert result['is_likely_ai'] == False, "Should NOT detect human text as AI"
    assert result['perplexity'] > 30, "Human text should have higher perplexity"
    
    print("\n✅ TEST PASSED: Human text correctly identified")


def test_video_analyzer_mock():
    """Test video analyzer with mock data (no video file needed)."""
    print("\n" + "="*60)
    print("TEST: Video Analyzer - Mock Gaze Data")
    print("="*60)
    
    # This will fail gracefully if no video, but tests the interface
    result = video_analyzer.analyze_gaze_behavior("nonexistent_video.mp4")
    
    print(f"\nResults:")
    print(f"  Camera Focus Ratio: {result['camera_focus_ratio']*100:.1f}%")
    print(f"  Reading Pattern: {result['reading_pattern_detected']}")
    print(f"  Erratic Gaze: {result['erratic_gaze']}")
    print(f"  Frames Analyzed: {result['total_frames_analyzed']}")
    
    # Should return default values gracefully
    assert 'camera_focus_ratio' in result
    assert 'reading_pattern_detected' in result
    
    print("\n✅ TEST PASSED: Video analyzer handles missing video gracefully")


def test_timing_analyzer_mock():
    """Test timing analyzer with mock data."""
    print("\n" + "="*60)
    print("TEST: Timing Analyzer - Mock Audio Data")
    print("="*60)
    
    result = timing_analyzer.analyze_pauses("nonexistent_audio.wav")
    
    print(f"\nResults:")
    print(f"  Typing Pattern: {result['typing_pattern_detected']}")
    print(f"  Too Fluent: {result['too_fluent']}")
    print(f"  Pause Ratio: {result['pause_ratio']*100:.1f}%")
    print(f"  Num Pauses: {result['num_pauses']}")
    
    assert 'typing_pattern_detected' in result
    
    print("\n✅ TEST PASSED: Timing analyzer handles missing audio gracefully")


def test_complete_cheating_detector():
    """Test complete cheating detection workflow."""
    print("\n" + "="*60)
    print("TEST: Complete Cheating Detection Workflow")
    print("="*60)
    
    # Test with AI-generated text (no video/audio)
    result = cheating_detector.analyze_interview(
        transcript=AI_GENERATED_TEXT,
        video_path=None,
        audio_path=None,
        candidate_baseline=None
    )
    
    print(f"\nResults:")
    print(f"  Cheating Score: {result['cheating_score']*100:.1f}%")
    print(f"  Is Likely Cheating: {result['is_likely_cheating']}")
    print(f"  Confidence: {result['confidence']*100:.1f}%")
    print(f"  Indicators Detected: {result['num_indicators']}")
    print(f"\n  Summary: {result['summary']}")
    
    print(f"\n  Indicators:")
    for indicator in result['indicators']:
        print(f"    - {indicator['type']}: {indicator['evidence'][:80]}...")
    
    assert result['cheating_score'] > 0, "Should detect cheating indicators"
    assert 'indicators' in result
    assert 'summary' in result
    
    print("\n✅ TEST PASSED: Complete workflow executed successfully")


@pytest.mark.asyncio
async def test_cheating_detector_agent():
    """Test Cheating Detector Agent with LLM reasoning."""
    print("\n" + "="*60)
    print("TEST: Cheating Detector Agent (LLM-based)")
    print("="*60)
    
    agent = CheatingDetectorAgent()
    
    result = await agent.analyze_interview_security(
        transcript=AI_GENERATED_TEXT,
        video_path=None,
        audio_path=None,
        candidate_baseline=None
    )
    
    print(f"\nResults:")
    print(f"  Risk Level: {result['risk_level']}")
    print(f"  Cheating Score: {result['cheating_score']*100:.1f}%")
    print(f"\n  Agent Interpretation:")
    print(f"    {result['agent_interpretation'][:200]}...")
    print(f"\n  Recommendation: {result['recommendation']}")
    
    assert 'risk_level' in result
    assert 'agent_interpretation' in result
    
    print("\n✅ TEST PASSED: Agent analysis completed")


# ═══════════════════════════════════════════════════════════════
# INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════

def test_vocabulary_consistency():
    """Test vocabulary consistency detection."""
    print("\n" + "="*60)
    print("TEST: Vocabulary Consistency Detection")
    print("="*60)
    
    # Baseline (simple vocabulary)
    baseline = {
        'vocabulary': ['machine', 'learning', 'data', 'computer', 'program', 'simple']
    }
    
    # Answer with sophisticated vocabulary not in baseline
    sophisticated_answer = """
    Machine learning algorithms leverage stochastic gradient descent to optimize 
    objective functions, facilitating convergence towards local minima within 
    high-dimensional parameter spaces.
    """
    
    result = cheating_detector.analyze_interview(
        transcript=sophisticated_answer,
        video_path=None,
        audio_path=None,
        candidate_baseline=baseline
    )
    
    print(f"\nResults:")
    print(f"  Vocabulary indicators: {[i for i in result['indicators'] if i['type'] == 'vocabulary']}")
    
    # Should flag vocabulary mismatch
    vocab_indicators = [i for i in result['indicators'] if i['type'] == 'vocabulary']
    assert len(vocab_indicators) > 0, "Should detect vocabulary inconsistency"
    
    print("\n✅ TEST PASSED: Vocabulary inconsistency detected")


# ═══════════════════════════════════════════════════════════════
# MAIN TEST RUNNER
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "="*60)
    print("CHEATING DETECTION SYSTEM - TEST SUITE")
    print("="*60)
    
    # Run unit tests
    test_perplexity_checker_ai_text()
    test_perplexity_checker_human_text()
    test_video_analyzer_mock()
    test_timing_analyzer_mock()
    test_complete_cheating_detector()
    test_vocabulary_consistency()
    
    # Run async test
    print("\n" + "="*60)
    print("Running Async Agent Test...")
    print("="*60)
    asyncio.run(test_cheating_detector_agent())
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)