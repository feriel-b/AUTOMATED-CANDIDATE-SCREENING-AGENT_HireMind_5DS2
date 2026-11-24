import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Avatar, AvatarFallback } from "./ui/avatar";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Progress } from "./ui/progress";
import { 
  Brain, 
  Lightbulb, 
  Target, 
  TrendingUp, 
  CheckCircle2,
  AlertCircle,
  Sparkles,
  Copy,
  Clock,
  Users
} from "lucide-react";
import { toast } from "sonner@2.0.3";

interface InterviewQuestion {
  id: string;
  category: string;
  question: string;
  rationale: string;
  expectedAnswer: string;
  scoringCriteria: string[];
}

interface AIInterviewAssistantProps {
  candidateId: string;
  onBack: () => void;
  onStartEvaluation: () => void;
}

export function AIInterviewAssistant({ candidateId, onBack, onStartEvaluation }: AIInterviewAssistantProps) {
  const [copiedQuestions, setCopiedQuestions] = useState<Set<string>>(new Set());

  // Mock candidate data
  const candidate = {
    id: candidateId,
    name: "Sarah Johnson",
    currentRole: "Senior Frontend Engineer",
    fitScore: 94,
    technicalScore: 92,
    softSkillsScore: 96,
    cultureFitScore: 93,
    successLikelihood: 89,
    skills: ["React", "TypeScript", "Node.js", "AWS", "Leadership"],
    experience: "6 years",
    strengths: [
      "Exceptional communication skills",
      "Strong leadership potential",
      "Modern tech stack expertise"
    ],
    concerns: [
      "Limited experience with large-scale systems",
      "May need mentorship in backend architecture"
    ]
  };

  const questions: InterviewQuestion[] = [
    {
      id: "1",
      category: "Technical",
      question: "Can you walk me through a complex React application you've built? Focus on state management decisions and performance optimization strategies you implemented.",
      rationale: "Assesses depth of React expertise and architectural thinking. Candidate's profile shows strong React background.",
      expectedAnswer: "Should mention state management libraries (Redux/Context), code splitting, memoization, and real-world performance metrics.",
      scoringCriteria: [
        "Demonstrates deep technical knowledge",
        "Explains tradeoffs clearly",
        "Provides specific examples with metrics"
      ]
    },
    {
      id: "2",
      category: "Technical",
      question: "Describe a situation where you had to scale a frontend application to handle 10x traffic. What challenges did you face and how did you solve them?",
      rationale: "Addresses the concern about large-scale systems experience. Tests problem-solving under pressure.",
      expectedAnswer: "Should cover caching strategies, CDN usage, lazy loading, API optimization, and monitoring.",
      scoringCriteria: [
        "Structured problem-solving approach",
        "Mentions scalability best practices",
        "Shows understanding of infrastructure"
      ]
    },
    {
      id: "3",
      category: "Leadership",
      question: "Tell me about a time when you had to lead a project or mentor junior developers. How did you approach it and what was the outcome?",
      rationale: "Evaluates leadership potential identified in AI analysis. Critical for senior role expectations.",
      expectedAnswer: "Should demonstrate empathy, clear communication, delegation skills, and measurable impact.",
      scoringCriteria: [
        "Shows leadership initiative",
        "Demonstrates mentorship ability",
        "Quantifies team impact"
      ]
    },
    {
      id: "4",
      category: "Problem Solving",
      question: "Describe a technical decision you made that you later realized was wrong. How did you handle it?",
      rationale: "Tests humility, learning ability, and decision-making process. Important for cultural fit.",
      expectedAnswer: "Should show accountability, learning mindset, and ability to course-correct gracefully.",
      scoringCriteria: [
        "Takes ownership of mistakes",
        "Shows learning and growth",
        "Demonstrates resilience"
      ]
    },
    {
      id: "5",
      category: "Culture Fit",
      question: "Our company values rapid innovation and experimentation. Can you share an example of when you had to balance moving fast with maintaining code quality?",
      rationale: "Directly assesses alignment with company culture. Tests pragmatic decision-making.",
      expectedAnswer: "Should demonstrate understanding of technical debt tradeoffs and strategic thinking.",
      scoringCriteria: [
        "Balances speed with quality",
        "Shows strategic thinking",
        "Aligns with company values"
      ]
    },
    {
      id: "6",
      category: "Soft Skills",
      question: "Tell me about a time when you had to persuade stakeholders or team members who disagreed with your technical approach.",
      rationale: "Evaluates communication and influence skills, a key strength identified in AI analysis.",
      expectedAnswer: "Should show empathy, data-driven arguments, and collaborative problem-solving.",
      scoringCriteria: [
        "Demonstrates strong communication",
        "Uses data and reasoning",
        "Shows collaborative mindset"
      ]
    }
  ];

  const handleCopyQuestion = (questionId: string, questionText: string) => {
    navigator.clipboard.writeText(questionText);
    setCopiedQuestions(new Set(copiedQuestions).add(questionId));
    toast.success("Question copied to clipboard");
    setTimeout(() => {
      setCopiedQuestions(prev => {
        const newSet = new Set(prev);
        newSet.delete(questionId);
        return newSet;
      });
    }, 2000);
  };

  const categoryColors = {
    "Technical": "bg-blue-100 text-blue-700 border-blue-200",
    "Leadership": "bg-purple-100 text-purple-700 border-purple-200",
    "Problem Solving": "bg-green-100 text-green-700 border-green-200",
    "Culture Fit": "bg-orange-100 text-orange-700 border-orange-200",
    "Soft Skills": "bg-pink-100 text-pink-700 border-pink-200"
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Button variant="ghost" onClick={onBack} className="mb-2">
            ← Back to Shortlist
          </Button>
          <h2>AI Interview Assistant</h2>
          <p className="text-gray-600">Personalized interview guidance and success predictions</p>
        </div>
      </div>

      {/* Candidate Overview */}
      <Card className="border-2 border-indigo-200">
        <CardContent className="pt-6">
          <div className="flex items-start gap-4">
            <Avatar className="h-16 w-16">
              <AvatarFallback className="bg-indigo-100 text-indigo-600 text-lg">
                {candidate.name.split(" ").map(n => n[0]).join("")}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3>{candidate.name}</h3>
                  <p className="text-sm text-gray-600">{candidate.currentRole} • {candidate.experience}</p>
                </div>
                <div className="text-center px-4 py-3 rounded-lg bg-gradient-to-br from-indigo-50 to-purple-50 border border-indigo-200">
                  <div className="text-3xl bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                    {candidate.fitScore}%
                  </div>
                  <div className="text-xs text-gray-600">AI Fit Score</div>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4 mb-4">
                <div>
                  <div className="text-xs text-gray-600 mb-1">Technical</div>
                  <div className="flex items-center gap-2">
                    <Progress value={candidate.technicalScore} className="h-2 flex-1" />
                    <span className="text-sm">{candidate.technicalScore}%</span>
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-600 mb-1">Soft Skills</div>
                  <div className="flex items-center gap-2">
                    <Progress value={candidate.softSkillsScore} className="h-2 flex-1" />
                    <span className="text-sm">{candidate.softSkillsScore}%</span>
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-600 mb-1">Culture Fit</div>
                  <div className="flex items-center gap-2">
                    <Progress value={candidate.cultureFitScore} className="h-2 flex-1" />
                    <span className="text-sm">{candidate.cultureFitScore}%</span>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    <span className="text-sm text-green-900">Key Strengths</span>
                  </div>
                  <ul className="space-y-1">
                    {candidate.strengths.map((strength, i) => (
                      <li key={i} className="text-sm text-gray-700">• {strength}</li>
                    ))}
                  </ul>
                </div>
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertCircle className="h-4 w-4 text-yellow-600" />
                    <span className="text-sm text-yellow-900">Areas to Probe</span>
                  </div>
                  <ul className="space-y-1">
                    {candidate.concerns.map((concern, i) => (
                      <li key={i} className="text-sm text-gray-700">• {concern}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Success Prediction */}
      <Card className="border-2 border-green-200 bg-gradient-to-r from-green-50 to-emerald-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-green-600" />
            AI Success Prediction
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <div className="text-5xl text-green-600">{candidate.successLikelihood}%</div>
            <div className="flex-1">
              <p className="mb-2">Likelihood of success in this role based on:</p>
              <ul className="space-y-1 text-sm text-gray-700">
                <li>✓ Skills match (92% alignment)</li>
                <li>✓ Cultural fit analysis (93% match)</li>
                <li>✓ Experience level assessment</li>
                <li>✓ Communication style compatibility</li>
              </ul>
            </div>
            <div className="text-right">
              <Badge className="bg-green-600 text-lg px-4 py-2">High Potential</Badge>
              <p className="text-xs text-gray-600 mt-2">Top 15% of all candidates</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Interview Questions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-indigo-600" />
            AI-Generated Interview Questions
          </CardTitle>
          <CardDescription>
            Personalized questions designed to evaluate key competencies and address specific areas
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="all" className="space-y-4">
            <TabsList>
              <TabsTrigger value="all">All Questions ({questions.length})</TabsTrigger>
              <TabsTrigger value="technical">Technical</TabsTrigger>
              <TabsTrigger value="behavioral">Leadership & Soft Skills</TabsTrigger>
              <TabsTrigger value="culture">Culture Fit</TabsTrigger>
            </TabsList>

            <TabsContent value="all" className="space-y-4">
              {questions.map((q, index) => (
                <Card key={q.id} className="border-l-4 border-l-indigo-500">
                  <CardContent className="pt-6">
                    <div className="space-y-3">
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-2">
                          <Badge className={`${categoryColors[q.category as keyof typeof categoryColors]} border`}>
                            {q.category}
                          </Badge>
                          <span className="text-sm text-gray-600">Question {index + 1}</span>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleCopyQuestion(q.id, q.question)}
                          className="gap-2"
                        >
                          {copiedQuestions.has(q.id) ? (
                            <>
                              <CheckCircle2 className="h-4 w-4 text-green-600" />
                              Copied
                            </>
                          ) : (
                            <>
                              <Copy className="h-4 w-4" />
                              Copy
                            </>
                          )}
                        </Button>
                      </div>

                      <div className="bg-gray-50 p-4 rounded-lg">
                        <p className="text-gray-900">{q.question}</p>
                      </div>

                      <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
                        <div className="flex items-center gap-2 mb-1">
                          <Lightbulb className="h-4 w-4 text-purple-600" />
                          <span className="text-sm text-purple-900">AI Rationale</span>
                        </div>
                        <p className="text-sm text-gray-700">{q.rationale}</p>
                      </div>

                      <div className="grid grid-cols-2 gap-3">
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                          <div className="flex items-center gap-2 mb-1">
                            <Target className="h-4 w-4 text-blue-600" />
                            <span className="text-sm text-blue-900">What to Look For</span>
                          </div>
                          <p className="text-sm text-gray-700">{q.expectedAnswer}</p>
                        </div>

                        <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                          <div className="flex items-center gap-2 mb-1">
                            <CheckCircle2 className="h-4 w-4 text-green-600" />
                            <span className="text-sm text-green-900">Scoring Criteria</span>
                          </div>
                          <ul className="space-y-1">
                            {q.scoringCriteria.map((criteria, i) => (
                              <li key={i} className="text-sm text-gray-700">• {criteria}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </TabsContent>

            <TabsContent value="technical" className="space-y-4">
              {questions.filter(q => q.category === "Technical").map((q, index) => (
                <Card key={q.id} className="border-l-4 border-l-blue-500">
                  <CardContent className="pt-6">
                    <div className="bg-gray-50 p-4 rounded-lg mb-3">
                      <p className="text-gray-900">{q.question}</p>
                    </div>
                    <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
                      <div className="flex items-center gap-2 mb-1">
                        <Lightbulb className="h-4 w-4 text-purple-600" />
                        <span className="text-sm text-purple-900">AI Rationale</span>
                      </div>
                      <p className="text-sm text-gray-700">{q.rationale}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </TabsContent>

            <TabsContent value="behavioral" className="space-y-4">
              {questions.filter(q => q.category === "Leadership" || q.category === "Soft Skills").map((q) => (
                <Card key={q.id} className="border-l-4 border-l-purple-500">
                  <CardContent className="pt-6">
                    <div className="bg-gray-50 p-4 rounded-lg mb-3">
                      <p className="text-gray-900">{q.question}</p>
                    </div>
                    <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
                      <div className="flex items-center gap-2 mb-1">
                        <Lightbulb className="h-4 w-4 text-purple-600" />
                        <span className="text-sm text-purple-900">AI Rationale</span>
                      </div>
                      <p className="text-sm text-gray-700">{q.rationale}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </TabsContent>

            <TabsContent value="culture" className="space-y-4">
              {questions.filter(q => q.category === "Culture Fit" || q.category === "Problem Solving").map((q) => (
                <Card key={q.id} className="border-l-4 border-l-orange-500">
                  <CardContent className="pt-6">
                    <div className="bg-gray-50 p-4 rounded-lg mb-3">
                      <p className="text-gray-900">{q.question}</p>
                    </div>
                    <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
                      <div className="flex items-center gap-2 mb-1">
                        <Lightbulb className="h-4 w-4 text-purple-600" />
                        <span className="text-sm text-purple-900">AI Rationale</span>
                      </div>
                      <p className="text-sm text-gray-700">{q.rationale}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </TabsContent>
          </Tabs>

          <div className="mt-6 p-4 bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 rounded-lg">
            <div className="flex items-start gap-3">
              <Sparkles className="h-5 w-5 text-indigo-600 mt-1" />
              <div className="flex-1">
                <div className="text-sm text-indigo-900 mb-2">Interview Tips</div>
                <ul className="space-y-1 text-sm text-gray-700">
                  <li>• Estimated interview time: <span className="font-medium">45-60 minutes</span></li>
                  <li>• Allow time for candidate questions at the end</li>
                  <li>• Focus on behavioral examples with the STAR method</li>
                  <li>• Take notes on each scoring criteria for consistency</li>
                </ul>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <Button onClick={onStartEvaluation} size="lg" className="gap-2">
          <CheckCircle2 className="h-5 w-5" />
          Complete Interview & Start Evaluation
        </Button>
        <Button variant="outline" size="lg">
          Save Questions for Later
        </Button>
      </div>
    </div>
  );
}
