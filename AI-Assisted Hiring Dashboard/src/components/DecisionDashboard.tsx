import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Avatar, AvatarFallback } from "./ui/avatar";
import { Progress } from "./ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { 
  Brain, 
  Trophy, 
  TrendingUp,
  Target,
  Users,
  Sparkles,
  CheckCircle2,
  XCircle,
  Award,
  BarChart3,
  ChevronRight,
  Star
} from "lucide-react";
import { 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis, 
  Radar, 
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from "recharts";
import { toast } from "sonner@2.0.3";

interface Candidate {
  id: string;
  name: string;
  currentRole: string;
  fitScore: number;
  technicalScore: number;
  softSkillsScore: number;
  cultureFitScore: number;
  successLikelihood: number;
  experienceYears: number;
  interviewScore: number;
  aiRecommendationRank: number;
  skills: string[];
  strengths: string[];
  concerns: string[];
  aiReasoning: string[];
  salaryExpectation: string;
  availability: string;
}

export function DecisionDashboard() {
  const [selectedCandidates, setSelectedCandidates] = useState<string[]>(["1", "2"]);
  const [finalDecision, setFinalDecision] = useState<string | null>(null);

  const candidates: Candidate[] = [
    {
      id: "1",
      name: "Sarah Johnson",
      currentRole: "Senior Frontend Engineer",
      fitScore: 94,
      technicalScore: 92,
      softSkillsScore: 96,
      cultureFitScore: 93,
      successLikelihood: 89,
      experienceYears: 6,
      interviewScore: 91,
      aiRecommendationRank: 1,
      skills: ["React", "TypeScript", "Leadership", "AWS", "Node.js"],
      strengths: [
        "Exceptional communication and leadership skills",
        "Strong modern tech stack expertise",
        "Proven track record of team collaboration",
        "High cultural alignment with company values"
      ],
      concerns: [
        "Limited experience with large-scale backend systems",
        "May need mentorship in distributed systems architecture"
      ],
      aiReasoning: [
        "Highest soft skills score (96%) - critical for team lead role",
        "Interview performance exceeded expectations (91%)",
        "Cultural fit score aligns perfectly with team dynamics",
        "Communication clarity rated 89% by AI analysis",
        "Leadership potential identified through portfolio review"
      ],
      salaryExpectation: "$140k - $160k",
      availability: "2 weeks notice"
    },
    {
      id: "2",
      name: "Michael Chen",
      currentRole: "Lead Backend Engineer",
      fitScore: 89,
      technicalScore: 95,
      softSkillsScore: 84,
      cultureFitScore: 87,
      successLikelihood: 85,
      experienceYears: 8,
      interviewScore: 88,
      aiRecommendationRank: 2,
      skills: ["Python", "Django", "Kubernetes", "PostgreSQL", "System Design"],
      strengths: [
        "Deep technical expertise in scalable systems",
        "Proven track record at top tech companies",
        "Strong problem-solving methodology",
        "Experience with team management"
      ],
      concerns: [
        "Soft skills score slightly below team average",
        "May need support developing communication with non-technical stakeholders",
        "Salary expectations at upper end of budget"
      ],
      aiReasoning: [
        "Highest technical score (95%) - brings deep expertise",
        "8 years experience matches senior requirements",
        "Strong systematic approach to problem-solving",
        "Interview showed solid technical depth",
        "Could elevate team's technical standards"
      ],
      salaryExpectation: "$160k - $180k",
      availability: "1 month notice"
    },
    {
      id: "3",
      name: "Emily Rodriguez",
      currentRole: "Full Stack Developer",
      fitScore: 87,
      technicalScore: 88,
      softSkillsScore: 91,
      cultureFitScore: 85,
      successLikelihood: 82,
      experienceYears: 5,
      interviewScore: 86,
      aiRecommendationRank: 3,
      skills: ["React", "Vue.js", "GraphQL", "MongoDB", "Collaboration"],
      strengths: [
        "Quick learner with modern tech stack",
        "Strong collaborative work style",
        "Excellent cultural fit based on values",
        "Balanced full-stack skillset"
      ],
      concerns: [
        "Slightly less experience than ideal (5 years vs 6+ preferred)",
        "Would require relocation support",
        "May need time to ramp up on specific technologies"
      ],
      aiReasoning: [
        "Strong cultural fit (85%) - long-term retention potential",
        "Full-stack versatility adds team flexibility",
        "Growth trajectory shows rapid skill acquisition",
        "Interview demonstrated strong learning mindset",
        "Best value considering cost and potential"
      ],
      salaryExpectation: "$120k - $135k",
      availability: "Immediate"
    },
    {
      id: "4",
      name: "James Wilson",
      currentRole: "Engineering Manager",
      fitScore: 91,
      technicalScore: 90,
      softSkillsScore: 93,
      cultureFitScore: 90,
      successLikelihood: 91,
      experienceYears: 10,
      interviewScore: 92,
      aiRecommendationRank: 4,
      skills: ["Team Management", "Java", "Microservices", "Agile", "Strategy"],
      strengths: [
        "Extensive leadership and management experience",
        "Proven ability to scale teams",
        "Strong strategic thinking",
        "Excellent stakeholder management"
      ],
      concerns: [
        "May be overqualified for IC role",
        "Higher retention risk if seeking management position",
        "Salary expectations above budget range"
      ],
      aiReasoning: [
        "Highest overall success likelihood (91%)",
        "Strong leadership could benefit team growth",
        "Excellent interview performance (92%)",
        "May seek management role within 6-12 months",
        "Consider for future leadership pipeline"
      ],
      salaryExpectation: "$170k - $190k",
      availability: "3 weeks notice"
    }
  ];

  const topThreeCandidates = candidates
    .sort((a, b) => a.aiRecommendationRank - b.aiRecommendationRank)
    .slice(0, 3);

  const getComparisonData = (candidateIds: string[]) => {
    const selected = candidates.filter(c => candidateIds.includes(c.id));
    
    return [
      { metric: "Technical", ...Object.fromEntries(selected.map(c => [c.name, c.technicalScore])) },
      { metric: "Soft Skills", ...Object.fromEntries(selected.map(c => [c.name, c.softSkillsScore])) },
      { metric: "Culture Fit", ...Object.fromEntries(selected.map(c => [c.name, c.cultureFitScore])) },
      { metric: "Interview", ...Object.fromEntries(selected.map(c => [c.name, c.interviewScore])) },
    ];
  };

  const getRadarData = (candidate: Candidate) => [
    { subject: "Technical", score: candidate.technicalScore, fullMark: 100 },
    { subject: "Soft Skills", score: candidate.softSkillsScore, fullMark: 100 },
    { subject: "Culture Fit", score: candidate.cultureFitScore, fullMark: 100 },
    { subject: "Interview", score: candidate.interviewScore, fullMark: 100 },
    { subject: "AI Fit", score: candidate.fitScore, fullMark: 100 },
  ];

  const handleMakeOffer = (candidateId: string) => {
    const candidate = candidates.find(c => c.id === candidateId);
    setFinalDecision(candidateId);
    toast.success(`Offer extended to ${candidate?.name}! Moving to offer stage.`);
  };

  const colors = ["#6366f1", "#8b5cf6", "#ec4899", "#f59e0b"];

  return (
    <div className="space-y-6">
      <div>
        <h2>Decision Dashboard</h2>
        <p className="text-gray-600">AI-powered candidate comparison and recommendation</p>
      </div>

      {/* AI Top 3 Recommendations */}
      <Card className="border-2 border-purple-200 bg-gradient-to-r from-purple-50 to-indigo-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Trophy className="h-6 w-6 text-purple-600" />
            AI Recommended Top 3 Candidates
          </CardTitle>
          <CardDescription>
            Based on comprehensive analysis of skills, cultural fit, interview performance, and success likelihood
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            {topThreeCandidates.map((candidate, index) => (
              <Card 
                key={candidate.id} 
                className={`border-2 ${
                  index === 0 ? "border-yellow-400 bg-gradient-to-br from-yellow-50 to-amber-50" :
                  index === 1 ? "border-gray-400 bg-gradient-to-br from-gray-50 to-slate-50" :
                  "border-orange-400 bg-gradient-to-br from-orange-50 to-red-50"
                }`}
              >
                <CardContent className="pt-6">
                  <div className="flex items-start gap-3 mb-4">
                    <div className={`h-10 w-10 rounded-full flex items-center justify-center text-lg ${
                      index === 0 ? "bg-yellow-400 text-yellow-900" :
                      index === 1 ? "bg-gray-400 text-gray-900" :
                      "bg-orange-400 text-orange-900"
                    }`}>
                      #{index + 1}
                    </div>
                    <Avatar className="h-12 w-12">
                      <AvatarFallback className="bg-indigo-100 text-indigo-600">
                        {candidate.name.split(" ").map(n => n[0]).join("")}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h3 className="text-sm">{candidate.name}</h3>
                      </div>
                      <p className="text-xs text-gray-600">{candidate.currentRole}</p>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">AI Fit Score</span>
                      <span className="text-purple-600">{candidate.fitScore}%</span>
                    </div>
                    <Progress value={candidate.fitScore} className="h-2" />
                    
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Success Likelihood</span>
                      <span className="text-green-600">{candidate.successLikelihood}%</span>
                    </div>
                    <Progress value={candidate.successLikelihood} className="h-2" />
                  </div>

                  <div className="mt-4 p-3 bg-white rounded-lg border border-purple-200">
                    <div className="text-xs text-purple-900 mb-2 flex items-center gap-1">
                      <Brain className="h-3 w-3" />
                      Why recommended:
                    </div>
                    <ul className="space-y-1">
                      {candidate.aiReasoning.slice(0, 2).map((reason, i) => (
                        <li key={i} className="text-xs text-gray-700">• {reason}</li>
                      ))}
                    </ul>
                  </div>

                  <Button 
                    className="w-full mt-4"
                    variant={index === 0 ? "default" : "outline"}
                    onClick={() => {
                      if (!selectedCandidates.includes(candidate.id)) {
                        setSelectedCandidates([...selectedCandidates.slice(0, 1), candidate.id]);
                      }
                    }}
                  >
                    {index === 0 && <Star className="h-4 w-4 mr-2" />}
                    Compare
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Candidate Selection for Comparison */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Select Candidates to Compare
          </CardTitle>
          <CardDescription>Choose 2-3 candidates for side-by-side comparison</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 md:grid-cols-4">
            {candidates.map((candidate) => (
              <button
                key={candidate.id}
                onClick={() => {
                  if (selectedCandidates.includes(candidate.id)) {
                    setSelectedCandidates(selectedCandidates.filter(id => id !== candidate.id));
                  } else if (selectedCandidates.length < 3) {
                    setSelectedCandidates([...selectedCandidates, candidate.id]);
                  } else {
                    toast.error("You can compare up to 3 candidates at once");
                  }
                }}
                className={`p-3 rounded-lg border-2 text-left transition-all ${
                  selectedCandidates.includes(candidate.id)
                    ? "border-indigo-500 bg-indigo-50"
                    : "border-gray-200 hover:border-gray-300"
                }`}
              >
                <div className="flex items-center gap-2 mb-2">
                  <Avatar className="h-8 w-8">
                    <AvatarFallback className="bg-gray-100 text-xs">
                      {candidate.name.split(" ").map(n => n[0]).join("")}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm truncate">{candidate.name}</div>
                    <div className="text-xs text-gray-600">Rank #{candidate.aiRecommendationRank}</div>
                  </div>
                  {selectedCandidates.includes(candidate.id) && (
                    <CheckCircle2 className="h-5 w-5 text-indigo-600 flex-shrink-0" />
                  )}
                </div>
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Comparison Charts */}
      {selectedCandidates.length >= 2 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Side-by-Side Comparison
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="chart" className="space-y-4">
              <TabsList>
                <TabsTrigger value="chart">Bar Chart</TabsTrigger>
                <TabsTrigger value="radar">Skill Radar</TabsTrigger>
                <TabsTrigger value="detailed">Detailed View</TabsTrigger>
              </TabsList>

              <TabsContent value="chart">
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={getComparisonData(selectedCandidates)}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="metric" />
                    <YAxis domain={[0, 100]} />
                    <Tooltip />
                    <Legend />
                    {selectedCandidates.map((id, index) => {
                      const candidate = candidates.find(c => c.id === id);
                      return (
                        <Bar 
                          key={id} 
                          dataKey={candidate?.name} 
                          fill={colors[index]} 
                          radius={[8, 8, 0, 0]}
                        />
                      );
                    })}
                  </BarChart>
                </ResponsiveContainer>
              </TabsContent>

              <TabsContent value="radar">
                <div className="grid gap-6 md:grid-cols-3">
                  {selectedCandidates.map((id, index) => {
                    const candidate = candidates.find(c => c.id === id);
                    if (!candidate) return null;
                    return (
                      <div key={id} className="text-center">
                        <h3 className="text-sm mb-4">{candidate.name}</h3>
                        <ResponsiveContainer width="100%" height={300}>
                          <RadarChart data={getRadarData(candidate)}>
                            <PolarGrid />
                            <PolarAngleAxis dataKey="subject" />
                            <PolarRadiusAxis domain={[0, 100]} />
                            <Radar
                              name={candidate.name}
                              dataKey="score"
                              stroke={colors[index]}
                              fill={colors[index]}
                              fillOpacity={0.6}
                            />
                          </RadarChart>
                        </ResponsiveContainer>
                      </div>
                    );
                  })}
                </div>
              </TabsContent>

              <TabsContent value="detailed">
                <div className="space-y-6">
                  {selectedCandidates.map((id) => {
                    const candidate = candidates.find(c => c.id === id);
                    if (!candidate) return null;
                    return (
                      <Card key={id} className="border-2 border-gray-200">
                        <CardContent className="pt-6">
                          <div className="flex items-start gap-4 mb-4">
                            <Avatar className="h-16 w-16">
                              <AvatarFallback className="bg-indigo-100 text-indigo-600 text-lg">
                                {candidate.name.split(" ").map(n => n[0]).join("")}
                              </AvatarFallback>
                            </Avatar>
                            <div className="flex-1">
                              <div className="flex items-start justify-between mb-3">
                                <div>
                                  <h3>{candidate.name}</h3>
                                  <p className="text-sm text-gray-600">{candidate.currentRole} • {candidate.experienceYears} years</p>
                                  <Badge className="mt-2">AI Rank #{candidate.aiRecommendationRank}</Badge>
                                </div>
                                <div className="text-center px-4 py-3 rounded-lg bg-gradient-to-br from-indigo-50 to-purple-50 border border-indigo-200">
                                  <div className="text-3xl bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                                    {candidate.fitScore}%
                                  </div>
                                  <div className="text-xs text-gray-600">Fit Score</div>
                                </div>
                              </div>

                              <div className="grid grid-cols-4 gap-3 mb-4">
                                <div className="bg-blue-50 rounded-lg p-3">
                                  <div className="text-xs text-gray-600 mb-1">Technical</div>
                                  <div className="text-lg text-blue-600">{candidate.technicalScore}%</div>
                                </div>
                                <div className="bg-purple-50 rounded-lg p-3">
                                  <div className="text-xs text-gray-600 mb-1">Soft Skills</div>
                                  <div className="text-lg text-purple-600">{candidate.softSkillsScore}%</div>
                                </div>
                                <div className="bg-green-50 rounded-lg p-3">
                                  <div className="text-xs text-gray-600 mb-1">Culture</div>
                                  <div className="text-lg text-green-600">{candidate.cultureFitScore}%</div>
                                </div>
                                <div className="bg-orange-50 rounded-lg p-3">
                                  <div className="text-xs text-gray-600 mb-1">Success</div>
                                  <div className="text-lg text-orange-600">{candidate.successLikelihood}%</div>
                                </div>
                              </div>

                              <div className="grid grid-cols-2 gap-4 mb-4">
                                <div>
                                  <div className="text-xs text-gray-600 mb-1">Salary Expectation</div>
                                  <div className="text-sm">{candidate.salaryExpectation}</div>
                                </div>
                                <div>
                                  <div className="text-xs text-gray-600 mb-1">Availability</div>
                                  <div className="text-sm">{candidate.availability}</div>
                                </div>
                              </div>

                              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 mb-4">
                                <div className="flex items-center gap-2 mb-3">
                                  <Sparkles className="h-4 w-4 text-purple-600" />
                                  <span className="text-sm text-purple-900">AI Recommendation Reasoning</span>
                                </div>
                                <ul className="space-y-1">
                                  {candidate.aiReasoning.map((reason, i) => (
                                    <li key={i} className="text-sm text-gray-700">• {reason}</li>
                                  ))}
                                </ul>
                              </div>

                              <div className="grid grid-cols-2 gap-4">
                                <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                                  <div className="flex items-center gap-2 mb-2">
                                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                                    <span className="text-sm text-green-900">Strengths</span>
                                  </div>
                                  <ul className="space-y-1">
                                    {candidate.strengths.map((strength, i) => (
                                      <li key={i} className="text-xs text-gray-700">• {strength}</li>
                                    ))}
                                  </ul>
                                </div>
                                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                                  <div className="flex items-center gap-2 mb-2">
                                    <Target className="h-4 w-4 text-yellow-600" />
                                    <span className="text-sm text-yellow-900">Considerations</span>
                                  </div>
                                  <ul className="space-y-1">
                                    {candidate.concerns.map((concern, i) => (
                                      <li key={i} className="text-xs text-gray-700">• {concern}</li>
                                    ))}
                                  </ul>
                                </div>
                              </div>

                              <div className="flex gap-2 mt-4">
                                <Button 
                                  onClick={() => handleMakeOffer(candidate.id)}
                                  disabled={finalDecision !== null}
                                  className="gap-2"
                                >
                                  <Award className="h-4 w-4" />
                                  {finalDecision === candidate.id ? "Offer Extended" : "Extend Offer"}
                                </Button>
                                <Button variant="outline">
                                  Schedule Follow-up
                                </Button>
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    );
                  })}
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      )}

      {selectedCandidates.length < 2 && (
        <Card>
          <CardContent className="py-12 text-center">
            <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 mb-2">Select at least 2 candidates to view comparison</p>
            <p className="text-sm text-gray-500">Choose candidates from the selection above</p>
          </CardContent>
        </Card>
      )}

      {finalDecision && (
        <Card className="border-2 border-green-500 bg-green-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="h-12 w-12 rounded-full bg-green-500 flex items-center justify-center">
                <CheckCircle2 className="h-6 w-6 text-white" />
              </div>
              <div className="flex-1">
                <h3 className="text-green-900">Decision Made!</h3>
                <p className="text-sm text-green-700">
                  Offer extended to {candidates.find(c => c.id === finalDecision)?.name}. 
                  The candidate will be notified and moved to the offer stage.
                </p>
              </div>
              <Button variant="outline" className="gap-2">
                View Offer Details
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
