import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Progress } from "./ui/progress";
import { Input } from "./ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { 
  Sparkles, 
  MapPin, 
  Briefcase, 
  DollarSign,
  TrendingUp,
  Heart,
  Search,
  Filter,
  Building2,
  Clock,
  Users,
  Star,
  CheckCircle2,
  Target
} from "lucide-react";
import { toast } from "sonner@2.0.3";

interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  type: string;
  salary: string;
  matchScore: number;
  skillMatch: number;
  cultureMatch: number;
  growthPotential: number;
  description: string;
  requiredSkills: string[];
  yourSkills: string[];
  missingSkills: string[];
  posted: string;
  applicants: number;
  aiReason: string[];
  saved: boolean;
  applied: boolean;
}

export function JobRecommendations() {
  const [searchQuery, setSearchQuery] = useState("");
  const [filterType, setFilterType] = useState("all");
  const [sortBy, setSortBy] = useState("match");
  
  const [jobs, setJobs] = useState<Job[]>([
    {
      id: "1",
      title: "Senior Frontend Engineer",
      company: "TechCorp",
      location: "San Francisco, CA",
      type: "Full-time",
      salary: "$140k - $180k",
      matchScore: 94,
      skillMatch: 92,
      cultureMatch: 96,
      growthPotential: 93,
      description: "Join our team building next-generation web applications using React and TypeScript...",
      requiredSkills: ["React", "TypeScript", "Node.js", "AWS"],
      yourSkills: ["React", "TypeScript", "Node.js"],
      missingSkills: ["AWS"],
      posted: "2 days ago",
      applicants: 45,
      aiReason: [
        "Your React and TypeScript skills are a perfect match",
        "Company culture emphasizes work-life balance (matches your preferences)",
        "Strong growth opportunities based on your career goals"
      ],
      saved: false,
      applied: false
    },
    {
      id: "2",
      title: "Full Stack Developer",
      company: "InnovateLabs",
      location: "Remote",
      type: "Full-time",
      salary: "$120k - $150k",
      matchScore: 89,
      skillMatch: 88,
      cultureMatch: 87,
      growthPotential: 92,
      description: "Looking for a versatile developer to work on both frontend and backend systems...",
      requiredSkills: ["React", "Python", "PostgreSQL", "Docker"],
      yourSkills: ["React", "Python", "Docker"],
      missingSkills: ["PostgreSQL"],
      posted: "1 week ago",
      applicants: 78,
      aiReason: [
        "Remote position matches your location preferences",
        "Your full-stack experience aligns well",
        "Startup environment matches your work style preferences"
      ],
      saved: true,
      applied: false
    },
    {
      id: "3",
      title: "Lead Software Engineer",
      company: "CloudScale Inc",
      location: "New York, NY",
      type: "Full-time",
      salary: "$160k - $200k",
      matchScore: 87,
      skillMatch: 85,
      cultureMatch: 88,
      growthPotential: 90,
      description: "Lead a team of engineers building scalable cloud infrastructure solutions...",
      requiredSkills: ["Python", "Kubernetes", "AWS", "Team Leadership"],
      yourSkills: ["Python"],
      missingSkills: ["Kubernetes", "AWS", "Team Leadership"],
      posted: "3 days ago",
      applicants: 112,
      aiReason: [
        "Next career step based on your progression goals",
        "Leadership opportunity aligns with 7+ years experience",
        "Competitive salary matches your expectations"
      ],
      saved: false,
      applied: false
    },
    {
      id: "4",
      title: "React Developer",
      company: "StartupXYZ",
      location: "Austin, TX",
      type: "Full-time",
      salary: "$110k - $140k",
      matchScore: 91,
      skillMatch: 95,
      cultureMatch: 86,
      growthPotential: 89,
      description: "Build beautiful user interfaces for our growing fintech platform...",
      requiredSkills: ["React", "TypeScript", "GraphQL", "CSS"],
      yourSkills: ["React", "TypeScript", "GraphQL"],
      missingSkills: [],
      posted: "5 days ago",
      applicants: 34,
      aiReason: [
        "100% skill match - you have all required skills!",
        "Fintech domain matches your industry interests",
        "Fast-growing company with equity opportunities"
      ],
      saved: false,
      applied: false
    }
  ]);

  const handleSaveJob = (jobId: string) => {
    setJobs(jobs.map(job => 
      job.id === jobId ? { ...job, saved: !job.saved } : job
    ));
    const job = jobs.find(j => j.id === jobId);
    if (job && !job.saved) {
      toast.success(`Saved ${job.title} at ${job.company}`);
    }
  };

  const handleApply = (jobId: string) => {
    setJobs(jobs.map(job => 
      job.id === jobId ? { ...job, applied: true } : job
    ));
    const job = jobs.find(j => j.id === jobId);
    toast.success(`Application submitted for ${job?.title}!`);
  };

  const filteredJobs = jobs
    .filter(job => 
      (filterType === "all" || 
       (filterType === "saved" && job.saved) ||
       (filterType === "applied" && job.applied) ||
       (filterType === "remote" && job.location.toLowerCase().includes("remote")))
    )
    .filter(job =>
      job.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      job.company.toLowerCase().includes(searchQuery.toLowerCase())
    )
    .sort((a, b) => {
      if (sortBy === "match") return b.matchScore - a.matchScore;
      if (sortBy === "salary") return parseInt(b.salary.split("-")[1]) - parseInt(a.salary.split("-")[1]);
      if (sortBy === "recent") return new Date(b.posted).getTime() - new Date(a.posted).getTime();
      return 0;
    });

  const avgMatchScore = Math.round(jobs.reduce((sum, job) => sum + job.matchScore, 0) / jobs.length);
  const savedJobs = jobs.filter(j => j.saved).length;
  const appliedJobs = jobs.filter(j => j.applied).length;

  return (
    <div className="space-y-6">
      <div>
        <h2>Your Personalized Jobs</h2>
        <p className="text-gray-600">AI-powered recommendations based on your skills and preferences</p>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card className="border-2 border-blue-200 bg-gradient-to-br from-blue-50 to-indigo-50">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-blue-600" />
              Avg Match Score
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl text-blue-600">{avgMatchScore}%</div>
            <Progress value={avgMatchScore} className="mt-2 h-2" />
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <Target className="h-4 w-4" />
              Recommended
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl">{jobs.length}</div>
            <p className="text-xs text-gray-600 mt-1">Perfect matches</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <Heart className="h-4 w-4 text-red-600" />
              Saved
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl text-red-600">{savedJobs}</div>
            <p className="text-xs text-gray-600 mt-1">Jobs bookmarked</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-green-600" />
              Applied
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl text-green-600">{appliedJobs}</div>
            <p className="text-xs text-gray-600 mt-1">Applications sent</p>
          </CardContent>
        </Card>
      </div>

      {/* Search & Filter */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search by job title or company..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={filterType} onValueChange={setFilterType}>
              <SelectTrigger className="w-full md:w-48">
                <Filter className="h-4 w-4 mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Jobs</SelectItem>
                <SelectItem value="saved">Saved Only</SelectItem>
                <SelectItem value="applied">Applied</SelectItem>
                <SelectItem value="remote">Remote Only</SelectItem>
              </SelectContent>
            </Select>
            <Select value={sortBy} onValueChange={setSortBy}>
              <SelectTrigger className="w-full md:w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="match">Best Match</SelectItem>
                <SelectItem value="salary">Highest Salary</SelectItem>
                <SelectItem value="recent">Most Recent</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Job Cards */}
      <div className="space-y-4">
        {filteredJobs.map((job) => (
          <Card key={job.id} className="hover:shadow-lg transition-shadow">
            <CardContent className="pt-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-start gap-4">
                    <div className="h-14 w-14 rounded-lg bg-gradient-to-br from-blue-100 to-purple-100 flex items-center justify-center flex-shrink-0">
                      <Building2 className="h-7 w-7 text-blue-600" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-start justify-between">
                        <div>
                          <h3 className="mb-1">{job.title}</h3>
                          <p className="text-sm text-gray-600 mb-2">{job.company}</p>
                          <div className="flex flex-wrap gap-3 text-sm text-gray-600">
                            <div className="flex items-center gap-1">
                              <MapPin className="h-3 w-3" />
                              {job.location}
                            </div>
                            <div className="flex items-center gap-1">
                              <Briefcase className="h-3 w-3" />
                              {job.type}
                            </div>
                            <div className="flex items-center gap-1">
                              <DollarSign className="h-3 w-3" />
                              {job.salary}
                            </div>
                            <div className="flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              {job.posted}
                            </div>
                            <div className="flex items-center gap-1">
                              <Users className="h-3 w-3" />
                              {job.applicants} applicants
                            </div>
                          </div>
                        </div>
                        <div className="text-center px-4 py-3 rounded-lg bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200">
                          <div className="text-3xl text-green-600">{job.matchScore}%</div>
                          <div className="text-xs text-gray-600 flex items-center gap-1">
                            <Star className="h-3 w-3" />
                            Match Score
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* AI Insights */}
              <div className="mb-4 p-4 bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg">
                <div className="flex items-center gap-2 mb-3">
                  <Sparkles className="h-4 w-4 text-purple-600" />
                  <span className="text-sm text-purple-900">Why This Job Matches You</span>
                </div>
                <ul className="space-y-1">
                  {job.aiReason.map((reason, i) => (
                    <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                      <CheckCircle2 className="h-4 w-4 text-green-600 flex-shrink-0 mt-0.5" />
                      {reason}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Match Breakdown */}
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div>
                  <div className="text-xs text-gray-600 mb-1">Skill Match</div>
                  <div className="flex items-center gap-2">
                    <Progress value={job.skillMatch} className="h-2 flex-1" />
                    <span className="text-sm">{job.skillMatch}%</span>
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-600 mb-1">Culture Fit</div>
                  <div className="flex items-center gap-2">
                    <Progress value={job.cultureMatch} className="h-2 flex-1" />
                    <span className="text-sm">{job.cultureMatch}%</span>
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-600 mb-1">Growth Potential</div>
                  <div className="flex items-center gap-2">
                    <Progress value={job.growthPotential} className="h-2 flex-1" />
                    <span className="text-sm">{job.growthPotential}%</span>
                  </div>
                </div>
              </div>

              {/* Skills Match */}
              <div className="grid md:grid-cols-2 gap-4 mb-4">
                <div>
                  <div className="text-xs text-gray-600 mb-2">Your Matching Skills</div>
                  <div className="flex gap-2 flex-wrap">
                    {job.yourSkills.map((skill) => (
                      <Badge key={skill} className="bg-green-600">
                        <CheckCircle2 className="h-3 w-3 mr-1" />
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </div>
                {job.missingSkills.length > 0 && (
                  <div>
                    <div className="text-xs text-gray-600 mb-2">Skills to Learn</div>
                    <div className="flex gap-2 flex-wrap">
                      {job.missingSkills.map((skill) => (
                        <Badge key={skill} variant="outline" className="bg-orange-50 border-orange-200">
                          <TrendingUp className="h-3 w-3 mr-1" />
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="flex gap-2">
                {!job.applied ? (
                  <Button onClick={() => handleApply(job.id)} className="gap-2">
                    <CheckCircle2 className="h-4 w-4" />
                    Apply Now
                  </Button>
                ) : (
                  <Button disabled className="gap-2">
                    <CheckCircle2 className="h-4 w-4" />
                    Applied ✓
                  </Button>
                )}
                <Button 
                  variant="outline" 
                  onClick={() => handleSaveJob(job.id)}
                  className={job.saved ? "bg-red-50 border-red-200" : ""}
                >
                  <Heart className={`h-4 w-4 ${job.saved ? 'fill-red-600 text-red-600' : ''}`} />
                </Button>
                <Button variant="outline">View Details</Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredJobs.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-gray-600">No jobs found matching your criteria</p>
            <Button 
              variant="outline" 
              className="mt-4"
              onClick={() => {
                setSearchQuery("");
                setFilterType("all");
              }}
            >
              Clear Filters
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
