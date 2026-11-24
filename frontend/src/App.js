import React, { useState } from 'react';
import './App.css';
import VoiceRecorder from './components/VoiceRecorder';
import InterviewSimulator from './components/InterviewSimulator';

function App() {
  const [currentView, setCurrentView] = useState('home');

  const renderView = () => {
    switch (currentView) {
      case 'voice-analysis':
        return (
          <div className="App">
            <header className="App-header">
              <h1>🎤 HireMind Voice Stress Analysis</h1>
              <p>AI-Powered Voice Stress Detection</p>
              <button className="nav-btn" onClick={() => setCurrentView('home')}>
                ← Back to Home
              </button>
            </header>
            
            <main className="App-main">
              <VoiceRecorder />
            </main>
            
            <footer className="App-footer">
              <p>Phase 2: Advanced Voice Analysis | Powered by AI</p>
            </footer>
          </div>
        );

      case 'interview-simulator':
        return <InterviewSimulator />;

      default:
        return (
          <div className="App">
            <header className="App-header">
              <h1>🎯 HireMind AI Platform</h1>
              <p>AI-Powered Candidate Screening & Interview Practice</p>
            </header>
            
            <main className="App-main home-view">
              <div className="feature-cards">
                <div className="feature-card" onClick={() => setCurrentView('voice-analysis')}>
                  <div className="feature-icon">🎤</div>
                  <h2>Voice Stress Analysis</h2>
                  <p>Analyze voice recordings for stress indicators, pauses, speech patterns, and nervousness levels.</p>
                  <button className="feature-btn">Try Voice Analysis →</button>
                </div>

                <div className="feature-card" onClick={() => setCurrentView('interview-simulator')}>
                  <div className="feature-icon">💼</div>
                  <h2>AI Interview Simulator</h2>
                  <p>Practice interview questions with AI feedback, TTS question reading, and answer quality evaluation.</p>
                  <button className="feature-btn">Start Interview Practice →</button>
                </div>
              </div>
            </main>
            
            <footer className="App-footer">
              <p>HireMind Platform | Powered by AI</p>
            </footer>
          </div>
        );
    }
  };

  return renderView();
}

export default App;

