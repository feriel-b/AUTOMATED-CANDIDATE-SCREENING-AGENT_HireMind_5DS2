import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Avatar, AvatarFallback } from "./ui/avatar";
import { Textarea } from "./ui/textarea";
import { Progress } from "./ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { 
  Brain, 
  Mic, 
  FileText, 
  TrendingUp, 
  TrendingDown,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  Volume2,
  Clock,
  Target,
  MessageSquare
} from "lucide-react";
import { toast } from "sonner@2.0.3";

interface EvaluationSupportProps {
  candidateId: string;
  onBack: () => void;
  onCompleteEvaluation: () => void;
}

export function EvaluationSupport({ candidateId, onBack, onCompleteEvaluation }: EvaluationSupportProps) {
  const [interviewNotes, setInterviewNotes] = useState("");
  const [ratings, setRatings] = useState({
    technical: 0,
    communication: 0,
    problemSolving: 0,
    cultureFit: 0
  });

  const candidate = {
    name: "Sarah Johnson",
    currentRole: "Senior Frontend Engineer",
    interviewDate: "Oct 15, 2025",
    interviewDuration: "52 minutes"
  };

  // Simulated AI analysis of interview
  const aiAnalysis = {
    overallConfidence: 88,
    toneAnalysis: {
      positive: 72,
      confident: 81,
      professional: 94,
      enthusiastic: 68
    },
    communicationMetrics: {
      clarity: 89,
      conciseness: 76,
      activeListening: 92,
      thoughtfulness: 85
    },
    keyInsights: [
      "Candidate demonstrated strong technical depth when discussing React architecture",
      "Showed excellent self-awareness when discussing areas for growth",
      "Communication style is clear and well-structured, indicating strong presentation skills",
      "Displayed genuine enthusiasm about the role and company mission"
    ],
    concerns: [
      "Slightly hesitant when discussing backend scalability - may indicate limited experience",
      "Could benefit from more specific examples of leadership impact"
    ],
    strengths: [
      "Exceptional ability to explain complex technical concepts clearly",
      "Strong problem-solving methodology with structured approach",
      "Demonstrated cultural alignment through examples and values discussion",
      "Proactive in asking thoughtful questions about team dynamics"
    ],
    transcriptHighlights: [
      {
        question: "Tell me about a time you led a project",
        response: "I led the redesign of our component library... achieved 40% reduction in bundle size... collaborated with 5 teams...",
        analysis: "Strong quantifiable impact, demonstrates leadership and cross-functional collaboration",
        sentiment: "positive"
      },
      {
        question: "How do you handle technical disagreements?",
        response: "I believe in data-driven decisions... created a POC to demonstrate... team adopted approach unanimously...",
        analysis: "Shows maturity and collaborative problem-solving. Excellent conflict resolution skills.",
        sentiment: "positive"
      },
      {
        question: "What's your experience with backend systems?",
        response: "I've worked primarily on frontend but have integrated with various APIs... interested in learning more...",
        analysis: "Honest about limitations. Shows growth mindset but confirms limited backend depth.",
        sentiment: "neutral"
      }
    ]
  };

  const handleSaveEvaluation = () => {
    if (!interviewNotes.trim()) {
      toast.error("Please add your interview notes before saving");
      return;
    }
    toast.success("Evaluation saved successfully");
  };

  const handleSubmitToDecisionDashboard = () => {
    if (!interviewNotes.trim()) {
      toast.error("Please complete the evaluation before submitting");
      return;
    }
    onCompleteEvaluation();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Button variant="ghost" onClick={onBack} className="mb-2">
            ← Back to Interview Assistant
          </Button>
          <h2>Interview Evaluation</h2>
          <p className="text-gray-600">AI-powered analysis and evaluation support</p>
        </div>
      </div>

      {/* Candidate Info */}
      <Card className="border-2 border-indigo-200">
        <CardContent className="pt-6">
          <div className="flex items-center gap-4">
            <Avatar className="h-12 w-12">
              <AvatarFallback className="bg-indigo-100 text-indigo-600">
                SJ
              </AvatarFallback>
            </Avatar>
            <div className="flex-1">
              <h3>{candidate.name}</h3>
              <p className="text-sm text-gray-600">{candidate.currentRole}</p>
            </div>
            <div className="flex gap-4 text-sm text-gray-600">
              <div className="flex items-center gap-1">
                <Clock className="h-4 w-4" />
                {candidate.interviewDate}
              </div>
              <div className="flex items-center gap-1">
                <Mic className="h-4 w-4" />
                {candidate.interviewDuration}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* AI Overall Assessment */}
      <Card className="border-2 border-purple-200 bg-gradient-to-r from-purple-50 to-indigo-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-purple-600" />
            AI Overall Assessment
          </CardTitle>
          <CardDescription>
            Automated analysis based on interview audio and conversation patterns
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-6 mb-6">
            <div className="text-center">
              <div className="text-5xl text-purple-600 mb-1">{aiAnalysis.overallConfidence}%</div>
              <div className="text-sm text-gray-600">Overall Confidence</div>
              <Badge className="mt-2 bg-purple-600">Strong Candidate</Badge>
            </div>
            <div className="flex-1 grid grid-cols-2 gap-4">
              <div className="bg-white rounded-lg p-3 border border-purple-200">
                <div className="text-xs text-gray-600 mb-1">Tone: Confident</div>
                <Progress value={aiAnalysis.toneAnalysis.confident} className="h-2 mb-1" />
                <div className="text-sm">{aiAnalysis.toneAnalysis.confident}%</div>
              </div>
              <div className="bg-white rounded-lg p-3 border border-purple-200">
                <div className="text-xs text-gray-600 mb-1">Tone: Professional</div>
                <Progress value={aiAnalysis.toneAnalysis.professional} className="h-2 mb-1" />
                <div className="text-sm">{aiAnalysis.toneAnalysis.professional}%</div>
              </div>
              <div className="bg-white rounded-lg p-3 border border-purple-200">
                <div className="text-xs text-gray-600 mb-1">Clarity</div>
                <Progress value={aiAnalysis.communicationMetrics.clarity} className="h-2 mb-1" />
                <div className="text-sm">{aiAnalysis.communicationMetrics.clarity}%</div>
              </div>
              <div className="bg-white rounded-lg p-3 border border-purple-200">
                <div className="text-xs text-gray-600 mb-1">Active Listening</div>
                <Progress value={aiAnalysis.communicationMetrics.activeListening} className="h-2 mb-1" />
                <div className="text-sm">{aiAnalysis.communicationMetrics.activeListening}%</div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-3">
                <CheckCircle2 className="h-5 w-5 text-green-600" />
                <span className="text-green-900">AI-Detected Strengths</span>
              </div>
              <ul className="space-y-2">
                {aiAnalysis.strengths.map((strength, i) => (
                  <li key={i} className="text-sm text-gray-700 flex gap-2">
                    <TrendingUp className="h-4 w-4 text-green-600 flex-shrink-0 mt-0.5" />
                    {strength}
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-3">
                <AlertTriangle className="h-5 w-5 text-yellow-600" />
                <span className="text-yellow-900">Areas of Concern</span>
              </div>
              <ul className="space-y-2">
                {aiAnalysis.concerns.map((concern, i) => (
                  <li key={i} className="text-sm text-gray-700 flex gap-2">
                    <TrendingDown className="h-4 w-4 text-yellow-600 flex-shrink-0 mt-0.5" />
                    {concern}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Detailed Analysis Tabs */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-indigo-600" />
            Detailed AI Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="highlights" className="space-y-4">
            <TabsList>
              <TabsTrigger value="highlights">Key Highlights</TabsTrigger>
              <TabsTrigger value="tone">Tone & Sentiment</TabsTrigger>
              <TabsTrigger value="communication">Communication</TabsTrigger>
            </TabsList>

            <TabsContent value="highlights" className="space-y-4">
              <div className="space-y-4">
                {aiAnalysis.transcriptHighlights.map((highlight, i) => (
                  <Card key={i} className={`border-l-4 ${
                    highlight.sentiment === "positive" ? "border-l-green-500 bg-green-50" :
                    highlight.sentiment === "neutral" ? "border-l-gray-500 bg-gray-50" :
                    "border-l-red-500 bg-red-50"
                  }`}>
                    <CardContent className="pt-4">
                      <div className="space-y-3">
                        <div>
                          <div className="text-xs text-gray-600 mb-1">Question Asked:</div>
                          <p className="text-sm">{highlight.question}</p>
                        </div>
                        <div className="bg-white border border-gray-200 rounded-lg p-3">
                          <div className="flex items-center gap-2 mb-2">
                            <MessageSquare className="h-4 w-4 text-gray-600" />
                            <span className="text-xs text-gray-600">Candidate Response:</span>
                          </div>
                          <p className="text-sm text-gray-700 italic">"{highlight.response}"</p>
                        </div>
                        <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
                          <div className="flex items-center gap-2 mb-1">
                            <Brain className="h-4 w-4 text-purple-600" />
                            <span className="text-xs text-purple-900">AI Analysis:</span>
                          </div>
                          <p className="text-sm text-gray-700">{highlight.analysis}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="tone" className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm">Positive Tone</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center gap-3">
                      <Progress value={aiAnalysis.toneAnalysis.positive} className="flex-1" />
                      <span className="text-lg">{aiAnalysis.toneAnalysis.positive}%</span>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm">Confident</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center gap-3">
                      <Progress value={aiAnalysis.toneAnalysis.confident} className="flex-1" />
                      <span className="text-lg">{aiAnalysis.toneAnalysis.confident}%</span>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm">Professional</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center gap-3">
                      <Progress value={aiAnalysis.toneAnalysis.professional} className="flex-1" />
                      <span className="text-lg">{aiAnalysis.toneAnalysis.professional}%</span>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm">Enthusiastic</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center gap-3">
                      <Progress value={aiAnalysis.toneAnalysis.enthusiastic} className="flex-1" />
                      <span className="text-lg">{aiAnalysis.toneAnalysis.enthusiastic}%</span>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Card className="bg-blue-50 border-blue-200">
                <CardContent className="pt-4">
                  <div className="flex items-start gap-3">
                    <Volume2 className="h-5 w-5 text-blue-600 mt-1" />
                    <div>
                      <div className="text-sm text-blue-900 mb-2">Tone Analysis Summary</div>
                      <p className="text-sm text-gray-700">
                        The candidate maintained a highly professional tone throughout the interview with strong 
                        confidence levels. Voice analysis indicates genuine engagement and enthusiasm about the 
                        opportunity. Communication style is well-suited for client-facing and team leadership roles.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="communication" className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                {Object.entries(aiAnalysis.communicationMetrics).map(([key, value]) => (
                  <Card key={key}>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm capitalize">{key.replace(/([A-Z])/g, ' $1').trim()}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center gap-3 mb-2">
                        <Progress value={value} className="flex-1" />
                        <span className="text-lg">{value}%</span>
                      </div>
                      <Badge variant={value >= 85 ? "default" : value >= 70 ? "secondary" : "outline"}>
                        {value >= 85 ? "Excellent" : value >= 70 ? "Good" : "Fair"}
                      </Badge>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Your Notes & Evaluation */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Your Interview Notes & Evaluation
          </CardTitle>
          <CardDescription>
            Add your personal observations and ratings
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm mb-2 block">Interview Notes</label>
            <Textarea
              placeholder="Enter your observations, specific examples discussed, and overall impressions..."
              value={interviewNotes}
              onChange={(e) => setInterviewNotes(e.target.value)}
              rows={6}
            />
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="text-sm text-blue-900 mb-3">Quick Rating (Optional)</div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs text-gray-600">Technical Skills</label>
                <div className="flex gap-2 mt-1">
                  {[1, 2, 3, 4, 5].map((rating) => (
                    <button
                      key={rating}
                      onClick={() => setRatings({...ratings, technical: rating})}
                      className={`h-8 w-8 rounded ${
                        ratings.technical >= rating 
                          ? 'bg-indigo-600 text-white' 
                          : 'bg-gray-200 text-gray-600'
                      }`}
                    >
                      {rating}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="text-xs text-gray-600">Communication</label>
                <div className="flex gap-2 mt-1">
                  {[1, 2, 3, 4, 5].map((rating) => (
                    <button
                      key={rating}
                      onClick={() => setRatings({...ratings, communication: rating})}
                      className={`h-8 w-8 rounded ${
                        ratings.communication >= rating 
                          ? 'bg-indigo-600 text-white' 
                          : 'bg-gray-200 text-gray-600'
                      }`}
                    >
                      {rating}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="text-xs text-gray-600">Problem Solving</label>
                <div className="flex gap-2 mt-1">
                  {[1, 2, 3, 4, 5].map((rating) => (
                    <button
                      key={rating}
                      onClick={() => setRatings({...ratings, problemSolving: rating})}
                      className={`h-8 w-8 rounded ${
                        ratings.problemSolving >= rating 
                          ? 'bg-indigo-600 text-white' 
                          : 'bg-gray-200 text-gray-600'
                      }`}
                    >
                      {rating}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="text-xs text-gray-600">Culture Fit</label>
                <div className="flex gap-2 mt-1">
                  {[1, 2, 3, 4, 5].map((rating) => (
                    <button
                      key={rating}
                      onClick={() => setRatings({...ratings, cultureFit: rating})}
                      className={`h-8 w-8 rounded ${
                        ratings.cultureFit >= rating 
                          ? 'bg-indigo-600 text-white' 
                          : 'bg-gray-200 text-gray-600'
                      }`}
                    >
                      {rating}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <Button onClick={handleSubmitToDecisionDashboard} size="lg" className="gap-2">
          <Target className="h-5 w-5" />
          Submit to Decision Dashboard
        </Button>
        <Button onClick={handleSaveEvaluation} variant="outline" size="lg">
          Save Draft
        </Button>
      </div>
    </div>
  );
}
