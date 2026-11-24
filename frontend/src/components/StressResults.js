import React, { useState } from 'react';
import './StressResults.css';

const StressResults = ({ results }) => {
  // Handle both Phase 1 and Phase 2 results
  const isPhase2 = results.analysis_version === 'phase2';
  
  // State for transcript toggle
  const [showFullTranscript, setShowFullTranscript] = useState(false);
  const [showFillerDetails, setShowFillerDetails] = useState(false);
  
  const {
    stressed_probability,
    not_stressed_probability,
    is_stressed,
    confidence,
    stress_level,
    duration_seconds,
    nervousness_score,
    pause_analysis,
    speech_rate_analysis,
    pitch_analysis,
    transcript_analysis
  } = results;

  // Convert to percentages
  const stressedPercent = (stressed_probability * 100).toFixed(1);
  const notStressedPercent = (not_stressed_probability * 100).toFixed(1);
  const confidencePercent = (confidence * 100).toFixed(1);
  const nervousnessPercent = isPhase2 ? (nervousness_score * 100).toFixed(1) : null;

  // Determine color based on stress level
  const getStressColor = () => {
    switch (stress_level) {
      case 'Low':
        return '#48bb78';
      case 'Moderate':
        return '#ed8936';
      case 'High':
        return '#f56565';
      case 'Very High':
        return '#c53030';
      default:
        return '#667eea';
    }
  };

  // Get emoji based on stress level
  const getStressEmoji = () => {
    switch (stress_level) {
      case 'Low':
        return '😊';
      case 'Moderate':
        return '😐';
      case 'High':
        return '😰';
      case 'Very High':
        return '😫';
      default:
        return '🤔';
    }
  };

  // Get feedback message with Phase 2 insights
  const getFeedback = () => {
    let feedback = '';
    switch (stress_level) {
      case 'Low':
        feedback = 'Great job! You sound calm and confident.';
        break;
      case 'Moderate':
        feedback = 'You\'re doing well, but there\'s some tension detected.';
        break;
      case 'High':
        feedback = 'Noticeable stress detected. Consider practicing relaxation techniques.';
        break;
      case 'Very High':
        feedback = 'High stress levels detected. Take time to relax and practice.';
        break;
      default:
        feedback = 'Analysis complete.';
    }

    // Add Phase 2 specific insights
    if (isPhase2) {
      const insights = [];
      
      if (speech_rate_analysis?.speech_rate_category === 'fast') {
        insights.push('Try speaking a bit slower');
      } else if (speech_rate_analysis?.speech_rate_category === 'slow') {
        insights.push('You can speak with more energy');
      }
      
      if (pause_analysis?.pause_frequency > 0.5) {
        insights.push('Reduce long pauses between words');
      }
      
      if (transcript_analysis?.filler_word_ratio > 0.15) {
        insights.push('Minimize filler words like "um" and "uh"');
      }
      
      if (pitch_analysis?.pitch_category === 'monotone') {
        insights.push('Add more vocal variety and expression');
      }
      
      if (insights.length > 0) {
        feedback += ' ' + insights.join(', ') + '.';
      }
    }

    return feedback;
  };

  // Get speech rate indicator
  const getSpeechRateIndicator = (category) => {
    switch (category) {
      case 'slow': return { emoji: '🐌', label: 'Slow', color: '#ed8936' };
      case 'fast': return { emoji: '⚡', label: 'Fast', color: '#f56565' };
      case 'normal': return { emoji: '✅', label: 'Normal', color: '#48bb78' };
      default: return { emoji: '❓', label: 'Unknown', color: '#667eea' };
    }
  };

  // Get pitch indicator  
  const getPitchIndicator = (category) => {
    switch (category) {
      case 'monotone': return { emoji: '📏', label: 'Monotone', color: '#ed8936' };
      case 'highly_variable': return { emoji: '🎢', label: 'Very Variable', color: '#f56565' };
      case 'normal': return { emoji: '🎵', label: 'Natural', color: '#48bb78' };
      default: return { emoji: '❓', label: 'Unknown', color: '#667eea' };
    }
  };

  // Analyze filler words from transcript (prefer backend breakdown)
  const getFillerWordBreakdown = () => {
    if (!isPhase2 || !transcript_analysis?.transcript_available) {
      return [];
    }

    // Prefer server-provided breakdown (includes apologies/hesitations/repetitions)
    if (transcript_analysis.filler_breakdown && Object.keys(transcript_analysis.filler_breakdown).length > 0) {
      return Object.entries(transcript_analysis.filler_breakdown)
        .map(([word, count]) => ({
          word,
          count,
          percentage: ((count / (transcript_analysis.total_words || 1)) * 100).toFixed(1)
        }))
        .sort((a, b) => b.count - a.count);
    }

    // Fallback: compute a simple local breakdown from preview text
    if (!transcript_analysis?.transcript_text) return [];
    const transcript = transcript_analysis.transcript_text.toLowerCase();
    const fillerWords = {
      'uh': 0,
      'um': 0,
      'ah': 0,
      'er': 0,
      'like': 0,
      'you know': 0,
      'so': 0,
      'well': 0,
      'oh': 0
    };

    Object.keys(fillerWords).forEach(filler => {
      if (filler.includes(' ')) {
        fillerWords[filler] = (transcript.match(new RegExp(filler, 'g')) || []).length;
      } else {
        const regex = new RegExp(`\\b${filler}\\b`, 'g');
        fillerWords[filler] = (transcript.match(regex) || []).length;
      }
    });

    return Object.entries(fillerWords)
      .filter(([_, count]) => count > 0)
      .map(([word, count]) => ({
        word,
        count,
        percentage: ((count / (transcript_analysis.total_words || 1)) * 100).toFixed(1)
      }))
      .sort((a, b) => b.count - a.count);
  };

  const fillerBreakdown = getFillerWordBreakdown();

  return (
    <div className="stress-results">
      <div className="results-header">
        <h2>📊 Voice Analysis Results {isPhase2 && <span className="phase-badge">Phase 2</span>}</h2>
      </div>

      {/* Main Stress Indicator */}
      <div className="stress-indicator" style={{ borderColor: getStressColor() }}>
        <div className="stress-emoji">{getStressEmoji()}</div>
        <div className="stress-classification">
          <h3>{is_stressed ? 'Stressed' : 'Not Stressed'}</h3>
          <p className="stress-level" style={{ color: getStressColor() }}>
            {stress_level} Stress Level
          </p>
        </div>
        <div className="confidence-badge">
          <span>{confidencePercent}%</span>
          <small>Confidence</small>
        </div>
      </div>

      {/* Phase 2: Nervousness Score */}
      {isPhase2 && (
        <div className="nervousness-section">
          <h4>🎯 Overall Nervousness Score</h4>
          <div className="nervousness-bar-container">
            <div className="nervousness-bar">
              <div 
                className="nervousness-fill"
                style={{ 
                  width: `${nervousnessPercent}%`,
                  backgroundColor: nervousness_score > 0.7 ? '#f56565' : nervousness_score > 0.4 ? '#ed8936' : '#48bb78'
                }}
              ></div>
            </div>
            <span className="nervousness-score">{nervousnessPercent}%</span>
          </div>
        </div>
      )}

      {/* Probability Bars */}
      <div className="probability-section">
        <div className="probability-item">
          <div className="probability-label">
            <span>😊 Not Stressed</span>
            <strong>{notStressedPercent}%</strong>
          </div>
          <div className="probability-bar">
            <div 
              className="probability-fill green"
              style={{ width: `${notStressedPercent}%` }}
            ></div>
          </div>
        </div>

        <div className="probability-item">
          <div className="probability-label">
            <span>😰 Stressed</span>
            <strong>{stressedPercent}%</strong>
          </div>
          <div className="probability-bar">
            <div 
              className="probability-fill red"
              style={{ width: `${stressedPercent}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Phase 2: Detailed Analysis */}
      {isPhase2 && (
        <div className="detailed-analysis">
          <h4>🔍 Detailed Analysis</h4>
          
          <div className="analysis-grid">
            {/* Speech Rate */}
            <div className="analysis-card">
              <div className="analysis-header">
                <span className="analysis-icon">🗣️</span>
                <h5>Speech Rate</h5>
              </div>
              <div className="analysis-value">
                <span className="indicator" style={{ color: getSpeechRateIndicator(speech_rate_analysis?.speech_rate_category).color }}>
                  {getSpeechRateIndicator(speech_rate_analysis?.speech_rate_category).emoji} {getSpeechRateIndicator(speech_rate_analysis?.speech_rate_category).label}
                </span>
                <small>{speech_rate_analysis?.words_per_minute?.toFixed(0)} WPM</small>
              </div>
            </div>

            {/* Pauses */}
            <div className="analysis-card">
              <div className="analysis-header">
                <span className="analysis-icon">⏸️</span>
                <h5>Pauses</h5>
              </div>
              <div className="analysis-value">
                <span className="number">{pause_analysis?.pause_count || 0}</span>
                <small>Significant pauses</small>
              </div>
            </div>

            {/* Pitch Variation */}
            <div className="analysis-card">
              <div className="analysis-header">
                <span className="analysis-icon">🎵</span>
                <h5>Pitch</h5>
              </div>
              <div className="analysis-value">
                <span className="indicator" style={{ color: getPitchIndicator(pitch_analysis?.pitch_category).color }}>
                  {getPitchIndicator(pitch_analysis?.pitch_category).emoji} {getPitchIndicator(pitch_analysis?.pitch_category).label}
                </span>
                <small>{pitch_analysis?.mean_pitch?.toFixed(0)} Hz avg</small>
              </div>
            </div>

            {/* Filler Words */}
            {transcript_analysis?.transcript_available && (
              <div className="analysis-card">
                <div className="analysis-header">
                  <span className="analysis-icon">💭</span>
                  <h5>Filler Words</h5>
                </div>
                <div className="analysis-value">
                  <span className="number">{transcript_analysis.filler_word_count}</span>
                  <small>{(transcript_analysis.filler_word_ratio * 100).toFixed(1)}% of speech</small>
                  {fillerBreakdown.length > 0 && (
                    <button 
                      className="details-toggle"
                      onClick={() => setShowFillerDetails(!showFillerDetails)}
                    >
                      {showFillerDetails ? 'Hide Details' : 'Show Details'}
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Filler Words Breakdown */}
          {showFillerDetails && fillerBreakdown.length > 0 && (
            <div className="filler-breakdown">
              <h5>🔍 Filler Words Breakdown</h5>
              <div className="filler-grid">
                {fillerBreakdown.map(({ word, count, percentage }) => (
                  <div key={word} className="filler-item">
                    <div className="filler-word">"{word}"</div>
                    <div className="filler-stats">
                      <span className="filler-count">{count}</span>
                      <span className="filler-percentage">{percentage}%</span>
                    </div>
                  </div>
                ))}
              </div>
              <div className="filler-summary">
                <small>
                  💡 Tip: Aim for less than 5% filler words for professional speech
                </small>
              </div>
            </div>
          )}

          {/* Transcript Preview */}
          {transcript_analysis?.transcript_available && transcript_analysis?.transcript_text && (
            <div className="transcript-section">
              <div className="transcript-header">
                <h5>📝 Transcript</h5>
                <button 
                  className="transcript-toggle"
                  onClick={() => setShowFullTranscript(!showFullTranscript)}
                >
                  {showFullTranscript ? 'Show Preview' : 'Show Full Text'}
                </button>
              </div>
              <div className="transcript-text">
                {showFullTranscript 
                  ? `"${transcript_analysis.full_transcript || transcript_analysis.transcript_text}"`
                  : `"${transcript_analysis.transcript_text}"`
                }
              </div>
              {transcript_analysis.full_transcript && 
               transcript_analysis.full_transcript.length > transcript_analysis.transcript_text.length && 
               !showFullTranscript && (
                <div className="transcript-hint">
                  <small>Click "Show Full Text" to see complete transcript</small>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Feedback */}
      <div className="feedback-section">
        <h4>💡 Feedback</h4>
        <p>{getFeedback()}</p>
      </div>

      {/* Metadata */}
      <div className="metadata-section">
        <div className="metadata-item">
          <span className="metadata-icon">⏱️</span>
          <div>
            <small>Duration</small>
            <strong>{duration_seconds.toFixed(1)}s</strong>
          </div>
        </div>
        <div className="metadata-item">
          <span className="metadata-icon">🎯</span>
          <div>
            <small>Accuracy</small>
            <strong>{confidencePercent}%</strong>
          </div>
        </div>
        {isPhase2 && speech_rate_analysis && (
          <div className="metadata-item">
            <span className="metadata-icon">📊</span>
            <div>
              <small>Words</small>
              <strong>{speech_rate_analysis.estimated_word_count}</strong>
            </div>
          </div>
        )}
      </div>

      {/* Tips Section */}
      <div className="tips-section">
        <h4>📌 Tips for Better Performance</h4>
        <ul>
          <li>Practice deep breathing before answering questions</li>
          <li>Speak at a moderate, steady pace (120-160 WPM)</li>
          <li>Minimize filler words like "um", "uh", "like"</li>
          <li>Use natural pitch variation to sound engaging</li>
          <li>Take brief pauses to think, but avoid long silences</li>
          <li>Practice your answers beforehand to build confidence</li>
        </ul>
      </div>
    </div>
  );
};

export default StressResults;
