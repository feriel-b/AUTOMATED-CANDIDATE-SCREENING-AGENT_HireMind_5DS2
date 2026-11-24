import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './InterviewSimulator.css';

const InterviewSimulator = () => {
  const [roles, setRoles] = useState([]);
  const [categories, setCategories] = useState([]);
  const [questions, setQuestions] = useState([]);
  // Health/status
  const [health, setHealth] = useState(null);
  const [healthError, setHealthError] = useState(null);
  
  const [selectedRole, setSelectedRole] = useState('');
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  
  const [isReadingQuestion, setIsReadingQuestion] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);
  const [audio, setAudio] = useState(null);
  
  // Recording state
  const [isRecording, setIsRecording] = useState(false);
  const [recordedBlob, setRecordedBlob] = useState(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  
  // Interview session state
  const [sessionStarted, setSessionStarted] = useState(false);
  const [sessionComplete, setSessionComplete] = useState(false);
  const [interviewRecording, setInterviewRecording] = useState(null);
  const [allAnswers, setAllAnswers] = useState([]);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [transcriptCopied, setTranscriptCopied] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const [showAllCategories, setShowAllCategories] = useState(false);
  
  const MAX_QUESTIONS = 4;

  // Derive API base URL
  const getApiBaseUrl = () => {
    if (window.location.protocol === 'file:') {
      return 'http://localhost:8000';
    }
    const { protocol, hostname } = window.location;
    return `${protocol}//${hostname}:8000`;
  };

  const API_BASE = getApiBaseUrl();

  // Helper: derive approximate speech intervals when backend doesn't provide them
  const getApproxIntervals = (ia, count) => {
    try {
      const raw = ia?.pause_analysis?.speech_intervals;
      if (Array.isArray(raw) && raw.length > 0) {
        const byStart = raw
          .filter(seg => typeof seg?.start === 'number' && typeof seg?.end === 'number' && seg.end > seg.start)
          .sort((a,b) => a.start - b.start);
        // If we need exactly 'count' segments, try to split largest segments until we reach count
        const n = Math.max(1, Number(count) || byStart.length);
        if (byStart.length >= n) return byStart.slice(0, n);

        // We need to add segments by splitting the longest ones
        const total = (typeof ia?.duration_seconds === 'number')
          ? ia.duration_seconds
          : (typeof ia?.speech_rate_analysis?.duration_seconds === 'number')
            ? ia.speech_rate_analysis.duration_seconds
            : null;
        if (!total || !isFinite(total)) return byStart;

        const minDur = 0.5; // seconds
        const segs = byStart.slice();
        let guard = 0;
        while (segs.length < n && guard < 100) {
          guard++;
          // find the longest segment
          let maxIdx = 0;
          let maxDur = -1;
          for (let i = 0; i < segs.length; i++) {
            const d = segs[i].end - segs[i].start;
            if (d > maxDur) { maxDur = d; maxIdx = i; }
          }
          if (maxDur < 2 * minDur) break; // can't split meaningfully
          const seg = segs[maxIdx];
          const mid = (seg.start + seg.end) / 2;
          const left = { start: seg.start, end: mid };
          const right = { start: mid, end: seg.end };
          // replace with two
          segs.splice(maxIdx, 1, left, right);
          // normalize ordering
          segs.sort((a,b) => a.start - b.start);
        }
        if (segs.length < n) {
          // As a final fallback, produce equal-split segments
          const step = total / n;
          const out = [];
          for (let i = 0; i < n; i++) {
            out.push({ start: Math.max(0, i * step), end: Math.min(total, (i+1)*step) });
          }
          return out;
        }
        return segs.slice(0, n);
      }
      // Fallback: split total duration into N equal segments
      const n = Math.max(1, Number(count) || 1);
      const total = (typeof ia?.duration_seconds === 'number')
        ? ia.duration_seconds
        : (typeof ia?.speech_rate_analysis?.duration_seconds === 'number')
          ? ia.speech_rate_analysis.duration_seconds
          : null;
      if (typeof total === 'number' && isFinite(total) && total > 0) {
        const step = total / n;
        const intervals = [];
        for (let i = 0; i < n; i++) {
          const start = Math.max(0, i * step);
          const end = Math.min(total, (i + 1) * step);
          intervals.push({ start, end });
        }
        return intervals;
      }
    } catch (e) {
      // ignore and return empty
    }
    return [];
  };

  // Fetch roles on mount
  useEffect(() => {
    fetchRoles();
    fetchHealth();
  }, []);

  // Fetch categories when role changes
  useEffect(() => {
    if (selectedRole || showAllCategories) {
      fetchCategories(showAllCategories ? null : selectedRole);
      setSelectedCategories([]);
    }
  }, [selectedRole, showAllCategories]);

  const fetchRoles = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/interview/roles`);
      setRoles(response.data.roles || []);
      setError(null);
    } catch (err) {
      console.error('Error fetching roles:', err);
      setError('Failed to load job roles. Please check API connection.');
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async (role) => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/interview/categories`, {
        params: role ? { role } : {}
      });
      setCategories(response.data.categories || []);
      setError(null);
    } catch (err) {
      console.error('Error fetching categories:', err);
      setError('Failed to load categories.');
    } finally {
      setLoading(false);
    }
  };

  const fetchHealth = async () => {
    try {
      const res = await axios.get(`${API_BASE}/interview/health`, { timeout: 5000 });
      setHealth(res.data || {});
      setHealthError(null);
    } catch (e) {
      console.warn('Health check failed:', e?.message || e);
      setHealth(null);
      setHealthError('Unavailable');
    }
  };

  // Category selection helpers
  const isCategorySelected = (cat) => selectedCategories.includes(cat);
  const toggleCategory = (cat) => {
    setSelectedCategories((prev) => (
      prev.includes(cat) ? prev.filter(c => c !== cat) : [...prev, cat]
    ));
  };

  const startInterview = async () => {
    if (!selectedRole || !selectedCategories || selectedCategories.length === 0) {
      setError('Please select both a role and category.');
      return;
    }

    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/interview/questions`, {
        params: {
          role: selectedRole,
          categories: selectedCategories,
          shuffle: true,
          limit: MAX_QUESTIONS
        },
        paramsSerializer: {
          indexes: null
        }
      });
      
      const fetchedQuestions = response.data.questions || [];
      if (fetchedQuestions.length === 0) {
        setError('No questions found for this role and category.');
        return;
      }

      setQuestions(fetchedQuestions.slice(0, MAX_QUESTIONS));
      setCurrentQuestionIndex(0);
      setCurrentQuestion(fetchedQuestions[0]);
      setSessionStarted(true);
      setSessionComplete(false);
      setAllAnswers([]);
      setError(null);
      
      // Start recording and read first question
      await startRecording();
      setTimeout(() => readQuestion(fetchedQuestions[0]), 1000);
    } catch (err) {
      console.error('Error starting interview:', err);
      setError('Failed to start interview session.');
    } finally {
      setLoading(false);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      mediaRecorder.onstop = async () => {
        const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        // Store raw recording blob; analysis result will be stored in interviewRecording later
        setRecordedBlob(blob);
        stream.getTracks().forEach(track => track.stop());
        
        // Analyze the full interview recording
        await analyzeFullInterview(blob);
      };
      
      mediaRecorder.start();
      setIsRecording(true);
      console.log('✓ Interview recording started');
    } catch (err) {
      console.error('Error starting recording:', err);
      setError('Failed to start recording. Please allow microphone access.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      console.log('✓ Interview recording stopped');
    }
  };

  const readQuestion = async (question) => {
    if (!question) return;

    try {
      setIsReadingQuestion(true);
      
      // Stop any currently playing audio
      if (audio) {
        audio.pause();
        audio.currentTime = 0;
      }

      const response = await axios.post(
        `${API_BASE}/interview/read-question`,
        {
          text: question.question,
          lang: 'en',
          slow: false
        },
        {
          responseType: 'blob'
        }
      );

      const url = URL.createObjectURL(response.data);
      setAudioUrl(url);
      
      const newAudio = new Audio(url);
      setAudio(newAudio);
      
      newAudio.onended = () => {
        setIsReadingQuestion(false);
      };
      
      newAudio.onerror = () => {
        setIsReadingQuestion(false);
        setError('Failed to play question audio.');
      };

      await newAudio.play();
    } catch (err) {
      console.error('Error reading question (backend TTS):', err);
      // Fallback to browser SpeechSynthesis API
      try {
        const synth = window.speechSynthesis;
        if (!synth) throw new Error('SpeechSynthesis not available');
        // Stop any ongoing speech
        if (synth.speaking) synth.cancel();
        const utter = new SpeechSynthesisUtterance(question.question);
        utter.lang = 'en-US';
        utter.rate = 1;
        utter.pitch = 1;
        utter.onend = () => setIsReadingQuestion(false);
        utter.onerror = () => {
          setIsReadingQuestion(false);
          setError('Failed to generate question audio.');
        };
        setIsReadingQuestion(true);
        synth.speak(utter);
      } catch (fallbackErr) {
        console.error('Error reading question (browser TTS):', fallbackErr);
        setError('Failed to generate question audio.');
        setIsReadingQuestion(false);
      }
    }
  };

  const analyzeFullInterview = async (audioBlob) => {
    try {
      // Immediately switch to results view in loading state
      setLoading(true);
      setSessionComplete(true);
      setShowToast(true);

      const formData = new FormData();
      formData.append('file', audioBlob, 'interview.webm');

      const response = await axios.post(
        `${API_BASE}/interview/analyze-voice`,
        formData,
        {
          headers: {
            'Accept': 'application/json'
          },
          // Whisper on CPU can exceed 2 minutes; allow up to 5 minutes
          timeout: 300000
        }
      );

      console.log('✓ Full interview analysis complete:', response.data);

  // Store voice analysis for results display
      const voiceAnalysis = response.data;
      setInterviewRecording(voiceAnalysis);
  // sessionComplete already set to true above to show loading spinner

      // Evaluate all answers in the background (don’t block showing results)
      try {
        const evaluations = await Promise.all(
          (allAnswers || []).map(async (answer) => {
            try {
              const [evalResponse, aiDetectResponse] = await Promise.all([
                axios.post(`${API_BASE}/interview/evaluate-answer`, {
                  user_answer: answer?.transcript || '',
                  expected_answer: answer?.question?.answer || '',
                  question: answer?.question?.question || ''
                }),
                axios.post(`${API_BASE}/interview/detect-ai-answer`, {
                  text: answer?.transcript || ''
                })
              ]);
              return {
                ...answer,
                evaluation: evalResponse.data,
                aiDetection: aiDetectResponse.data
              };
            } catch (err) {
              console.error('Error evaluating/detecting answer:', err);
              return {
                ...answer,
                evaluation: { score: 0, feedback: { level: 'error', message: 'Evaluation failed' } },
                aiDetection: { ai_probability: null, confidence: 0, method: 'error', explanation: 'Detection failed' }
              };
            }
          })
        );
        setAllAnswers(evaluations);
      } catch (err) {
        console.error('Batch evaluation error:', err);
      }

      setLoading(false);
      setShowToast(false);

    } catch (err) {
      console.error('Error analyzing interview:', err);
      setError('Failed to analyze interview recording.');
      setLoading(false);
      setShowToast(false);
    }
  };

  // Helper: format seconds to mm:ss
  const formatTime = (seconds) => {
    if (typeof seconds !== 'number' || !isFinite(seconds)) return '';
    const m = Math.floor(seconds / 60);
    const s = Math.round(seconds % 60);
    return `${m.toString().padStart(2,'0')}:${s.toString().padStart(2,'0')}`;
  };

  // Generate a printable HTML report and trigger Save as PDF via the browser print dialog
  const downloadPdfReport = () => {
    try {
      const win = window.open('', '_blank');
      if (!win) return;
      const ia = interviewRecording || {};
    const transcript = ia?.transcript_analysis?.full_transcript || ia?.transcript_analysis?.transcript_text || '';
    const asrSegments = Array.isArray(ia?.transcript_analysis?.segments) ? ia.transcript_analysis.segments : [];
  const speechIntervals = getApproxIntervals(ia, questions.length);
      const stressPct = typeof ia?.stressed_probability === 'number' ? (ia.stressed_probability * 100).toFixed(1) : 'N/A';
      const confPct = typeof ia?.confidence === 'number' ? (ia.confidence * 100).toFixed(1) : 'N/A';
      const duration = typeof ia?.duration_seconds === 'number' ? ia.duration_seconds : ia?.speech_rate_analysis?.duration_seconds;
      const wpm = ia?.speech_rate_analysis?.words_per_minute;
      const wpmCat = ia?.speech_rate_analysis?.speech_rate_category;
  const fillerCount = ia?.transcript_analysis?.filler_word_count;
      const pauseCount = ia?.pause_analysis?.pause_count;
  const nervousPhrases = ia?.transcript_analysis?.nervous_phrase_count;
  const nervousBreakdown = ia?.transcript_analysis?.nervous_phrase_breakdown || {};

  const html = `
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Interview Report</title>
  <style>
    body { font-family: Arial, sans-serif; padding: 24px; color: #111; }
    h1 { margin: 0 0 8px 0; }
    h2 { margin: 24px 0 8px 0; }
    .meta { color: #444; margin-bottom: 16px; }
    .grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
    .card { border: 1px solid #ddd; border-radius: 8px; padding: 12px; }
    .mono { white-space: pre-wrap; border: 1px solid #eee; padding: 12px; border-radius: 6px; background: #fafafa; }
    table { width: 100%; border-collapse: collapse; }
    td, th { border: 1px solid #e5e5e5; padding: 8px; }
    .small { color: #666; font-size: 12px; }
    @media print { .no-print { display: none; } }
  </style>
  </head>
  <body>
    <h1>Interview Report</h1>
    <div class="meta">Role: ${selectedRole || ''} • Categories: ${(selectedCategories || []).join(', ')} • Questions: ${questions.length}</div>

    <div class="grid">
      <div class="card">
        <h2>Voice Analysis</h2>
        <table>
          <tr><th>Stress Level</th><td>${(ia?.stress_level || '').toString()}</td></tr>
          <tr><th>Stress Probability</th><td>${stressPct}%</td></tr>
          <tr><th>Confidence</th><td>${confPct}%</td></tr>
          <tr><th>Duration</th><td>${typeof duration === 'number' ? duration.toFixed(1)+'s' : 'N/A'}</td></tr>
          <tr><th>Speech Rate</th><td>${typeof wpm === 'number' ? Math.round(wpm) + ' WPM' : 'N/A'} ${wpmCat ? '('+wpmCat+')' : ''}</td></tr>
          <tr><th>Filler Words</th><td>${typeof fillerCount === 'number' ? fillerCount : 'N/A'}</td></tr>
          <tr><th>Pauses</th><td>${typeof pauseCount === 'number' ? pauseCount : 'N/A'}</td></tr>
          <tr><th>Nervous Phrases</th><td>${typeof nervousPhrases === 'number' ? nervousPhrases : 'N/A'}</td></tr>
        </table>
      </div>
      <div class="card">
        <h2>Approx. Answer Times</h2>
        <table>
          <tr><th>#</th><th>Approx Start</th><th>Approx End</th></tr>
          ${speechIntervals.map((seg, i) => `<tr><td>${i+1}</td><td>${formatTime(seg.start)}</td><td>${formatTime(seg.end)}</td></tr>`).join('')}
        </table>
        <div class="small">Intervals derived from speech activity; may not perfectly align to question boundaries.</div>
      </div>
    </div>

    <div class="card" style="margin-top:16px;">
      <h2>Conversation</h2>
      <table>
        <tr><th>#</th><th>Time</th><th>Question</th><th>Answer (excerpt)</th></tr>
        ${speechIntervals.map((seg, i) => {
          // Find ASR segments that overlap this interval
          const parts = asrSegments.filter(s =>
            typeof s?.start === 'number' && typeof s?.end === 'number' && s?.text && s.end > seg.start && s.start < seg.end
          ).map(s => s.text.trim());
          const answer = parts.length > 0 ? parts.join(' ') : (transcript ? transcript : '');
          const safeQ = (questions[i]?.question || '').replace(/&/g,'&amp;').replace(/</g,'&lt;');
          const safeA = (answer || '').replace(/&/g,'&amp;').replace(/</g,'&lt;');
          const time = `${formatTime(seg.start)}–${formatTime(seg.end)}`;
          return `<tr><td>${i+1}</td><td>${time}</td><td>${safeQ}</td><td>${safeA}</td></tr>`;
        }).join('')}
      </table>
      <div class="small">Answers are aligned using speech activity and ASR segment timings; minor offsets are possible.</div>
    </div>

    ${Object.keys(nervousBreakdown).length > 0 ? `
    <div class="card" style="margin-top:16px;">
      <h2>Nervous Phrases (Details)</h2>
      <table>
        <tr><th>Phrase</th><th>Count</th></tr>
        ${Object.entries(nervousBreakdown)
          .sort((a,b) => b[1]-a[1])
          .map(([p,c]) => `<tr><td>${(p||'').replace(/&/g,'&amp;').replace(/</g,'&lt;')}</td><td>${c}</td></tr>`)
          .join('')}
      </table>
    </div>
    ` : ''}

    <div class="card" style="margin-top:16px;">
      <h2>Transcript</h2>
      <div class="mono">${(transcript || '').replace(/&/g,'&amp;').replace(/</g,'&lt;')}</div>
    </div>

    <div class="no-print" style="margin-top:16px;">
      <button onclick="window.print()">Save as PDF</button>
    </div>
  </body>
  </html>`;
      win.document.write(html);
      win.document.close();
      // Auto-open print dialog after a tiny delay for layout
      setTimeout(() => { try { win.focus(); win.print(); } catch(e){} }, 300);
    } catch (e) {
      console.error('PDF generation failed:', e);
    }
  };

  const copyTranscriptToClipboard = async (text) => {
    if (!text) return;
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(text);
      } else {
        const tmp = document.createElement('textarea');
        tmp.value = text;
        document.body.appendChild(tmp);
        tmp.select();
        document.execCommand('copy');
        document.body.removeChild(tmp);
      }
      setTranscriptCopied(true);
      setTimeout(() => setTranscriptCopied(false), 2000);
    } catch (e) {
      console.error('Copy failed:', e);
    }
  };

  const nextQuestion = async () => {
    // Save current answer (placeholder transcript - will be extracted from full recording)
    const currentAnswer = {
      questionIndex: currentQuestionIndex,
      question: currentQuestion,
      transcript: `Answer ${currentQuestionIndex + 1}`, // Placeholder
      timestamp: new Date().toISOString()
    };
    
    setAllAnswers([...allAnswers, currentAnswer]);
    
    if (currentQuestionIndex < questions.length - 1) {
      // Move to next question
      const nextIndex = currentQuestionIndex + 1;
      setCurrentQuestionIndex(nextIndex);
      setCurrentQuestion(questions[nextIndex]);
      
      // Stop audio if playing
      if (audio) {
        audio.pause();
      }
      
      // Read next question
      setTimeout(() => readQuestion(questions[nextIndex]), 500);
    } else {
      // All questions complete - stop recording and analyze
      stopRecording();
    }
  };

  const exitInterview = async () => {
    // Stop audio if playing
    if (audio) {
      audio.pause();
    }

    // If recording is active, stop it and trigger analysis via onstop handler
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      setLoading(true);
      stopRecording();
      return;
    }

    // If we already have a recorded blob (e.g., recording already stopped), analyze it
    if (recordedBlob) {
      setLoading(true);
      await analyzeFullInterview(recordedBlob);
      return;
    }

    // No recording captured yet – confirm exit without results
    const confirmExit = window.confirm('No recording captured yet. Exit without results?');
    if (confirmExit) {
      restartInterview();
    }
  };

  const restartInterview = () => {
    // Stop recording if active
    if (isRecording) {
      stopRecording();
    }
    
    setSessionStarted(false);
    setSessionComplete(false);
    setQuestions([]);
    setCurrentQuestion(null);
    setCurrentQuestionIndex(0);
    setAllAnswers([]);
    setInterviewRecording(null);
    setSelectedRole('');
  setSelectedCategories([]);
    
    if (audio) {
      audio.pause();
    }
  };

  // Setup screen
  if (!sessionStarted) {
    return (
      <div className="interview-simulator ai-dashboard">
        <header className="ai-header">
          <div className="brand">
            <div className="logo-spark" />
            <span>AI Interview Assistant</span>
          </div>
          <div className="status-chips">
            <span className={`chip ${health ? 'ok' : 'warn'}`} title="Backend health">
              {health ? 'API: healthy' : (healthError ? 'API: unavailable' : 'API: ...')}
            </span>
            <span className={`chip ${health?.models?.vad === 'ready' ? 'ok' : 'warn'}`} title="Voice Activity Detection">
              VAD: {health?.models?.vad || 'unknown'}
            </span>
            <button className="chip action" onClick={fetchHealth}>Refresh</button>
          </div>
        </header>

        {error && (
          <div className="error-banner">
            {error}
          </div>
        )}

        <div className="dashboard-main">
          <aside className="dashboard-left">
            <div className="panel">
              <div className="panel-title">Filters</div>

              <div className="form-group">
                <label htmlFor="role-select">Job Role</label>
                <select
                  id="role-select"
                  className="form-select"
                  value={selectedRole}
                  onChange={(e) => setSelectedRole(e.target.value)}
                  disabled={loading}
                >
                  <option value="">-- Select a Role --</option>
                  {roles.map((role, idx) => (
                    <option key={idx} value={role}>{role}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Categories {categories?.length ? `(${categories.length})` : ''}</label>
                <div className="category-controls">
                  <div className="toggle-all">
                    <input
                      id="all-cats"
                      type="checkbox"
                      checked={showAllCategories}
                      onChange={(e) => setShowAllCategories(e.target.checked)}
                      disabled={loading}
                    />
                    <label htmlFor="all-cats">Show all (ignore role filter)</label>
                  </div>
                  <div className="selected-count">Selected: {selectedCategories.length}</div>
                </div>

                <div className={`category-checklist ${loading || (!selectedRole && !showAllCategories) ? 'disabled' : ''}`}>
                  {categories.map((cat, idx) => (
                    <label key={idx} className={`category-item ${isCategorySelected(cat) ? 'active' : ''}`}>
                      <input
                        type="checkbox"
                        checked={isCategorySelected(cat)}
                        onChange={() => toggleCategory(cat)}
                        disabled={loading || (!selectedRole && !showAllCategories)}
                      />
                      <span className="category-name">{cat}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </aside>

          <main className="dashboard-center">
            <div className="page-title">
              <h1>🎯 Interview Simulator</h1>
              <p>Practice your interview skills with AI-powered feedback</p>
            </div>

            <div className="preview-grid">
              <div className="panel">
                <div className="panel-title">AI Interviewer</div>
                <div className="avatar-row">
                  <div className={`avatar-container ${isReadingQuestion ? 'speaking' : ''}`}>
                    <div className={`avatar-image ${isReadingQuestion ? 'speaking' : ''}`}>
                      <div className="face-features">
                        <div className="eyes">
                          <div className="eye"></div>
                          <div className="eye"></div>
                        </div>
                        <div className="mouth"></div>
                      </div>
                    </div>
                  </div>
                  <div className={`ai-status ${isReadingQuestion ? 'speaking' : ''}`}>
                    {isReadingQuestion ? '🔊 Speaking...' : 'Ready to assist'}
                  </div>
                </div>
              </div>

              <div className="panel callout">
                <div className="panel-title">Quick Start</div>
                <p>Select a role and at least one category, then start your 4-question session. The AI will read each question automatically.</p>
                <button
                  className="start-btn"
                  onClick={startInterview}
                  disabled={loading || !selectedRole || selectedCategories.length === 0}
                >
                  {loading ? '⏳ Loading…' : '▶️ Start Interview'}
                </button>
              </div>
            </div>
          </main>

          <aside className="dashboard-right">
            <div className="panel">
              <div className="panel-title">System Status</div>
              <div className="stat-grid">
                <div className="stat">
                  <div className="stat-label">API</div>
                  <div className={`stat-value ${health ? 'ok' : 'warn'}`}>{health ? 'Healthy' : 'Unknown'}</div>
                </div>
                <div className="stat">
                  <div className="stat-label">Wav2Vec2</div>
                  <div className="stat-value">{health?.models?.wav2vec2 || '—'}</div>
                </div>
                <div className="stat">
                  <div className="stat-label">Stress Model</div>
                  <div className="stat-value">{health?.models?.stress_recognition || '—'}</div>
                </div>
                <div className="stat">
                  <div className="stat-label">VAD</div>
                  <div className={`stat-value ${health?.models?.vad === 'ready' ? 'ok' : 'warn'}`}>{health?.models?.vad || '—'}</div>
                </div>
              </div>
            </div>

            <div className="panel tips">
              <div className="panel-title">Tips</div>
              <ul className="tips-list">
                <li>Use headphones to avoid echo.</li>
                <li>Answer concisely in 30–60 seconds.</li>
                <li>Pause briefly before you start speaking.</li>
              </ul>
            </div>
          </aside>
        </div>
      </div>
    );
  }

  // Interview session screen - Results (Dashboard layout)
  if (sessionComplete) {
    return (
      <div className="interview-simulator ai-dashboard">
        <header className="ai-header">
          <div className="brand">
            <div className="logo-spark" />
            <span>AI Interview Assistant</span>
          </div>
          <div className="status-chips">
            <span className={`chip ${loading ? 'warn' : 'ok'}`}>{loading ? 'Analyzing…' : 'Complete'}</span>
            <span className={`chip ${health ? 'ok' : 'warn'}`}>API</span>
          </div>
        </header>

        <div className="dashboard-main">
          <aside className="dashboard-left">
            <div className="panel">
              <div className="panel-title">Session</div>
              <div className="session-summary">
                <div><strong>Role:</strong> {selectedRole}</div>
                <div><strong>Categories:</strong> {selectedCategories.join(', ')}</div>
                <div><strong>Questions:</strong> {questions.length}</div>
              </div>
              <button className="restart-btn" onClick={restartInterview} style={{width:'100%', marginTop: '1rem'}}>Start New Interview</button>
            </div>
          </aside>

          <main className="dashboard-center">
            <div className="page-title">
              <h1>{loading ? '⏳ Analyzing your interview…' : '✅ Interview Complete'}</h1>
              {!loading && <p>Here are your results</p>}
            </div>

            {loading ? (
              <div className="loading-card">
                <div className="spinner"></div>
                <p>Analyzing your performance...</p>
              </div>
            ) : (
              <div className="results-container">
            <div className="completion-card">
              <h2>📊 Session Summary</h2>
              <p>Role: <strong>{selectedRole}</strong></p>
              <p>Categories: <strong>{selectedCategories.join(', ')}</strong></p>
              <p>Questions Answered: <strong>{questions.length}</strong></p>
            </div>

            {/* Voice Analysis Results */}
            {interviewRecording && (
              <div className="voice-analysis-card">
                <h2>🎤 Voice Analysis Results</h2>
                {(() => {
                  const lvl = (interviewRecording.stress_level || '').toLowerCase();
                  const stressClass = lvl.includes('very') ? 'very-high' :
                                     lvl.includes('moderate') ? 'medium' :
                                     lvl.includes('low') ? 'low' :
                                     lvl.includes('high') ? 'high' : '';
                  const stressedProb = (typeof interviewRecording.stressed_probability === 'number')
                    ? interviewRecording.stressed_probability
                    : (typeof interviewRecording.stress_probability === 'number')
                      ? interviewRecording.stress_probability
                      : null;
                  const probText = (stressedProb !== null)
                    ? `${(stressedProb * 100).toFixed(1)}%`
                    : 'N/A';
                  const confText = (typeof interviewRecording.confidence === 'number')
                    ? `${(interviewRecording.confidence * 100).toFixed(1)}%`
                    : 'N/A';
                  const durationSec = (typeof interviewRecording.duration_seconds === 'number')
                    ? interviewRecording.duration_seconds
                    : (typeof interviewRecording.speech_rate_analysis?.duration_seconds === 'number')
                      ? interviewRecording.speech_rate_analysis.duration_seconds
                      : null;
                  const durationText = (durationSec !== null)
                    ? `${durationSec.toFixed(1)} seconds`
                    : 'N/A';
                  // Highlights data
                  const fillerCount = interviewRecording.transcript_analysis?.filler_word_count ?? null;
                  const fillerBreakdown = interviewRecording.transcript_analysis?.filler_breakdown || {};
                  const topFillers = Object.entries(fillerBreakdown)
                    .sort((a,b) => b[1]-a[1])
                    .slice(0,3);
                  const pauseCount = interviewRecording.pause_analysis?.pause_count ?? null;
                  const totalPauseTime = interviewRecording.pause_analysis?.total_pause_time ?? null;
                  const wpm = interviewRecording.speech_rate_analysis?.words_per_minute ?? null;
                  const wpmCat = interviewRecording.speech_rate_analysis?.speech_rate_category ?? '';
                  const nervousPhrases = interviewRecording.transcript_analysis?.nervous_phrase_count ?? 0;
                  const nervousBreakdown = interviewRecording.transcript_analysis?.nervous_phrase_breakdown || {};

                  // Friendly explanation
                  const explanations = [];
                  if (stressedProb !== null) {
                    if (stressedProb >= 0.8) explanations.push('Your stress probability is very high. Focus on breathing and slowing down before answering.');
                    else if (stressedProb >= 0.6) explanations.push('Your stress appears elevated. Try pausing briefly before speaking to organize thoughts.');
                    else if (stressedProb >= 0.4) explanations.push('Moderate stress detected. A calm pace and concise structure will help.');
                    else explanations.push('Low stress detected. Keep the same confident pace.');
                  }
                  if (typeof fillerCount === 'number') {
                    if (fillerCount > 10) explanations.push('Frequent filler words reduce clarity. Practice replacing them with short pauses.');
                    else if (fillerCount > 4) explanations.push('Some filler words present. Aim for shorter sentences to reduce them.');
                  }
                  if (typeof pauseCount === 'number') {
                    if (pauseCount === 0) explanations.push('Consider adding brief pauses to structure your answer.');
                    else if (pauseCount > 8) explanations.push('Many pauses detected. Try to maintain a steady flow with fewer breaks.');
                  }
                  if (typeof wpm === 'number') {
                    if (wpm > 180) explanations.push('You spoke quite fast. Slowing down can improve clarity and poise.');
                    else if (wpm < 110) explanations.push('Your pace is slow. Slightly increasing pace can convey confidence.');
                  }

                  const fullTranscript = interviewRecording.transcript_analysis?.full_transcript
                    || interviewRecording.transcript_analysis?.transcript_text || '';

                  // Tips to Improve
                  const tips = [];
                  if (stressedProb !== null && stressedProb >= 0.6) tips.push('Before answering, take a deep breath and pause for 1–2 seconds to lower stress.');
                  if ((interviewRecording.transcript_analysis?.filler_word_ratio ?? 0) > 0.08) tips.push('Replace filler words with short silence. Practice mock answers to reduce “um/uh/like”.');
                  if ((interviewRecording.pause_analysis?.pause_frequency ?? 0) > 0.8) tips.push('Group ideas into 2–3 sentences and keep fewer, purposeful pauses.');
                  if (wpm && wpm > 180) tips.push('Slow down slightly—aim for ~140–160 WPM.');
                  if (wpm && wpm < 110) tips.push('Increase pace a bit—aim for ~130–160 WPM.');
                  const pitchCat = interviewRecording.pitch_analysis?.pitch_category;
                  if (pitchCat === 'monotone') tips.push('Add small pitch variation to emphasize key points.');
                  if (pitchCat === 'highly_variable') tips.push('Keep a steadier tone to sound more composed.');
                  if ((interviewRecording.transcript_analysis?.apology_count ?? 0) > 0) tips.push('Avoid apologizing mid-answer; stay composed and continue.');
                  if (nervousPhrases > 0) tips.push('Swap nervous phrases with confident alternatives (e.g., “I believe...” instead of “I’m not sure but...”).');

                  return (
                    <>
                      <div className="analysis-grid">
                        <div className="analysis-item">
                          <span className="analysis-label">Stress Level:</span>
                          <span className={`stress-level ${stressClass}`}>
                            {(interviewRecording.stress_level || '').toUpperCase() || 'UNKNOWN'}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Stress Probability:</span>
                          <span className="analysis-value">{probText}</span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Confidence:</span>
                          <span className="analysis-value">{confText}</span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Audio Duration:</span>
                          <span className="analysis-value">{durationText}</span>
                        </div>
                      </div>

                      {/* Highlights */}
                      <div className="highlight-card">
                        <h3>Key Highlights</h3>
                        <div className="highlight-grid">
                          <div className="highlight">
                            <div className="label">Filler words</div>
                            <div className="value">{typeof fillerCount === 'number' ? fillerCount : 'N/A'}</div>
                            {topFillers.length > 0 && (
                              <div className="subtext">
                                {topFillers.map(([word,count],i) => (
                                  <span key={i} className="pill">{word}: {count}</span>
                                ))}
                              </div>
                            )}
                          </div>
                          <div className="highlight">
                            <div className="label">Pauses</div>
                            <div className="value">{typeof pauseCount === 'number' ? pauseCount : 'N/A'}</div>
                            <div className="subtext">{typeof totalPauseTime === 'number' ? `${totalPauseTime.toFixed(1)}s total` : ''}</div>
                          </div>
                          <div className="highlight">
                            <div className="label">Speech rate</div>
                            <div className="value">{typeof wpm === 'number' ? Math.round(wpm) : 'N/A'} WPM</div>
                            <div className="subtext">{wpmCat}</div>
                          </div>
                          <div className="highlight">
                            <div className="label">Nervous phrases</div>
                            <div className="value">{nervousPhrases}</div>
                          </div>
                        </div>
                      </div>

                      {/* Explanation */}
                      {explanations.length > 0 && (
                        <div className="explanation-card">
                          <h3>What this means</h3>
                          <ul>
                            {explanations.map((txt, idx) => <li key={idx}>{txt}</li>)}
                          </ul>
                        </div>
                      )}

                      {/* Tips to Improve */}
                      {tips.length > 0 && (
                        <div className="explanation-card">
                          <h3>Tips to Improve</h3>
                          <ul>
                            {tips.map((t, i) => <li key={i}>{t}</li>)}
                          </ul>
                        </div>
                      )}

                      {/* Nervous Phrases */}
                      {(
                        (Array.isArray(interviewRecording.transcript_analysis?.detected_nervous_phrases) && interviewRecording.transcript_analysis.detected_nervous_phrases.length > 0)
                        || (Object.keys(nervousBreakdown).length > 0)
                      ) && (
                        <div className="questions-card">
                          <h3>Nervous Phrases Detected</h3>
                          {Object.keys(nervousBreakdown).length > 0 ? (
                            <div className="pill-list">
                              {Object.entries(nervousBreakdown)
                                .sort((a,b) => b[1]-a[1])
                                .map(([p, c], i) => (
                                  <span key={i} className="pill">{p}: {c}</span>
                                ))}
                            </div>
                          ) : (
                            <div className="pill-list">
                              {interviewRecording.transcript_analysis.detected_nervous_phrases.map((p, i) => (
                                <span key={i} className="pill">{p}</span>
                              ))}
                            </div>
                          )}
                        </div>
                      )}

                      {/* Conversation Timeline (includes actions) */}
                      {(() => {
                        const intervals = getApproxIntervals(interviewRecording, questions.length).slice();
                        const segments = Array.isArray(interviewRecording?.transcript_analysis?.segments)
                          ? interviewRecording.transcript_analysis.segments : [];
                        const conv = intervals
                          .sort((a,b) => a.start - b.start)
                          .slice(0, questions.length)
                          .map((seg, i) => {
                            const parts = segments.filter(s =>
                              typeof s?.start === 'number' && typeof s?.end === 'number' && s?.text && s.end > seg.start && s.start < seg.end
                            ).map(s => s.text.trim());
                            const answerText = parts.length > 0 ? parts.join(' ') : (fullTranscript || '');
                            return { idx: i, time: `${formatTime(seg.start)}–${formatTime(seg.end)}`, question: questions[i]?.question || '', answer: answerText };
                          });
                        return (
                          <div className="questions-card">
                            <div className="transcript-header">
                              <h3>Conversation Timeline</h3>
                              <div>
                                <button className="copy-btn" onClick={() => copyTranscriptToClipboard(fullTranscript)} disabled={!fullTranscript}>
                                  {transcriptCopied ? 'Copied ✓' : 'Copy Transcript'}
                                </button>
                                <button className="copy-btn" onClick={downloadPdfReport} disabled={!interviewRecording} style={{ marginLeft: 8 }}>
                                  Download PDF
                                </button>
                              </div>
                            </div>
                            <ol className="question-list">
                              {conv.map(item => (
                                <li key={item.idx}>
                                  <div><strong>[{item.time}]</strong> {item.question}</div>
                                  <div className="subtext" style={{marginTop:'6px'}}><em>Answer:</em> {item.answer || '—'}</div>
                                </li>
                              ))}
                            </ol>
                          </div>
                        );
                      })()}

                      {/* Full transcript panel removed; actions moved into Conversation Timeline header */}
                    </>
                  );
                })()}
              </div>
            )}

            {/* Individual Question Results */}
            <div className="question-results">
              <h2>📝 Question-by-Question Results</h2>
              {allAnswers.map((answer, idx) => (
                <div key={idx} className="answer-result-card">
                  <div className="result-header">
                    <h3>Question {idx + 1}</h3>
                    {answer.evaluation && (
                      <div className="score-badge" style={{ backgroundColor: answer.evaluation.feedback.color }}>
                        {answer.evaluation.score}/100
                      </div>
                    )}
                  </div>
                  
                  <p className="result-question"><strong>Q:</strong> {answer.question.question}</p>
                  {answer.timestamp && (
                    <div className="result-timestamp">Answered at: {new Date(answer.timestamp).toLocaleString()}</div>
                  )}
                  
                  {answer.evaluation && (
                    <div className="evaluation-summary">
                      <p className="feedback-text">{answer.evaluation.feedback.message}</p>
                      <div className="score-breakdown">
                        <span>Semantic: {answer.evaluation.semantic_score}%</span>
                        <span>Keywords: {answer.evaluation.keyword_score}%</span>
                        {answer.aiDetection && typeof answer.aiDetection.ai_probability === 'number' && (
                          <span>
                            AI-likelihood: {(answer.aiDetection.ai_probability * 100).toFixed(0)}%
                            {answer.aiDetection.confidence ? ` (conf: ${(answer.aiDetection.confidence * 100).toFixed(0)}%)` : ''}
                          </span>
                        )}
                      </div>
                      {answer.aiDetection && answer.aiDetection.explanation && (
                        <div className="subtext" style={{ marginTop: 6 }}>
                          <em>{answer.aiDetection.explanation}</em>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
            
            <button className="restart-btn" onClick={restartInterview}>
              🔄 Start New Interview
            </button>
          </div>
            )}
          </main>

          <aside className="dashboard-right">
            {!loading && interviewRecording && (
              <div className="panel">
                <div className="panel-title">At a glance</div>
                <div className="stat-grid">
                  <div className="stat"><div className="stat-label">Stress</div><div className="stat-value">{(interviewRecording?.stressed_probability != null ? (interviewRecording.stressed_probability*100).toFixed(0)+'%' : '—')}</div></div>
                  <div className="stat"><div className="stat-label">Confidence</div><div className="stat-value">{(interviewRecording?.confidence != null ? (interviewRecording.confidence*100).toFixed(0)+'%' : '—')}</div></div>
                  <div className="stat"><div className="stat-label">Pauses</div><div className="stat-value">{interviewRecording?.pause_analysis?.pause_count ?? '—'}</div></div>
                  <div className="stat"><div className="stat-label">WPM</div><div className="stat-value">{interviewRecording?.speech_rate_analysis?.words_per_minute ? Math.round(interviewRecording.speech_rate_analysis.words_per_minute) : '—'}</div></div>
                </div>
              </div>
            )}
          </aside>
        </div>
      </div>
    );
  }

  return (
    <div className="interview-simulator ai-dashboard">
      <header className="ai-header">
        <div className="brand">
          <div className="logo-spark" />
          <span>AI Interview Assistant</span>
        </div>
        <div className="status-chips">
          <span className={`chip ${health ? 'ok' : 'warn'}`}>{health ? 'API: healthy' : 'API: unknown'}</span>
          {isRecording && (
            <span className="chip rec">● Recording</span>
          )}
        </div>
      </header>
      {showToast && (
        <div className="toast">Analyzing recording… This may take a minute.</div>
      )}
      {error && (
        <div className="error-banner">{error}</div>
      )}
      <div className="dashboard-main">
        <aside className="dashboard-left">
          <div className="panel">
            <div className="panel-title">Session</div>
            <div className="session-progress">Question {currentQuestionIndex + 1} / {questions.length}</div>
            <div className="chips-row">
              <span className="chip tag">{selectedRole}</span>
              {selectedCategories.map((cat, i) => (
                <span key={i} className="chip tag">{cat}</span>
              ))}
            </div>
            <div className="panel-actions">
              <button 
                className="next-btn" 
                onClick={nextQuestion}
                disabled={isReadingQuestion}
              >
                {currentQuestionIndex < questions.length - 1 ? 'Next Question →' : 'Finish Interview ✓'}
              </button>
              <button className="exit-btn" onClick={exitInterview}>Exit Interview</button>
            </div>
          </div>
        </aside>

        <main className="dashboard-center">
          <div className="question-card">
            <div className="question-header">
              <span className="question-label">Question {currentQuestionIndex + 1}</span>
              {isReadingQuestion && (
                <span className="reading-indicator">AI Reading</span>
              )}
            </div>
            <div className="avatar-row">
              <div className={`avatar-container ${isReadingQuestion ? 'speaking' : ''}`}>
                <div className={`avatar-image ${isReadingQuestion ? 'speaking' : ''}`}>
                  <div className="face-features">
                    <div className="eyes">
                      <div className="eye"></div>
                      <div className="eye"></div>
                    </div>
                    <div className="mouth"></div>
                  </div>
                </div>
              </div>
              <div className={`ai-status ${isReadingQuestion ? 'speaking' : ''}`}>
                {isReadingQuestion ? '🔊 Speaking...' : 'Ready to assist'}
              </div>
            </div>
            <p className="question-text">{currentQuestion?.question}</p>
            <div className="question-meta">
              <span className="badge">{selectedRole}</span>
              {selectedCategories.map((cat, i) => (
                <span key={i} className="badge">{cat}</span>
              ))}
            </div>
          </div>

          <div className="instructions-card">
            <h3>Instructions</h3>
            <p>
              {isReadingQuestion 
                ? 'Listen carefully to the AI reading the question...'
                : 'Speak your answer clearly, then click "Next Question" when ready.'
              }
            </p>
          </div>
        </main>

        <aside className="dashboard-right">
          <div className="panel">
            <div className="panel-title">Live Status</div>
            <div className="live-status-row">
              <div className={`status-pill ${isRecording ? 'on' : ''}`}>
                <span className="dot" /> {isRecording ? 'Recording' : 'Idle'}
              </div>
              <div className={`status-pill ${isReadingQuestion ? 'on' : ''}`}>
                <span className="dot" /> {isReadingQuestion ? 'Speaking' : 'Silent'}
              </div>
            </div>
          </div>
          <div className="panel tips">
            <div className="panel-title">Tips</div>
            <ul className="tips-list">
              <li>Speak close to the mic for clarity.</li>
              <li>Use brief pauses to structure thoughts.</li>
              <li>Aim for confident, steady pace.</li>
            </ul>
          </div>
        </aside>
      </div>
    </div>
  );
};

export default InterviewSimulator;
