import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Input } from "./ui/input";
import { Checkbox } from "./ui/checkbox";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Avatar, AvatarFallback } from "./ui/avatar";
import { Search, Filter, Star, TrendingUp, Mail, Calendar } from "lucide-react";
import { Progress } from "./ui/progress";
import { toast } from "sonner@2.0.3";

interface Candidate {
  id: string;
  name: string;
  email: string;
  location: string;
  currentRole: string;
  experience: string;
  fitScore: number;
  skills: string[];
  matchedSkills: number;
  totalSkills: number;
  availability: string;
}

export function AutomatedScreening() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCandidates, setSelectedCandidates] = useState<string[]>([]);
  const [sortBy, setSortBy] = useState("score");

  const candidates: Candidate[] = [
    {
      id: "1",
      name: "Sarah Johnson",
      email: "sarah.j@email.com",
      location: "New York, NY",
      currentRole: "Senior Frontend Engineer",
      experience: "6 years",
      fitScore: 94,
      skills: ["React", "TypeScript", "Node.js", "AWS"],
      matchedSkills: 4,
      totalSkills: 5,
      availability: "2 weeks",
    },
    {
      id: "2",
      name: "Michael Chen",
      email: "m.chen@email.com",
      location: "San Francisco, CA",
      currentRole: "Lead Backend Engineer",
      experience: "8 years",
      fitScore: 89,
      skills: ["Python", "Django", "PostgreSQL", "Docker"],
      matchedSkills: 3,
      totalSkills: 5,
      availability: "1 month",
    },
    {
      id: "3",
      name: "Emily Rodriguez",
      email: "emily.r@email.com",
      location: "Austin, TX",
      currentRole: "Full Stack Developer",
      experience: "5 years",
      fitScore: 87,
      skills: ["React", "Vue.js", "GraphQL", "MongoDB"],
      matchedSkills: 3,
      totalSkills: 5,
      availability: "Immediate",
    },
    {
      id: "4",
      name: "David Kim",
      email: "david.kim@email.com",
      location: "Seattle, WA",
      currentRole: "Senior Software Engineer",
      experience: "7 years",
      fitScore: 82,
      skills: ["Java", "Spring Boot", "Kubernetes", "AWS"],
      matchedSkills: 2,
      totalSkills: 5,
      availability: "3 weeks",
    },
    {
      id: "5",
      name: "Amanda Lee",
      email: "amanda.lee@email.com",
      location: "Boston, MA",
      currentRole: "Frontend Developer",
      experience: "4 years",
      fitScore: 76,
      skills: ["React", "JavaScript", "CSS", "Redux"],
      matchedSkills: 2,
      totalSkills: 5,
      availability: "2 weeks",
    },
  ];

  const toggleCandidate = (id: string) => {
    setSelectedCandidates((prev) =>
      prev.includes(id) ? prev.filter((cId) => cId !== id) : [...prev, id]
    );
  };

  const handleShortlist = () => {
    if (selectedCandidates.length === 0) {
      toast.error("Please select at least one candidate");
      return;
    }
    toast.success(`${selectedCandidates.length} candidates added to shortlist`);
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return "text-green-600";
    if (score >= 80) return "text-blue-600";
    if (score >= 70) return "text-yellow-600";
    return "text-gray-600";
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 90) return "bg-green-50 border-green-200";
    if (score >= 80) return "bg-blue-50 border-blue-200";
    if (score >= 70) return "bg-yellow-50 border-yellow-200";
    return "bg-gray-50 border-gray-200";
  };

  return (
    <div className="space-y-6">
      <div>
        <h2>Automated Screening</h2>
        <p className="text-gray-600">Candidates ranked by AI fit score for Senior Full Stack Engineer</p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search candidates..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={sortBy} onValueChange={setSortBy}>
              <SelectTrigger className="w-[200px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="score">Sort by: Fit Score</SelectItem>
                <SelectItem value="experience">Sort by: Experience</SelectItem>
                <SelectItem value="availability">Sort by: Availability</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" className="gap-2">
              <Filter className="h-4 w-4" />
              Filters
            </Button>
          </div>
        </CardHeader>
      </Card>

      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-600">
          {candidates.length} candidates found • {selectedCandidates.length} selected
        </p>
        <Button onClick={handleShortlist} disabled={selectedCandidates.length === 0}>
          Add to Shortlist ({selectedCandidates.length})
        </Button>
      </div>

      <div className="space-y-4">
        {candidates.map((candidate, index) => (
          <Card key={candidate.id} className="hover:shadow-md transition-shadow">
            <CardContent className="pt-6">
              <div className="flex items-start gap-4">
                <Checkbox
                  checked={selectedCandidates.includes(candidate.id)}
                  onCheckedChange={() => toggleCandidate(candidate.id)}
                  className="mt-1"
                />
                
                <Avatar className="h-12 w-12">
                  <AvatarFallback className="bg-indigo-100 text-indigo-600">
                    {candidate.name.split(" ").map(n => n[0]).join("")}
                  </AvatarFallback>
                </Avatar>

                <div className="flex-1 space-y-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <h3>{candidate.name}</h3>
                        {index < 3 && (
                          <Badge variant="secondary" className="gap-1">
                            <Star className="h-3 w-3" />
                            Top Match
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm text-gray-600">{candidate.currentRole}</p>
                    </div>
                    <div className={`text-center px-4 py-2 rounded-lg border ${getScoreBgColor(candidate.fitScore)}`}>
                      <div className={`text-2xl ${getScoreColor(candidate.fitScore)}`}>
                        {candidate.fitScore}%
                      </div>
                      <div className="text-xs text-gray-600">AI Fit Score</div>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">Location:</span> {candidate.location}
                    </div>
                    <div>
                      <span className="text-gray-500">Experience:</span> {candidate.experience}
                    </div>
                    <div className="flex items-center gap-1">
                      <Calendar className="h-3 w-3 text-gray-500" />
                      <span className="text-gray-500">Available:</span> {candidate.availability}
                    </div>
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-gray-600">
                        Skills Match: {candidate.matchedSkills}/{candidate.totalSkills}
                      </span>
                      <span className="text-sm">
                        {Math.round((candidate.matchedSkills / candidate.totalSkills) * 100)}%
                      </span>
                    </div>
                    <Progress value={(candidate.matchedSkills / candidate.totalSkills) * 100} />
                  </div>

                  <div className="flex gap-2 flex-wrap">
                    {candidate.skills.map((skill) => (
                      <Badge key={skill} variant="outline">
                        {skill}
                      </Badge>
                    ))}
                  </div>

                  <div className="flex gap-2 pt-2">
                    <Button variant="outline" size="sm" className="gap-2">
                      <Mail className="h-4 w-4" />
                      Contact
                    </Button>
                    <Button variant="outline" size="sm">
                      View Profile
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
