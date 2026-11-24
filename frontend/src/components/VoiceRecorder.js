import React, { useState, useRef } from 'react';
import axios from 'axios';
import './VoiceRecorder.css';
import StressResults from './StressResults';

// Prefer environment variable, otherwise derive from current host (handles 127.0.0.1 vs localhost).
// If opened as file:// (no dev server), fall back to http://localhost:8000.
const deriveApiBase = () => {
  const env = process.env.REACT_APP_API_BASE_URL;
  if (env) return env;
  const proto = window.location.protocol;
  if (proto.startsWith('http')) {
    const host = window.location.hostname || 'localhost';
    return `${proto}//${host}:8000`;
  }
  // file:// or other protocols
  console.warn('Non-HTTP context detected; defaulting API base to http://localhost:8000');
  return 'http://localhost:8000';
};
const API_BASE_URL = deriveApiBase();

const VoiceRecorder = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [error, setError] = useState(null);
  const [recordingTime, setRecordingTime] = useState(0);
  const [apiStatus, setApiStatus] = useState(null);
  
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const timerRef = useRef(null);

  // Start recording
  const startRecording = async () => {
    try {
      setError(null);
      setAnalysisResults(null);
      
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];
      
      // Collect audio data
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };
      
      // Handle recording stop
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        setAudioBlob(blob);
        setAudioUrl(URL.createObjectURL(blob));
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };
      
      // Start recording
      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);
      
      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
      
    } catch (err) {
      console.error('Error starting recording:', err);
      setError('Failed to access microphone. Please grant permission and try again.');
    }
  };

  // Stop recording
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      // Stop timer
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  };

  // Analyze the recorded audio
  const analyzeAudio = async () => {
    if (!audioBlob) {
      setError('No audio to analyze. Please record first.');
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    
    try {
      // Debug: show blob size and endpoint
      console.log('AnalyzeAudio: blob size(bytes)=', audioBlob.size, 'POST', `${API_BASE_URL}/interview/analyze-voice`);
      // Convert webm to wav (server accepts various formats)
      const formData = new FormData();
      formData.append('file', audioBlob, 'recording.webm');
      
      // Send to backend
      const response = await axios.post(
        `${API_BASE_URL}/interview/analyze-voice`,
        formData,
        {
          // Do not set Content-Type manually; let browser set boundary for multipart
          withCredentials: false,
          timeout: 60000
        }
      );
      
      setAnalysisResults(response.data);
      
    } catch (err) {
      // Improve error visibility
      const status = err.response?.status;
      const detail = err.response?.data?.detail;
      console.error('Analysis error:', { status, detail, err });
      const fallback = 'Failed to analyze audio. Please try again.';
      const errorMsg = detail || (status ? `Error ${status}` : null) || fallback;
      setError(errorMsg);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Test API connectivity (health check)
  const testApi = async () => {
    setApiStatus(null);
    setError(null);
    try {
      console.log('Testing API at', `${API_BASE_URL}/interview/health`);
      const res = await axios.get(`${API_BASE_URL}/interview/health`, { timeout: 15000 });
      setApiStatus(`API OK: ${res?.data?.status || 'healthy'}`);
    } catch (e) {
      console.error('Health check failed:', e);
      setApiStatus(null);
      setError('Cannot reach API. Check that the backend is running at ' + API_BASE_URL);
    }
  };

  // Reset everything
  const reset = () => {
    setAudioBlob(null);
    setAudioUrl(null);
    setAnalysisResults(null);
    setError(null);
    setRecordingTime(0);
  };

  // Format time as MM:SS
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="voice-recorder-container">
      <div className="recorder-card">
        <div className="recorder-header">
          <h2>🎙️ Voice Recorder</h2>
          <p>Record your interview answer and get instant stress analysis</p>
        </div>

        <div className="recorder-body">
          {/* Recording Controls */}
          <div className="recording-section">
            {isRecording && (
              <div className="recording-indicator">
                <span className="pulse-dot"></span>
                <span className="recording-text">Recording... {formatTime(recordingTime)}</span>
              </div>
            )}
            
            <div className="button-group">
              {!isRecording ? (
                <button 
                  className="btn btn-primary btn-large"
                  onClick={startRecording}
                  disabled={isAnalyzing}
                >
                  <span className="btn-icon">🎤</span>
                  Start Recording
                </button>
              ) : (
                <button 
                  className="btn btn-danger btn-large"
                  onClick={stopRecording}
                >
                  <span className="btn-icon">⏹️</span>
                  Stop Recording
                </button>
              )}
            </div>
          </div>

          {/* Audio Playback */}
          {audioUrl && !isRecording && (
            <div className="audio-section">
              <h3>📼 Your Recording</h3>
              <audio controls src={audioUrl} className="audio-player" />
              
              <div className="button-group">
                <button 
                  className="btn btn-success"
                  onClick={analyzeAudio}
                  disabled={isAnalyzing}
                >
                  {isAnalyzing ? (
                    <>
                      <span className="spinner"></span>
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <span className="btn-icon">🧠</span>
                      Analyze Voice
                    </>
                  )}
                </button>
                
                <button 
                  className="btn btn-outline"
                  onClick={testApi}
                  disabled={isAnalyzing}
                >
                  <span className="btn-icon">🧪</span>
                  Test API
                </button>

                <a
                  className="btn btn-outline"
                  href={audioUrl}
                  download="recording.webm"
                  onClick={(e) => {
                    if (!audioUrl) e.preventDefault();
                  }}
                >
                  <span className="btn-icon">💾</span>
                  Download Recording
                </a>
                
                <button 
                  className="btn btn-secondary"
                  onClick={reset}
                  disabled={isAnalyzing}
                >
                  <span className="btn-icon">🔄</span>
                  New Recording
                </button>
              </div>
              {apiStatus && (
                <div className="tip-box" style={{ marginTop: '8px' }}>
                  {apiStatus}
                </div>
              )}
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="error-box">
              <span className="error-icon">⚠️</span>
              <span>{error}</span>
            </div>
          )}

          {/* Analysis Results */}
          {analysisResults && (
            <StressResults results={analysisResults} />
          )}
        </div>
      </div>

      {/* Instructions */}
      <div className="instructions-card">
        <h3>📋 Instructions</h3>
        <ol>
          <li>Click <strong>"Start Recording"</strong> and speak your answer</li>
          <li>Click <strong>"Stop Recording"</strong> when finished</li>
          <li>Play back your recording to review</li>
          <li>Click <strong>"Analyze Voice"</strong> to get stress analysis</li>
          <li>View your stress levels and insights</li>
        </ol>
        
        <div className="tip-box">
          <strong>💡 Tip:</strong> Speak naturally for at least 5-10 seconds for best results
        </div>
      </div>
    </div>
  );
};

export default VoiceRecorder;
