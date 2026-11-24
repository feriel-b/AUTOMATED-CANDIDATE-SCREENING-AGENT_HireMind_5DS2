import React, { useState, useEffect, useRef, useMemo } from 'react';
import { Progress } from './ui/progress';
import { toast } from 'sonner';
import { Download, RotateCcw, Volume2 } from 'lucide-react';
import '../styles/InterviewSimulatorFrontend.css';

function useApiBase() {
  return useMemo(() => {
    if (typeof window !== "undefined") {
      if (window.location.protocol === "file:") return "http://localhost:8000";
      const { protocol, hostname } = window.location;
      return `${protocol}//${hostname}:8000`;
    }
    return "http://localhost:8000";
  }, []);
}

export const InterviewPracticeIntegrated = () => {
  const API_BASE = useApiBase();
  const [roles, setRoles] = useState<string[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [questions, setQuestions] = useState<any[]>([]);
  const [health, setHealth] = useState<any>(null);
  const [healthError, setHealthError] = useState<string | null>(null);
  
  const [selectedRole, setSelectedRole] = useState('');
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [currentQuestion, setCurrentQuestion] = useState<any>(null);
  
  const [isReadingQuestion, setIsReadingQuestion] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [audio, setAudio] = useState<HTMLAudioElement | null>(null);
  
  const [isRecording, setIsRecording] = useState(false);
  const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  
  const [sessionStarted, setSessionStarted] = useState(false);
  const [sessionComplete, setSessionComplete] = useState(false);
  const [interviewRecording, setInterviewRecording] = useState<any>(null);
  const [allAnswers, setAllAnswers] = useState<any[]>([]);
  const allAnswersRef = useRef<any[]>([]);
  
  const [questionStartTime, setQuestionStartTime] = useState<number | null>(null);
  const recordingStartTimeRef = useRef<number | null>(null);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [transcriptCopied, setTranscriptCopied] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const [showAllCategories, setShowAllCategories] = useState(false);
  
  const MAX_QUESTIONS = 4;

  const getApproxIntervals = (ia: any, count: number) => {
    try {
      const raw = ia?.pause_analysis?.speech_intervals;
      if (Array.isArray(raw) && raw.length > 0) {
        const byStart = raw
          .filter(seg => typeof seg?.start === 'number' && typeof seg?.end === 'number' && seg.end > seg.start)
          .sort((a,b) => a.start - b.start);
        const n = Math.max(1, Number(count) || byStart.length);
        if (byStart.length >= n) return byStart.slice(0, n);

        const total = (typeof ia?.duration_seconds === 'number')
          ? ia.duration_seconds
          : (typeof ia?.speech_rate_analysis?.duration_seconds === 'number')
            ? ia.speech_rate_analysis.duration_seconds
            : null;
        if (!total || !isFinite(total)) return byStart;

        const minDur = 0.5;
        const segs = byStart.slice();
        let guard = 0;
        while (segs.length < n && guard < 100) {
          guard++;
          let maxIdx = 0;
          let maxDur = -1;
          for (let i = 0; i < segs.length; i++) {
            const d = segs[i].end - segs[i].start;
            if (d > maxDur) { maxDur = d; maxIdx = i; }
          }
          if (maxDur < 2 * minDur) break;
          const seg = segs[maxIdx];
          const mid = (seg.start + seg.end) / 2;
          const left = { start: seg.start, end: mid };
          const right = { start: mid, end: seg.end };
          segs.splice(maxIdx, 1, left, right);
          segs.sort((a,b) => a.start - b.start);
        }
        if (segs.length < n) {
          const step = total / n;
          const out = [];
          for (let i = 0; i < n; i++) {
            out.push({ start: Math.max(0, i * step), end: Math.min(total, (i+1)*step) });
          }
          return out;
        }
        return segs.slice(0, n);
      }
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
      // ignore
    }
    return [];
  };

  useEffect(() => {
    fetchRoles();
    fetchHealth();
  }, []);

  useEffect(() => {
    if (selectedRole || showAllCategories) {
      fetchCategories(showAllCategories ? null : selectedRole);
      setSelectedCategories([]);
    }
  }, [selectedRole, showAllCategories]);

  const fetchRoles = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/interview/roles`);
      const data = await response.json();
      setRoles(data.roles || []);
      setError(null);
    } catch (err) {
      console.error('Error fetching roles:', err);
      setError('Failed to load job roles. Please check API connection.');
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async (role: string | null) => {
    try {
      setLoading(true);
      const url = role ? `${API_BASE}/interview/categories?role=${encodeURIComponent(role)}` : `${API_BASE}/interview/categories`;
      const response = await fetch(url);
      const data = await response.json();
      setCategories(data.categories || []);
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
      const res = await fetch(`${API_BASE}/interview/health`);
      const data = await res.json();
      setHealth(data || {});
      setHealthError(null);
    } catch (e: any) {
      console.warn('Health check failed:', e?.message || e);
      setHealth(null);
      setHealthError('Unavailable');
    }
  };

  const isCategorySelected = (cat: string) => selectedCategories.includes(cat);
  const toggleCategory = (cat: string) => {
    setSelectedCategories((prev: string[]) => (
      prev.includes(cat) ? prev.filter((c: string) => c !== cat) : [...prev, cat]
    ));
  };

  const startInterview = async () => {
    if (!selectedRole || !selectedCategories || selectedCategories.length === 0) {
      setError('Please select both a role and category.');
      return;
    }

    try {
      setLoading(true);
      const params = new URLSearchParams();
      params.set('role', selectedRole);
      selectedCategories.forEach((cat: string) => params.append('categories', cat));
      params.set('shuffle', 'true');
      params.set('limit', String(MAX_QUESTIONS));
      
      const response = await fetch(`${API_BASE}/interview/questions?${params.toString()}`);
      const data = await response.json();
      
      const fetchedQuestions = data.questions || [];
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
      
      await startRecording();
      setTimeout(() => {
        readQuestion(fetchedQuestions[0]);
        setTimeout(() => {
          setQuestionStartTime(Date.now());
        }, 3000);
      }, 1000);
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
        setRecordedBlob(blob);
        stream.getTracks().forEach(track => track.stop());
        await analyzeFullInterview(blob);
      };
      
      mediaRecorder.start();
      setIsRecording(true);
      recordingStartTimeRef.current = Date.now();
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

  const readQuestion = async (question: any) => {
    if (!question) return;

    try {
      setIsReadingQuestion(true);
      
      if (audio) {
        audio.pause();
        audio.currentTime = 0;
      }

      const response = await fetch(`${API_BASE}/interview/read-question`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: question.question,
          lang: 'en',
          slow: false
        })
      });

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
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
      try {
        const synth = window.speechSynthesis;
        if (!synth) throw new Error('SpeechSynthesis not available');
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

  const analyzeFullInterview = async (audioBlob: Blob) => {
    try {
      setLoading(true);
      setSessionComplete(true);
      setShowToast(true);

      const formData = new FormData();
      formData.append('file', audioBlob, 'interview.webm');

      const response = await fetch(`${API_BASE}/interview/analyze-voice`, {
        method: 'POST',
        headers: { 'Accept': 'application/json' },
        body: formData
      });

      const data = await response.json();
      console.log('✓ Full interview analysis complete:', data);
      console.log('✓ Current allAnswers with time ranges:', allAnswersRef.current);

      const voiceAnalysis = data;
      setInterviewRecording(voiceAnalysis);
      
      const segments = voiceAnalysis?.transcript_analysis?.segments || [];
      console.log('✓ Available transcript segments:', segments);
      
      const updatedAnswersWithTranscript = (allAnswersRef.current || []).map((answer: any) => {
        if (answer.timeRange && segments.length > 0) {
          const overlappingSegments = segments.filter((seg: any) => {
            return seg.start < answer.timeRange.end && seg.end > answer.timeRange.start;
          });
          
          if (overlappingSegments.length > 0) {
            const actualTranscript = overlappingSegments
              .map((seg: any) => seg.text.trim())
              .join(' ');
            
            console.log(`✓ Extracted transcript for Q${answer.questionIndex + 1}:`, actualTranscript);
            
            return {
              ...answer,
              transcript: actualTranscript
            };
          }
        }
        
        console.warn(`⚠ No transcript found for Q${answer.questionIndex + 1}, using placeholder`);
        return answer;
      });
      
      allAnswersRef.current = updatedAnswersWithTranscript;
      setAllAnswers(updatedAnswersWithTranscript);
      console.log('✓ Updated answers with transcripts:', updatedAnswersWithTranscript);

      try {
        const evaluations = await Promise.all(
          (allAnswersRef.current || []).map(async (answer: any) => {
            try {
              const [evalResponse, aiDetectResponse] = await Promise.all([
                fetch(`${API_BASE}/interview/evaluate-answer`, {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({
                    user_answer: answer?.transcript || '',
                    expected_answer: answer?.question?.answer || '',
                    question: answer?.question?.question || ''
                  })
                }).then(r => r.json()),
                fetch(`${API_BASE}/interview/detect-ai-answer`, {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ text: answer?.transcript || '' })
                }).then(r => r.json())
              ]);
              return {
                ...answer,
                timeRange: answer.timeRange,
                evaluation: evalResponse,
                aiDetection: aiDetectResponse
              };
            } catch (err) {
              console.error('Error evaluating/detecting answer:', err);
              return {
                ...answer,
                timeRange: answer.timeRange,
                evaluation: { score: 0, feedback: { level: 'error', message: 'Evaluation failed' } },
                aiDetection: { ai_probability: null, confidence: 0, method: 'error', explanation: 'Detection failed' }
              };
            }
          })
        );
        console.log('✓ Evaluations with preserved time ranges:', evaluations);
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

  const formatTime = (seconds: number) => {
    if (typeof seconds !== 'number' || !isFinite(seconds)) return '';
    const m = Math.floor(seconds / 60);
    const s = Math.round(seconds % 60);
    return `${m.toString().padStart(2,'0')}:${s.toString().padStart(2,'0')}`;
  };

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
      const fillerBreakdown = ia?.transcript_analysis?.filler_breakdown || {};
      const apologyCount = ia?.transcript_analysis?.apology_count || 0;
      const repetitionCount = ia?.transcript_analysis?.repetition_count || 0;

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
        ${speechIntervals.map((seg: any, i: number) => `<tr><td>${i+1}</td><td>${formatTime(seg.start)}</td><td>${formatTime(seg.end)}</td></tr>`).join('')}
      </table>
      <div class="small">Intervals derived from speech activity; may not perfectly align to question boundaries.</div>
    </div>
  </div>

  ${(() => {
    const hasFillers = Object.keys(fillerBreakdown).length > 0;
    const hasNervous = Object.keys(nervousBreakdown).length > 0;
    const hasApologies = apologyCount > 0;
    const hasRepetitions = repetitionCount > 0;
    
    if (!hasFillers && !hasNervous && !hasApologies && !hasRepetitions) {
      return '';
    }
    
    return `
    <div class="card" style="margin-top:16px; background:#fff9e6; border-left: 4px solid #f59e0b;">
      <h2>🔍 Detected Speech Patterns</h2>
      ${hasFillers ? `
        <div style="margin-bottom:16px;">
          <h3 style="font-size:14px; font-weight:600; margin:8px 0;">Filler Words & Hedges:</h3>
          <div style="display:flex; flex-wrap:wrap; gap:8px;">
            ${Object.entries(fillerBreakdown).map(([word, count]) => 
              `<span style="background:#fff; padding:4px 12px; border-radius:12px; border:1px solid #fbbf24; font-size:13px;">"${word}" <strong>×${count}</strong></span>`
            ).join('')}
          </div>
        </div>
      ` : ''}
      ${hasNervous ? `
        <div style="margin-bottom:16px;">
          <h3 style="font-size:14px; font-weight:600; margin:8px 0;">Nervous Phrases:</h3>
          <div style="display:flex; flex-wrap:wrap; gap:8px;">
            ${Object.entries(nervousBreakdown).map(([phrase, count]) => 
              `<span style="background:#fff; padding:4px 12px; border-radius:12px; border:1px solid #f87171; font-size:13px; color:#991b1b;">"${phrase}" <strong>×${count}</strong></span>`
            ).join('')}
          </div>
        </div>
      ` : ''}
      ${hasApologies ? `
        <div style="margin-bottom:8px;">
          <strong>Apologies:</strong> ${apologyCount} apology word${apologyCount > 1 ? 's' : ''} detected (e.g., "sorry", "apologize")
        </div>
      ` : ''}
      ${hasRepetitions ? `
        <div>
          <strong>Repetitions:</strong> ${repetitionCount} repeated word${repetitionCount > 1 ? 's' : ''} or phrase${repetitionCount > 1 ? 's' : ''} detected
        </div>
      ` : ''}
      <div style="margin-top:12px; padding-top:12px; border-top:1px solid #fbbf24; font-size:13px; font-style:italic; color:#78350f;">
        💡 Tip: Practice replacing these with pauses or more confident language.
      </div>
    </div>
    `;
  })()}

  <div class="card" style="margin-top:16px;">
    <h2>Conversation</h2>
    <table>
      <tr><th>#</th><th>Time</th><th>Question</th><th>Answer (excerpt)</th></tr>
      ${speechIntervals.map((seg: any, i: number) => {
        const parts = asrSegments.filter((s: any) =>
          typeof s?.start === 'number' && typeof s?.end === 'number' && s?.text && s.end > seg.start && s.start < seg.end
        ).map((s: any) => s.text.trim());
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
        .sort((a: any, b: any) => b[1]-a[1])
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
      setTimeout(() => { try { win.focus(); win.print(); } catch(e){} }, 300);
    } catch (e) {
      console.error('PDF generation failed:', e);
    }
  };

  const copyTranscriptToClipboard = async (text: string) => {
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
    const answerEndTime = Date.now();
    const startOffset = questionStartTime && recordingStartTimeRef.current 
      ? (questionStartTime - recordingStartTimeRef.current) / 1000 
      : 0;
    const endOffset = recordingStartTimeRef.current 
      ? (answerEndTime - recordingStartTimeRef.current) / 1000 
      : 0;
    
    const currentAnswer = {
      questionIndex: currentQuestionIndex,
      question: currentQuestion,
      transcript: `Answer ${currentQuestionIndex + 1}`,
      timestamp: new Date().toISOString(),
      timeRange: {
        start: startOffset,
        end: endOffset
      }
    };
    
    console.log('✓ Saving answer with time range:', currentAnswer);
    
    const updatedAnswers = [...allAnswers, currentAnswer];
    setAllAnswers(updatedAnswers);
    allAnswersRef.current = updatedAnswers;
    
    if (currentQuestionIndex < questions.length - 1) {
      const nextIndex = currentQuestionIndex + 1;
      setCurrentQuestionIndex(nextIndex);
      setCurrentQuestion(questions[nextIndex]);
      
      if (audio) {
        audio.pause();
      }
      
      setTimeout(() => {
        readQuestion(questions[nextIndex]);
        setTimeout(() => {
          setQuestionStartTime(Date.now());
        }, 3000);
      }, 500);
    } else {
      stopRecording();
    }
  };

  const exitInterview = async () => {
    if (audio) {
      audio.pause();
    }

    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      setLoading(true);
      stopRecording();
      return;
    }

    if (recordedBlob) {
      setLoading(true);
      await analyzeFullInterview(recordedBlob);
      return;
    }

    const confirmExit = window.confirm('No recording captured yet. Exit without results?');
    if (confirmExit) {
      restartInterview();
    }
  };

  const restartInterview = () => {
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
              <h1>Interview Simulator</h1>
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
                  {loading ? 'Loading...' : 'Start Interview'}
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

  // Results screen
  if (sessionComplete) {
    const ia = interviewRecording || {};
    const fullTranscript = ia?.transcript_analysis?.full_transcript || ia?.transcript_analysis?.transcript_text || '';
    const segments = ia?.transcript_analysis?.segments || [];
    const speechIntervals = getApproxIntervals(ia, questions.length);
    
    const stressedProb = typeof ia?.stressed_probability === 'number' ? ia.stressed_probability * 100 : null;
    const confidence = typeof ia?.confidence === 'number' ? ia.confidence * 100 : null;
    const fillerCount = ia?.transcript_analysis?.filler_word_count || 0;
    const pauseCount = ia?.pause_analysis?.pause_count || 0;
    const wpm = ia?.speech_rate_analysis?.words_per_minute || 0;
    const nervousPhrases = ia?.transcript_analysis?.nervous_phrase_count || 0;

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

        <div className="dashboard-main results-layout">
          <aside className="dashboard-left">
            <div className="panel">
              <div className="panel-title">At a glance</div>
              <div className="stat-grid">
                <div className="stat">
                  <div className="stat-label">Stress Level</div>
                  <div className="stat-value">{ia?.stress_level || '—'}</div>
                </div>
                <div className="stat">
                  <div className="stat-label">Confidence</div>
                  <div className="stat-value">{confidence !== null ? `${confidence.toFixed(0)}%` : '—'}</div>
                </div>
                <div className="stat">
                  <div className="stat-label">Speech Rate</div>
                  <div className="stat-value">{wpm ? `${Math.round(wpm)} WPM` : '—'}</div>
                </div>
                <div className="stat">
                  <div className="stat-label">Filler Words</div>
                  <div className="stat-value">{fillerCount}</div>
                </div>
              </div>
              <button className="restart-btn" onClick={restartInterview} style={{width:'100%', marginTop: '1rem'}}>
                <RotateCcw size={16} style={{marginRight: '0.5rem'}} />
                Start New Interview
              </button>
            </div>
          </aside>

          <main className="dashboard-center">
            {loading ? (
              <div className="loading-card">
                <div className="spinner"></div>
                <p>Analyzing your performance...</p>
              </div>
            ) : (
              <>
                {/* Overall Performance Card */}
                <div className="overall-performance-card">
                  <h2>Overall Performance</h2>
                  <div className="performance-grid">
                    <div className="perf-stat">
                      <div className="perf-label">Avg Score</div>
                      <div className="perf-value">
                        {(() => {
                          const validScores = allAnswers.filter(a => a.evaluation?.score != null).map(a => a.evaluation.score);
                          const avgScore = validScores.length > 0 ? Math.round(validScores.reduce((sum, s) => sum + s, 0) / validScores.length) : 0;
                          return `${avgScore}/100`;
                        })()}
                      </div>
                    </div>
                    <div className="perf-stat">
                      <div className="perf-label">Questions</div>
                      <div className="perf-value">{allAnswers.filter(a => a.evaluation).length}/{questions.length}</div>
                    </div>
                    <div className="perf-stat">
                      <div className="perf-label">Keyword Match</div>
                      <div className="perf-value">
                        {(() => {
                          const keywordScores = allAnswers.filter(a => a.evaluation?.keyword_score != null).map(a => a.evaluation.keyword_score);
                          return keywordScores.length > 0 ? `${Math.round(keywordScores.reduce((sum, s) => sum + s, 0) / keywordScores.length)}%` : '0%';
                        })()}
                      </div>
                    </div>
                    <div className="perf-stat">
                      <div className="perf-label">Completion</div>
                      <div className="perf-value">100%</div>
                    </div>
                  </div>
                </div>

                {/* Voice Analysis Section */}
                <div className="voice-analysis-section">
                  <h2>Voice Analysis</h2>
                  
                  {/* Stress Level Indicator with Color */}
                  <div style={{ marginBottom: '1.5rem' }}>
                    <div style={{ marginBottom: '0.5rem', fontWeight: '600', color: '#374151' }}>
                      Stress Level: {ia?.stress_level || 'Unknown'}
                    </div>
                    <div style={{ 
                      display: 'inline-block',
                      padding: '0.5rem 1rem',
                      borderRadius: '8px',
                      fontWeight: 'bold',
                      fontSize: '1.1rem',
                      backgroundColor: (() => {
                        const level = ia?.stress_level?.toLowerCase() || '';
                        if (level.includes('low') || level.includes('calm')) return '#10b981';
                        if (level.includes('moderate') || level.includes('medium')) return '#f59e0b';
                        if (level.includes('high') || level.includes('stressed')) return '#ef4444';
                        return '#6b7280';
                      })(),
                      color: 'white',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                    }}>
                      {ia?.stress_level || 'Unknown'}
                    </div>
                  </div>

                  <div className="analysis-metrics">
                    <div className="metric-item">
                      <div className="metric-label">Stress Probability</div>
                      <div className="metric-value">{stressedProb !== null ? `${stressedProb.toFixed(1)}%` : 'N/A'}</div>
                    </div>
                    <div className="metric-item">
                      <div className="metric-label">Confidence</div>
                      <div className="metric-value">{confidence !== null ? `${confidence.toFixed(1)}%` : 'N/A'}</div>
                    </div>
                    <div className="metric-item">
                      <div className="metric-label">Speech Rate</div>
                      <div className="metric-value">{wpm ? `${Math.round(wpm)} WPM` : 'N/A'}</div>
                    </div>
                    <div className="metric-item">
                      <div className="metric-label">Filler Words</div>
                      <div className="metric-value">{fillerCount}</div>
                    </div>
                    <div className="metric-item">
                      <div className="metric-label">Pauses</div>
                      <div className="metric-value">{pauseCount}</div>
                    </div>
                    <div className="metric-item">
                      <div className="metric-label">Nervous Phrases</div>
                      <div className="metric-value">{nervousPhrases}</div>
                    </div>
                  </div>

                  {/* Detected Speech Patterns Breakdown */}
                  {(() => {
                    const fillerBreakdown = ia?.transcript_analysis?.filler_breakdown || {};
                    const nervousBreakdown = ia?.transcript_analysis?.nervous_phrase_breakdown || {};
                    const apologyCount = ia?.transcript_analysis?.apology_count || 0;
                    const repetitionCount = ia?.transcript_analysis?.repetition_count || 0;
                    
                    const hasFillers = Object.keys(fillerBreakdown).length > 0;
                    const hasNervous = Object.keys(nervousBreakdown).length > 0;
                    const hasApologies = apologyCount > 0;
                    const hasRepetitions = repetitionCount > 0;
                    
                    if (!hasFillers && !hasNervous && !hasApologies && !hasRepetitions) {
                      return null;
                    }
                    
                    return (
                      <div style={{ 
                        marginTop: '1.5rem',
                        padding: '1rem',
                        background: '#fef3c7',
                        borderRadius: '8px',
                        borderLeft: '4px solid #f59e0b'
                      }}>
                        <h3 style={{ 
                          fontSize: '1.1rem',
                          fontWeight: '600',
                          marginBottom: '0.75rem',
                          color: '#92400e'
                        }}>
                          🔍 What We Detected in Your Speech
                        </h3>
                        
                        {/* Filler Words */}
                        {hasFillers && (
                          <div style={{ marginBottom: '1rem' }}>
                            <div style={{ 
                              fontWeight: '600',
                              color: '#78350f',
                              marginBottom: '0.5rem'
                            }}>
                              Filler Words & Hedges:
                            </div>
                            <div style={{ 
                              display: 'flex',
                              flexWrap: 'wrap',
                              gap: '0.5rem'
                            }}>
                              {Object.entries(fillerBreakdown).map(([word, count]: [string, any]) => (
                                <span key={word} style={{
                                  background: '#fff',
                                  padding: '0.25rem 0.75rem',
                                  borderRadius: '12px',
                                  fontSize: '0.875rem',
                                  border: '1px solid #fbbf24',
                                  color: '#92400e'
                                }}>
                                  "{word}" <strong>×{count}</strong>
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {/* Nervous Phrases */}
                        {hasNervous && (
                          <div style={{ marginBottom: '1rem' }}>
                            <div style={{ 
                              fontWeight: '600',
                              color: '#78350f',
                              marginBottom: '0.5rem'
                            }}>
                              Nervous Phrases:
                            </div>
                            <div style={{ 
                              display: 'flex',
                              flexWrap: 'wrap',
                              gap: '0.5rem'
                            }}>
                              {Object.entries(nervousBreakdown).map(([phrase, count]: [string, any]) => (
                                <span key={phrase} style={{
                                  background: '#fff',
                                  padding: '0.25rem 0.75rem',
                                  borderRadius: '12px',
                                  fontSize: '0.875rem',
                                  border: '1px solid #f87171',
                                  color: '#991b1b'
                                }}>
                                  "{phrase}" <strong>×{count}</strong>
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {/* Apologies */}
                        {hasApologies && (
                          <div style={{ marginBottom: '0.5rem' }}>
                            <span style={{ 
                              fontWeight: '600',
                              color: '#78350f'
                            }}>
                              Apologies:
                            </span>{' '}
                            <span style={{ color: '#92400e' }}>
                              {apologyCount} apology word{apologyCount > 1 ? 's' : ''} detected (e.g., "sorry", "apologize")
                            </span>
                          </div>
                        )}
                        
                        {/* Repetitions */}
                        {hasRepetitions && (
                          <div>
                            <span style={{ 
                              fontWeight: '600',
                              color: '#78350f'
                            }}>
                              Repetitions:
                            </span>{' '}
                            <span style={{ color: '#92400e' }}>
                              {repetitionCount} repeated word{repetitionCount > 1 ? 's' : ''} or phrase{repetitionCount > 1 ? 's' : ''} detected
                            </span>
                          </div>
                        )}
                        
                        <div style={{
                          marginTop: '0.75rem',
                          paddingTop: '0.75rem',
                          borderTop: '1px solid #fbbf24',
                          fontSize: '0.875rem',
                          color: '#78350f',
                          fontStyle: 'italic'
                        }}>
                          💡 Tip: Practice replacing these with pauses or more confident language.
                        </div>
                      </div>
                    );
                  })()}

                  {/* Voice Analysis Tips Section */}
                  <div style={{ 
                    marginTop: '1.5rem',
                    padding: '1rem',
                    background: '#f0fdf4',
                    borderRadius: '8px',
                    borderLeft: '4px solid #10b981'
                  }}>
                    <h3 style={{ 
                      fontSize: '1.1rem',
                      fontWeight: '600',
                      marginBottom: '0.75rem',
                      color: '#065f46'
                    }}>
                      💡 Improvement Tips
                    </h3>
                    <ul style={{ 
                      margin: 0,
                      paddingLeft: '1.5rem',
                      color: '#064e3b',
                      lineHeight: '1.8'
                    }}>
                      {(() => {
                        const tips = [];
                        
                        // Stress-based tips
                        if (stressedProb !== null && stressedProb >= 60) {
                          tips.push('Before answering, take a deep breath and pause for 1–2 seconds to lower stress.');
                        }
                        
                        // Filler words tips
                        if (fillerCount > 10) {
                          tips.push('Replace filler words with short pauses. Practice mock answers to reduce "um/uh/like".');
                        } else if (fillerCount > 4) {
                          tips.push('Some filler words present. Aim for shorter sentences to reduce them.');
                        }
                        
                        // Speech rate tips
                        if (wpm && wpm > 180) {
                          tips.push('You spoke quite fast. Slowing down to 140–160 WPM can improve clarity and poise.');
                        } else if (wpm && wpm < 110) {
                          tips.push('Your pace is slow. Slightly increasing to 130–160 WPM can convey more confidence.');
                        }
                        
                        // Pause tips
                        if (pauseCount === 0) {
                          tips.push('Consider adding brief pauses to structure your answer and give yourself time to think.');
                        } else if (pauseCount > 8) {
                          tips.push('Many pauses detected. Try to maintain a steady flow with fewer breaks.');
                        }
                        
                        // Nervous phrases tips
                        if (nervousPhrases > 0) {
                          tips.push('Swap nervous phrases with confident alternatives (e.g., "I believe..." instead of "I\'m not sure but...").');
                        }
                        
                        // Confidence tips
                        if (confidence !== null && confidence < 50) {
                          tips.push('Practice your responses to build confidence. Speaking clearly and at a steady pace helps.');
                        }
                        
                        // Default tips if none apply
                        if (tips.length === 0) {
                          tips.push('Great job! Your voice analysis shows good control. Keep maintaining steady pace and clear articulation.');
                          tips.push('Continue practicing to maintain your confident delivery style.');
                        }
                        
                        return tips.map((tip, i) => <li key={i}>{tip}</li>);
                      })()}
                    </ul>
                  </div>
                </div>

                {/* Conversation Timeline */}
                <div className="questions-card">
                  <div className="transcript-header">
                    <h3>Conversation Timeline</h3>
                    <div>
                      <button className="copy-btn" onClick={() => copyTranscriptToClipboard(fullTranscript)} disabled={!fullTranscript}>
                        {transcriptCopied ? 'Copied ✓' : 'Copy Transcript'}
                      </button>
                      <button className="copy-btn" onClick={downloadPdfReport} disabled={!interviewRecording} style={{ marginLeft: 8 }}>
                        <Download size={16} style={{marginRight: '0.25rem'}} />
                        Download PDF
                      </button>
                    </div>
                  </div>
                  <ol className="question-list">
                    {speechIntervals.map((seg: any, i: number) => {
                      const parts = segments.filter((s: any) => {
                        if (typeof s?.start !== 'number' || typeof s?.end !== 'number' || !s?.text) return false;
                        return s.end > seg.start && s.start < seg.end;
                      }).map((s: any) => s.text.trim());
                      
                      let answerText = parts.length > 0 ? parts.join(' ') : '';
                      
                      if (!answerText && segments.length > 0) {
                        const segmentsPerQuestion = Math.ceil(segments.length / questions.length);
                        const startIdx = i * segmentsPerQuestion;
                        const endIdx = Math.min((i + 1) * segmentsPerQuestion, segments.length);
                        const positionParts = segments.slice(startIdx, endIdx)
                          .filter((s: any) => s?.text)
                          .map((s: any) => s.text.trim());
                        answerText = positionParts.join(' ');
                      }
                      
                      return (
                        <li key={i}>
                          <div><strong>[{formatTime(seg.start)}–{formatTime(seg.end)}]</strong> {questions[i]?.question || ''}</div>
                          <div className="subtext" style={{marginTop:'6px'}}><em>Answer:</em> {answerText || '—'}</div>
                        </li>
                      );
                    })}
                  </ol>
                </div>

                {/* Individual Question Results */}
                <div className="question-results">
                  <div className="section-header">
                    <div className="header-content">
                      <h2>Interview Results</h2>
                      <p className="header-subtitle">Detailed analysis of your responses</p>
                    </div>
                  </div>

                  <div className="results-list">
                    {allAnswers.map((answer, idx) => {
                      const matchScore = answer.evaluation?.keyword_score || 0;
                      const aiGeneratedNum = answer.aiDetection ? parseFloat((answer.aiDetection.ai_probability * 100).toFixed(0)) : 0;
                      const overallScore = answer.evaluation?.score || 0;
                      
                      const expectedAnswer = answer.question?.answer || '';
                      const keyPoints = expectedAnswer.split('.').filter((s: string) => s.trim().length > 20).slice(0, 3);
                      
                      return (
                        <div key={idx} className="answer-result-card">
                          <div className="result-header">
                            <h3>Question {idx + 1}</h3>
                            {answer.evaluation && (
                              <div className="score-badge" style={{ 
                                backgroundColor: overallScore >= 80 ? '#10b981' : overallScore >= 60 ? '#f59e0b' : overallScore >= 40 ? '#f97316' : '#ef4444'
                              }}>
                                {overallScore}/100
                              </div>
                            )}
                          </div>
                          
                          <p className="result-question"><strong>Q:</strong> {answer.question.question}</p>
                          
                          {answer.evaluation && (
                            <div className="evaluation-summary">
                              <div className="simple-metrics" style={{ 
                                display: 'flex', 
                                gap: '1rem', 
                                marginBottom: '1rem',
                                flexWrap: 'wrap'
                              }}>
                                <div style={{ 
                                  flex: '1', 
                                  minWidth: '120px',
                                  padding: '0.75rem', 
                                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                  borderRadius: '8px',
                                  color: 'white',
                                  textAlign: 'center'
                                }}>
                                  <div style={{ fontSize: '0.875rem', opacity: 0.9 }}>Overall Score</div>
                                  <div style={{ fontSize: '1.5rem', fontWeight: 'bold', marginTop: '0.25rem' }}>{overallScore}/100</div>
                                </div>
                                
                                <div style={{ 
                                  flex: '1', 
                                  minWidth: '120px',
                                  padding: '0.75rem', 
                                  background: '#f3f4f6',
                                  borderRadius: '8px',
                                  textAlign: 'center'
                                }}>
                                  <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>Keyword Match</div>
                                  <div style={{ fontSize: '1.5rem', fontWeight: 'bold', marginTop: '0.25rem', color: '#111827' }}>{matchScore}%</div>
                                </div>
                                
                                <div style={{ 
                                  flex: '1', 
                                  minWidth: '120px',
                                  padding: '0.75rem', 
                                  background: aiGeneratedNum > 50 ? '#fee2e2' : '#f0fdf4',
                                  borderRadius: '8px',
                                  textAlign: 'center'
                                }}>
                                  <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>AI Generated</div>
                                  <div style={{ 
                                    fontSize: '1.5rem', 
                                    fontWeight: 'bold', 
                                    marginTop: '0.25rem',
                                    color: aiGeneratedNum > 50 ? '#dc2626' : '#16a34a'
                                  }}>{aiGeneratedNum}%</div>
                                </div>
                              </div>

                              {answer.evaluation.feedback && (
                                <div className="feedback-section" style={{
                                  padding: '1rem',
                                  background: '#f9fafb',
                                  borderRadius: '8px',
                                  marginBottom: '1rem'
                                }}>
                                  <div style={{ fontWeight: '600', marginBottom: '0.5rem', color: '#374151' }}>Feedback</div>
                                  <p style={{ color: '#6b7280', lineHeight: '1.6' }}>{answer.evaluation.feedback.message}</p>
                                </div>
                              )}

                              {keyPoints.length > 0 && (
                                <div className="key-points-section" style={{
                                  padding: '1rem',
                                  background: '#fefce8',
                                  borderRadius: '8px',
                                  borderLeft: '4px solid #eab308'
                                }}>
                                  <div style={{ fontWeight: '600', marginBottom: '0.5rem', color: '#854d0e' }}>Key Points to Cover</div>
                                  <ul style={{ margin: 0, paddingLeft: '1.5rem', color: '#713f12' }}>
                                    {keyPoints.map((point: string, i: number) => (
                                      <li key={i} style={{ marginBottom: '0.25rem' }}>{point.trim()}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>
                          )}

                          <div className="answer-transcript" style={{
                            marginTop: '1rem',
                            padding: '1rem',
                            background: '#ffffff',
                            border: '1px solid #e5e7eb',
                            borderRadius: '8px'
                          }}>
                            <div style={{ fontWeight: '600', marginBottom: '0.5rem', color: '#374151' }}>Your Answer</div>
                            <p style={{ color: '#6b7280', lineHeight: '1.6', fontStyle: answer.transcript.startsWith('Answer') ? 'italic' : 'normal' }}>
                              {answer.transcript || 'No transcript available'}
                            </p>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </>
            )}
          </main>

          <aside className="dashboard-right">
            <div className="panel">
              <div className="panel-title">Session Summary</div>
              <div className="session-summary">
                <div><strong>Role:</strong> {selectedRole}</div>
                <div><strong>Categories:</strong> {selectedCategories.join(', ')}</div>
                <div><strong>Questions:</strong> {questions.length}</div>
                <div><strong>Duration:</strong> {ia?.duration_seconds ? `${Math.round(ia.duration_seconds)}s` : 'N/A'}</div>
              </div>
            </div>
          </aside>
        </div>
      </div>
    );
  }

  // Active interview session screen
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

export default InterviewPracticeIntegrated;
