import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Avatar, AvatarFallback } from "./ui/avatar";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Slider } from "./ui/slider";
import { 
  Star, 
  MapPin, 
  Award, 
  Brain, 
  Users, 
  TrendingUp,
  Filter,
  ArrowUpDown,
  Sparkles
} from "lucide-react";
import { Progress } from "./ui/progress";

interface Candidate {
  id: string;
  name: string;
  email: string;
  location: string;
  currentRole: string;
  experience: string;
  fitScore: number;
  technicalScore: number;
  softSkillsScore: number;
  cultureFitScore: number;
  diversityTags: string[];
  skills: string[];
  education: string;
  aiInsights: string[];
  successLikelihood: number;
  interviewStatus: "pending" | "scheduled" | "completed";
}

interface HiringManagerShortlistProps {
  onViewCandidate: (id: string) => void;
  onScheduleInterview: (id: string) => void;
}

export function HiringManagerShortlist({ onViewCandidate, onScheduleInterview }: HiringManagerShortlistProps) {
  const [candidates] = useState<Candidate[]>([
    {
      id: "1",
      name: "Sarah Johnson",
      email: "sarah.j@email.com",
      location: "New York, NY",
      currentRole: "Senior Frontend Engineer",
      experience: "6 years",
      fitScore: 94,
      technicalScore: 92,
      softSkillsScore: 96,
      cultureFitScore: 93,
      diversityTags: ["Female", "STEM Background"],
      skills: ["React", "TypeScript", "Node.js", "AWS", "Leadership"],
      education: "BS Computer Science, MIT",
      aiInsights: [
        "Exceptional communication skills based on portfolio",
        "Strong leadership potential",
        "Aligned with company values on innovation"
      ],
      successLikelihood: 89,
      interviewStatus: "scheduled",
    },
    {
      id: "2",
      name: "Michael Chen",
      email: "m.chen@email.com",
      location: "San Francisco, CA",
      currentRole: "Lead Backend Engineer",
      experience: "8 years",
      fitScore: 89,
      technicalScore: 95,
      softSkillsScore: 84,
      cultureFitScore: 87,
      diversityTags: ["Asian", "International Experience"],
      skills: ["Python", "Django", "PostgreSQL", "Docker", "Kubernetes"],
      education: "MS Software Engineering, Stanford",
      aiInsights: [
        "Deep technical expertise in scalable systems",
        "Proven track record at top tech companies",
        "May need support developing team communication"
      ],
      successLikelihood: 85,
      interviewStatus: "pending",
    },
    {
      id: "3",
      name: "Emily Rodriguez",
      email: "emily.r@email.com",
      location: "Austin, TX",
      currentRole: "Full Stack Developer",
      experience: "5 years",
      fitScore: 87,
      technicalScore: 88,
      softSkillsScore: 91,
      cultureFitScore: 85,
      diversityTags: ["Hispanic/Latina", "First Generation College"],
      skills: ["React", "Vue.js", "GraphQL", "MongoDB", "Team Collaboration"],
      education: "BS Computer Science, UT Austin",
      aiInsights: [
        "Quick learner with modern tech stack",
        "Strong collaborative work style",
        "Excellent cultural fit based on values assessment"
      ],
      successLikelihood: 82,
      interviewStatus: "completed",
    },
    {
      id: "4",
      name: "James Wilson",
      email: "j.wilson@email.com",
      location: "Seattle, WA",
      currentRole: "Engineering Manager",
      experience: "10 years",
      fitScore: 91,
      technicalScore: 90,
      softSkillsScore: 93,
      cultureFitScore: 90,
      diversityTags: ["Military Veteran", "Career Changer"],
      skills: ["Java", "Spring", "Microservices", "Team Management", "Agile"],
      education: "BS Engineering, Georgia Tech + MBA",
      aiInsights: [
        "Strong leadership and management experience",
        "Excellent problem-solving approach",
        "Proven ability to scale teams"
      ],
      successLikelihood: 91,
      interviewStatus: "pending",
    },
  ]);

  const [minFitScore, setMinFitScore] = useState([0]);
  const [sortBy, setSortBy] = useState("fitScore");
  const [diversityFilter, setDiversityFilter] = useState("all");
  const [softSkillsFilter, setSoftSkillsFilter] = useState("all");

  const filteredAndSortedCandidates = candidates
    .filter(c => c.fitScore >= minFitScore[0])
    .filter(c => diversityFilter === "all" || c.diversityTags.length > 0)
    .filter(c => softSkillsFilter === "all" || c.softSkillsScore >= parseInt(softSkillsFilter))
    .sort((a, b) => {
      switch (sortBy) {
        case "fitScore":
          return b.fitScore - a.fitScore;
        case "technical":
          return b.technicalScore - a.technicalScore;
        case "softSkills":
          return b.softSkillsScore - a.softSkillsScore;
        case "successLikelihood":
          return b.successLikelihood - a.successLikelihood;
        default:
          return 0;
      }
    });

  const avgFitScore = Math.round(candidates.reduce((sum, c) => sum + c.fitScore, 0) / candidates.length);
  const diverseCandidates = candidates.filter(c => c.diversityTags.length > 0).length;

  return (
    <div className="space-y-6">
      <div>
        <h2>Candidate Shortlist</h2>
        <p className="text-gray-600">Review AI-evaluated candidates and schedule interviews</p>
      </div>

      {/* Stats Overview */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <Users className="h-4 w-4" />
              Total Candidates
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl">{candidates.length}</div>
            <p className="text-xs text-gray-600 mt-1">From recruiter review</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <Brain className="h-4 w-4 text-indigo-600" />
              Avg AI Fit Score
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl text-indigo-600">{avgFitScore}%</div>
            <Progress value={avgFitScore} className="mt-2 h-2" />
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-green-600" />
              High Success Rate
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl text-green-600">
              {candidates.filter(c => c.successLikelihood >= 85).length}
            </div>
            <p className="text-xs text-gray-600 mt-1">≥85% likelihood</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-purple-600" />
              Diverse Pool
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl text-purple-600">{diverseCandidates}</div>
            <p className="text-xs text-gray-600 mt-1">With diversity tags</p>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filters & Sorting
          </CardTitle>
          <CardDescription>Refine candidates by AI metrics and attributes</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-4">
            <div className="space-y-2">
              <label className="text-sm">Sort By</label>
              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="fitScore">
                    <div className="flex items-center gap-2">
                      <ArrowUpDown className="h-3 w-3" />
                      AI Fit Score
                    </div>
                  </SelectItem>
                  <SelectItem value="technical">Technical Score</SelectItem>
                  <SelectItem value="softSkills">Soft Skills</SelectItem>
                  <SelectItem value="successLikelihood">Success Likelihood</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm">Soft Skills</label>
              <Select value={softSkillsFilter} onValueChange={setSoftSkillsFilter}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Levels</SelectItem>
                  <SelectItem value="90">Excellent (90+)</SelectItem>
                  <SelectItem value="80">Good (80+)</SelectItem>
                  <SelectItem value="70">Fair (70+)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm">Diversity</label>
              <Select value={diversityFilter} onValueChange={setDiversityFilter}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Candidates</SelectItem>
                  <SelectItem value="diverse">Diverse Backgrounds</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm">Min Fit Score: {minFitScore[0]}%</label>
              <Slider
                value={minFitScore}
                onValueChange={setMinFitScore}
                max={100}
                step={5}
                className="mt-2"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Candidates List */}
      <div className="space-y-4">
        {filteredAndSortedCandidates.map((candidate) => (
          <Card key={candidate.id} className="hover:shadow-md transition-shadow">
            <CardContent className="pt-6">
              <div className="flex items-start gap-4">
                <Avatar className="h-16 w-16">
                  <AvatarFallback className="bg-indigo-100 text-indigo-600 text-lg">
                    {candidate.name.split(" ").map(n => n[0]).join("")}
                  </AvatarFallback>
                </Avatar>

                <div className="flex-1 space-y-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <h3>{candidate.name}</h3>
                        {candidate.interviewStatus === "scheduled" && (
                          <Badge className="bg-blue-600">Interview Scheduled</Badge>
                        )}
                        {candidate.interviewStatus === "completed" && (
                          <Badge className="bg-green-600">Interview Complete</Badge>
                        )}
                      </div>
                      <p className="text-sm text-gray-600">{candidate.currentRole}</p>
                      <div className="flex items-center gap-3 mt-1 text-sm text-gray-600">
                        <div className="flex items-center gap-1">
                          <MapPin className="h-3 w-3" />
                          {candidate.location}
                        </div>
                        <div className="flex items-center gap-1">
                          <Award className="h-3 w-3" />
                          {candidate.experience}
                        </div>
                      </div>
                    </div>
                    <div className="text-center px-4 py-3 rounded-lg bg-gradient-to-br from-indigo-50 to-purple-50 border border-indigo-200">
                      <div className="text-3xl bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                        {candidate.fitScore}%
                      </div>
                      <div className="text-xs text-gray-600 flex items-center gap-1">
                        <Brain className="h-3 w-3" />
                        AI Fit Score
                      </div>
                    </div>
                  </div>

                  {/* AI Insights Highlight */}
                  <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-3">
                    <div className="flex items-center gap-2 mb-2">
                      <Sparkles className="h-4 w-4 text-purple-600" />
                      <span className="text-sm text-purple-900">AI Insights</span>
                    </div>
                    <ul className="space-y-1">
                      {candidate.aiInsights.map((insight, i) => (
                        <li key={i} className="text-sm text-gray-700">• {insight}</li>
                      ))}
                    </ul>
                  </div>

                  {/* Score Breakdown */}
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <div className="text-xs text-gray-600 mb-1">Technical Skills</div>
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

                  <div className="flex items-center gap-2">
                    <div className="text-sm text-gray-600">Success Likelihood:</div>
                    <Badge variant={candidate.successLikelihood >= 85 ? "default" : "secondary"} className="gap-1">
                      <TrendingUp className="h-3 w-3" />
                      {candidate.successLikelihood}%
                    </Badge>
                  </div>

                  {/* Diversity Tags */}
                  {candidate.diversityTags.length > 0 && (
                    <div>
                      <div className="text-xs text-gray-600 mb-1">Diversity Attributes</div>
                      <div className="flex gap-2 flex-wrap">
                        {candidate.diversityTags.map((tag) => (
                          <Badge key={tag} variant="outline" className="bg-purple-50 border-purple-200">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Skills */}
                  <div>
                    <div className="text-xs text-gray-600 mb-1">Key Skills</div>
                    <div className="flex gap-2 flex-wrap">
                      {candidate.skills.slice(0, 5).map((skill) => (
                        <Badge key={skill} variant="secondary">
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <div className="flex gap-2 pt-2">
                    <Button 
                      onClick={() => onViewCandidate(candidate.id)}
                      className="gap-2"
                    >
                      <Brain className="h-4 w-4" />
                      View AI Interview Assistant
                    </Button>
                    {candidate.interviewStatus === "pending" && (
                      <Button 
                        onClick={() => onScheduleInterview(candidate.id)}
                        variant="outline"
                      >
                        Schedule Interview
                      </Button>
                    )}
                    {candidate.interviewStatus === "completed" && (
                      <Button 
                        variant="outline"
                        className="gap-2"
                      >
                        <Star className="h-4 w-4" />
                        View Evaluation
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredAndSortedCandidates.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-gray-600">No candidates match your current filters</p>
            <Button 
              variant="outline" 
              className="mt-4"
              onClick={() => {
                setMinFitScore([0]);
                setDiversityFilter("all");
                setSoftSkillsFilter("all");
              }}
            >
              Reset Filters
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
