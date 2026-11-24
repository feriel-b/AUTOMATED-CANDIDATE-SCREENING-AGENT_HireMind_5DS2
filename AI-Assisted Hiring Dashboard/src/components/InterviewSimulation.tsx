import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Progress } from "./ui/progress";
import { Textarea } from "./ui/textarea";
import { 
  Play, 
  Pause,
  RotateCcw,
  Mic,
  Video,
  Brain,
  Sparkles,
  TrendingUp,
  TrendingDown,
  CheckCircle2,
  AlertCircle,
  Award,
  Lightbulb,
  Volume2,
  Smile,
  MessageSquare
} from "lucide-react";
import { toast } from "sonner@2.0.3";

export function InterviewSimulation() {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [answer, setAnswer] = useState("");
  const [showFeedback, setShowFeedback] = useState(false);
  const [interviewComplete, setInterviewComplete] = useState(false);

  const questions = [
    {
      id: 1,
      question: "Tell me about yourself and your background in software engineering.",
      category: "Introduction",
      tips: "Keep it concise (2-3 minutes), focus on relevant experience, and end with why you're interested in this opportunity."
    },
    {
      id: 2,
      question: "Describe a challenging technical problem you solved recently. What was your approach?",
      category: "Technical",
      tips: "Use the STAR method: Situation, Task, Action, Result. Be specific about your technical decisions."
    },
    {
      id: 3,
      question: "How do you handle disagreements with team members about technical decisions?",
      category: "Behavioral",
      tips: "Show emotional intelligence, collaboration skills, and ability to compromise while maintaining technical standards."
    },
    {
      id: 4,
      question: "Where do you see yourself in 5 years?",
      category: "Career Goals",
      tips: "Show ambition while demonstrating commitment. Align your goals with potential growth at the company."
    }
  ];

  const currentQ = questions[currentQuestion];

  const feedback = {
    nlpAnalysis: {
      clarity: 85,
      relevance: 78,
      structure: 82,
      techDepth: 88
    },
    voiceAnalysis: {
      confidence: 76,
      pace: 82,
      tone: 88,
      stressLevel: 65
    },
    facialAnalysis: {
      engagement: 91,
      eyeContact: 85,
      expressiveness: 79,
      nervousness: 42
    },
    overallScore: 83,
    strengths: [
      "Excellent eye contact maintained throughout the answer",
      "Good technical depth in explaining your solution",
      "Confident tone and appropriate pacing",
      "Strong structure following the STAR method"
    ],
    weaknesses: [
      "Could reduce filler words ('um', 'like') for better clarity",
      "Answer slightly exceeded recommended 2-3 minute timeframe",
      "Consider providing more specific metrics in your examples"
    ],
    tips: [
      "Practice your opening statement to reduce initial nervousness",
      "Take a brief pause before answering to collect your thoughts",
      "Use concrete numbers to quantify your achievements (e.g., '30% performance improvement')"
    ]
  };

  const handleStartRecording = () => {
    setIsRecording(true);
    setIsPaused(false);
    toast.success("Recording started. AI is analyzing your response...");
  };

  const handlePauseRecording = () => {
    setIsPaused(!isPaused);
  };

  const handleStopAndAnalyze = () => {
    setIsRecording(false);
    setShowFeedback(true);
    toast.success("Analysis complete! Review your feedback below.");
  };

  const handleNextQuestion = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setAnswer("");
      setShowFeedback(false);
      setIsRecording(false);
    } else {
      setInterviewComplete(true);
    }
  };

  const handleRestartInterview = () => {
    setCurrentQuestion(0);
    setAnswer("");
    setShowFeedback(false);
    setIsRecording(false);
    setInterviewComplete(false);
  };

  if (interviewComplete) {
    return (
      <div className="space-y-6">
        <div>
          <h2>Interview Practice Complete! 🎉</h2>
          <p className="text-gray-600">Here's your comprehensive performance summary</p>
        </div>

        {/* Overall Performance */}
        <Card className="border-2 border-green-200 bg-gradient-to-br from-green-50 to-emerald-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Award className="h-6 w-6 text-green-600" />
              Overall Performance
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-6">
              <div className="text-center">
                <div className="text-6xl text-green-600 mb-2">{feedback.overallScore}%</div>
                <Badge className="bg-green-600 text-lg px-4 py-1">Great Job!</Badge>
              </div>
              <div className="flex-1 space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Content Quality</span>
                    <span>85%</span>
                  </div>
                  <Progress value={85} className="h-3" />
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Communication Skills</span>
                    <span>82%</span>
                  </div>
                  <Progress value={82} className="h-3" />
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Confidence & Presence</span>
                    <span>81%</span>
                  </div>
                  <Progress value={81} className="h-3" />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Detailed Breakdown */}
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm flex items-center gap-2">
                <MessageSquare className="h-4 w-4 text-blue-600" />
                Content Analysis (NLP)
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Clarity</span>
                  <span>{feedback.nlpAnalysis.clarity}%</span>
                </div>
                <Progress value={feedback.nlpAnalysis.clarity} className="h-2" />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Relevance</span>
                  <span>{feedback.nlpAnalysis.relevance}%</span>
                </div>
                <Progress value={feedback.nlpAnalysis.relevance} className="h-2" />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Structure</span>
                  <span>{feedback.nlpAnalysis.structure}%</span>
                </div>
                <Progress value={feedback.nlpAnalysis.structure} className="h-2" />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Technical Depth</span>
                  <span>{feedback.nlpAnalysis.techDepth}%</span>
                </div>
                <Progress value={feedback.nlpAnalysis.techDepth} className="h-2" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-sm flex items-center gap-2">
                <Volume2 className="h-4 w-4 text-purple-600" />
                Voice Analysis
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Confidence</span>
                  <span>{feedback.voiceAnalysis.confidence}%</span>
                </div>
                <Progress value={feedback.voiceAnalysis.confidence} className="h-2" />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Pace</span>
                  <span>{feedback.voiceAnalysis.pace}%</span>
                </div>
                <Progress value={feedback.voiceAnalysis.pace} className="h-2" />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Tone</span>
                  <span>{feedback.voiceAnalysis.tone}%</span>
                </div>
                <Progress value={feedback.voiceAnalysis.tone} className="h-2" />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Stress Level</span>
                  <span className="text-green-600">Low ({feedback.voiceAnalysis.stressLevel}%)</span>
                </div>
                <Progress value={100 - feedback.voiceAnalysis.stressLevel} className="h-2" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-sm flex items-center gap-2">
                <Smile className="h-4 w-4 text-orange-600" />
                Facial Analysis
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Engagement</span>
                  <span>{feedback.facialAnalysis.engagement}%</span>
                </div>
                <Progress value={feedback.facialAnalysis.engagement} className="h-2" />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Eye Contact</span>
                  <span>{feedback.facialAnalysis.eyeContact}%</span>
                </div>
                <Progress value={feedback.facialAnalysis.eyeContact} className="h-2" />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Expressiveness</span>
                  <span>{feedback.facialAnalysis.expressiveness}%</span>
                </div>
                <Progress value={feedback.facialAnalysis.expressiveness} className="h-2" />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Nervousness</span>
                  <span className="text-green-600">Low ({feedback.facialAnalysis.nervousness}%)</span>
                </div>
                <Progress value={100 - feedback.facialAnalysis.nervousness} className="h-2" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Comprehensive Feedback */}
        <div className="grid gap-4 md:grid-cols-2">
          <Card className="bg-green-50 border-2 border-green-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-green-900">
                <TrendingUp className="h-5 w-5" />
                Your Strengths
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {feedback.strengths.map((strength, i) => (
                  <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-600 flex-shrink-0 mt-0.5" />
                    {strength}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          <Card className="bg-orange-50 border-2 border-orange-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-orange-900">
                <TrendingDown className="h-5 w-5" />
                Areas to Improve
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {feedback.weaknesses.map((weakness, i) => (
                  <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                    <AlertCircle className="h-4 w-4 text-orange-600 flex-shrink-0 mt-0.5" />
                    {weakness}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>

        {/* AI Tips */}
        <Card className="bg-gradient-to-r from-purple-50 to-blue-50 border-2 border-purple-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lightbulb className="h-5 w-5 text-purple-600" />
              AI-Powered Tips for Next Time
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {feedback.tips.map((tip, i) => (
                <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                  <Sparkles className="h-4 w-4 text-purple-600 flex-shrink-0 mt-0.5" />
                  {tip}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        <div className="flex gap-3">
          <Button onClick={handleRestartInterview} size="lg" className="gap-2">
            <RotateCcw className="h-5 w-5" />
            Practice Again
          </Button>
          <Button variant="outline" size="lg">
            Save Results
          </Button>
          <Button variant="outline" size="lg">
            Share Progress
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2>AI Interview Practice</h2>
        <p className="text-gray-600">Practice with AI-powered real-time feedback on your performance</p>
      </div>

      {/* Progress */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm">Question {currentQuestion + 1} of {questions.length}</span>
            <span className="text-sm text-gray-600">{Math.round(((currentQuestion + 1) / questions.length) * 100)}% Complete</span>
          </div>
          <Progress value={((currentQuestion + 1) / questions.length) * 100} className="h-3" />
        </CardContent>
      </Card>

      {/* Current Question */}
      <Card className="border-2 border-blue-200">
        <CardHeader>
          <div className="flex items-center justify-between">
            <Badge>{currentQ.category}</Badge>
            <span className="text-sm text-gray-600">Question {currentQuestion + 1}</span>
          </div>
          <CardTitle className="text-2xl mt-4">{currentQ.question}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start gap-2">
              <Lightbulb className="h-4 w-4 text-blue-600 mt-0.5" />
              <div>
                <div className="text-sm text-blue-900 mb-1">Interview Tip</div>
                <p className="text-sm text-gray-700">{currentQ.tips}</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Recording Interface */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-purple-600" />
            AI Analysis Active
          </CardTitle>
          <CardDescription>
            Recording video and audio for multi-modal analysis
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Video Preview Placeholder */}
          <div className="aspect-video bg-gradient-to-br from-gray-900 to-gray-800 rounded-lg flex items-center justify-center relative overflow-hidden">
            {isRecording ? (
              <div className="text-center">
                <Video className="h-16 w-16 text-white mb-4 mx-auto animate-pulse" />
                <p className="text-white">Camera Active - AI Analyzing...</p>
                <div className="flex gap-2 justify-center mt-4">
                  <Badge className="bg-red-600 animate-pulse">● REC</Badge>
                  <Badge className="bg-green-600">Audio Active</Badge>
                  <Badge className="bg-blue-600">Facial Analysis</Badge>
                </div>
              </div>
            ) : (
              <div className="text-center text-white">
                <Video className="h-16 w-16 mb-4 mx-auto opacity-50" />
                <p className="opacity-50">Click Start to begin recording</p>
              </div>
            )}
          </div>

          {/* Text Answer (Optional) */}
          <div>
            <Label className="text-sm mb-2 block">Or Type Your Answer (Optional)</Label>
            <Textarea
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder="Type your answer here for text-based analysis..."
              rows={4}
              disabled={isRecording}
            />
          </div>

          {/* Recording Controls */}
          <div className="flex gap-2 justify-center">
            {!isRecording ? (
              <Button onClick={handleStartRecording} size="lg" className="gap-2">
                <Mic className="h-5 w-5" />
                Start Recording
              </Button>
            ) : (
              <>
                <Button onClick={handlePauseRecording} variant="outline" size="lg" className="gap-2">
                  {isPaused ? <Play className="h-5 w-5" /> : <Pause className="h-5 w-5" />}
                  {isPaused ? "Resume" : "Pause"}
                </Button>
                <Button onClick={handleStopAndAnalyze} size="lg" className="gap-2 bg-red-600 hover:bg-red-700">
                  Stop & Analyze
                </Button>
              </>
            )}
          </div>

          {/* Real-time Indicators */}
          {isRecording && !isPaused && (
            <div className="grid grid-cols-3 gap-3">
              <Card className="bg-green-50">
                <CardContent className="pt-4 pb-3 text-center">
                  <div className="text-2xl text-green-600">85%</div>
                  <div className="text-xs text-gray-600">Voice Clarity</div>
                </CardContent>
              </Card>
              <Card className="bg-blue-50">
                <CardContent className="pt-4 pb-3 text-center">
                  <div className="text-2xl text-blue-600">91%</div>
                  <div className="text-xs text-gray-600">Eye Contact</div>
                </CardContent>
              </Card>
              <Card className="bg-purple-50">
                <CardContent className="pt-4 pb-3 text-center">
                  <div className="text-2xl text-purple-600">Good</div>
                  <div className="text-xs text-gray-600">Confidence</div>
                </CardContent>
              </Card>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Feedback Card (After Analysis) */}
      {showFeedback && (
        <>
          <Card className="border-2 border-green-200 bg-green-50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-green-600" />
                AI Feedback for This Answer
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="text-center py-4">
                <div className="text-5xl text-green-600 mb-2">{feedback.overallScore}%</div>
                <Badge className="bg-green-600">Excellent Response!</Badge>
              </div>

              <div className="grid md:grid-cols-3 gap-4">
                <div>
                  <div className="text-sm text-gray-600 mb-2">Content Quality</div>
                  <Progress value={feedback.nlpAnalysis.clarity} className="h-2 mb-1" />
                  <div className="text-xs text-gray-600">{feedback.nlpAnalysis.clarity}%</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600 mb-2">Voice Confidence</div>
                  <Progress value={feedback.voiceAnalysis.confidence} className="h-2 mb-1" />
                  <div className="text-xs text-gray-600">{feedback.voiceAnalysis.confidence}%</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600 mb-2">Body Language</div>
                  <Progress value={feedback.facialAnalysis.engagement} className="h-2 mb-1" />
                  <div className="text-xs text-gray-600">{feedback.facialAnalysis.engagement}%</div>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div className="bg-white rounded-lg p-3 border border-green-200">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    <span className="text-sm">What Went Well</span>
                  </div>
                  <ul className="space-y-1">
                    {feedback.strengths.slice(0, 2).map((strength, i) => (
                      <li key={i} className="text-xs text-gray-700">• {strength}</li>
                    ))}
                  </ul>
                </div>
                <div className="bg-white rounded-lg p-3 border border-orange-200">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertCircle className="h-4 w-4 text-orange-600" />
                    <span className="text-sm">To Improve</span>
                  </div>
                  <ul className="space-y-1">
                    {feedback.weaknesses.slice(0, 2).map((weakness, i) => (
                      <li key={i} className="text-xs text-gray-700">• {weakness}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="flex gap-3">
            <Button onClick={handleNextQuestion} size="lg" className="gap-2">
              {currentQuestion < questions.length - 1 ? "Next Question" : "Complete Interview"}
              →
            </Button>
            <Button variant="outline" size="lg" onClick={() => {
              setShowFeedback(false);
              setAnswer("");
              setIsRecording(false);
            }}>
              Try Again
            </Button>
          </div>
        </>
      )}
    </div>
  );
}

function Label({ children, className }: { children: React.ReactNode; className?: string }) {
  return <label className={className}>{children}</label>;
}
