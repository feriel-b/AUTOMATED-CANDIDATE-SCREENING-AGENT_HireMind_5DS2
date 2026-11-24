import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Progress } from "./ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { 
  Clock,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Brain,
  TrendingUp,
  BookOpen,
  Target,
  Sparkles,
  MessageSquare,
  Calendar,
  FileText,
  Award,
  Lightbulb
} from "lucide-react";

interface Application {
  id: string;
  jobTitle: string;
  company: string;
  appliedDate: string;
  status: "applied" | "screening" | "interview" | "offer" | "rejected";
  matchScore: number;
  lastUpdate: string;
  timeline: {
    stage: string;
    date: string;
    status: "completed" | "current" | "pending";
  }[];
  aiFeedback?: {
    strengths: string[];
    gaps: string[];
    recommendations: string[];
    learningResources: {
      skill: string;
      resources: { title: string; type: string; link: string }[];
    }[];
  };
  nextSteps?: string[];
}

export function ApplicationTracking() {
  const [applications] = useState<Application[]>([
    {
      id: "1",
      jobTitle: "Senior Frontend Engineer",
      company: "TechCorp",
      appliedDate: "Oct 10, 2025",
      status: "interview",
      matchScore: 94,
      lastUpdate: "2 hours ago",
      timeline: [
        { stage: "Application Submitted", date: "Oct 10", status: "completed" },
        { stage: "Resume Screening", date: "Oct 11", status: "completed" },
        { stage: "Technical Assessment", date: "Oct 13", status: "completed" },
        { stage: "Phone Interview", date: "Oct 15", status: "current" },
        { stage: "Final Interview", date: "TBD", status: "pending" },
        { stage: "Offer Decision", date: "TBD", status: "pending" }
      ],
      aiFeedback: {
        strengths: [
          "Your React and TypeScript expertise perfectly matches role requirements",
          "Strong portfolio demonstrates relevant project experience",
          "Communication skills rated highly based on application materials"
        ],
        gaps: [
          "Limited AWS cloud infrastructure experience",
          "Could strengthen system design knowledge for senior role"
        ],
        recommendations: [
          "Complete AWS Certified Developer course before technical interview",
          "Review system design patterns for scalable applications",
          "Prepare examples of leading projects with measurable impact"
        ],
        learningResources: [
          {
            skill: "AWS Cloud Infrastructure",
            resources: [
              { title: "AWS Certified Developer - Associate", type: "Course", link: "#" },
              { title: "AWS in Action", type: "Book", link: "#" },
              { title: "AWS CloudFormation Tutorial", type: "Video", link: "#" }
            ]
          },
          {
            skill: "System Design",
            resources: [
              { title: "Grokking System Design Interview", type: "Course", link: "#" },
              { title: "System Design Primer", type: "Article", link: "#" },
              { title: "Designing Data-Intensive Applications", type: "Book", link: "#" }
            ]
          }
        ]
      },
      nextSteps: [
        "Phone interview scheduled for Oct 15 at 2:00 PM PST",
        "Prepare questions about team structure and tech stack",
        "Review your portfolio projects to discuss in detail"
      ]
    },
    {
      id: "2",
      jobTitle: "Full Stack Developer",
      company: "InnovateLabs",
      appliedDate: "Oct 5, 2025",
      status: "rejected",
      matchScore: 89,
      lastUpdate: "3 days ago",
      timeline: [
        { stage: "Application Submitted", date: "Oct 5", status: "completed" },
        { stage: "Resume Screening", date: "Oct 6", status: "completed" },
        { stage: "Technical Assessment", date: "Oct 8", status: "completed" },
        { stage: "Decision", date: "Oct 12", status: "completed" }
      ],
      aiFeedback: {
        strengths: [
          "Technical assessment score: 85% - above average",
          "Full-stack versatility demonstrated well"
        ],
        gaps: [
          "PostgreSQL experience level didn't meet senior requirements",
          "Limited experience with Docker in production environments",
          "Competition: 78 applicants for 1 position"
        ],
        recommendations: [
          "Build a project using PostgreSQL to strengthen database skills",
          "Get hands-on with Docker through personal projects or courses",
          "Consider mid-level full-stack roles to build senior-level experience"
        ],
        learningResources: [
          {
            skill: "PostgreSQL",
            resources: [
              { title: "PostgreSQL Bootcamp", type: "Course", link: "#" },
              { title: "Database Design & Implementation", type: "Project", link: "#" }
            ]
          },
          {
            skill: "Docker & DevOps",
            resources: [
              { title: "Docker Mastery Course", type: "Course", link: "#" },
              { title: "Docker in Production", type: "Tutorial", link: "#" }
            ]
          }
        ]
      }
    },
    {
      id: "3",
      jobTitle: "React Developer",
      company: "StartupXYZ",
      appliedDate: "Oct 12, 2025",
      status: "screening",
      matchScore: 91,
      lastUpdate: "1 day ago",
      timeline: [
        { stage: "Application Submitted", date: "Oct 12", status: "completed" },
        { stage: "Resume Screening", date: "Oct 13", status: "current" },
        { stage: "Technical Assessment", date: "TBD", status: "pending" },
        { stage: "Interview", date: "TBD", status: "pending" },
        { stage: "Decision", date: "TBD", status: "pending" }
      ],
      nextSteps: [
        "Application under review by hiring team",
        "Expected response within 3-5 business days",
        "In the meantime, research the company's tech blog"
      ]
    },
    {
      id: "4",
      jobTitle: "Lead Software Engineer",
      company: "CloudScale Inc",
      appliedDate: "Oct 8, 2025",
      status: "applied",
      matchScore: 87,
      lastUpdate: "1 week ago",
      timeline: [
        { stage: "Application Submitted", date: "Oct 8", status: "completed" },
        { stage: "Resume Screening", date: "TBD", status: "pending" },
        { stage: "Assessment", date: "TBD", status: "pending" },
        { stage: "Interview", date: "TBD", status: "pending" }
      ]
    }
  ]);

  const getStatusColor = (status: Application["status"]) => {
    switch (status) {
      case "applied": return "bg-gray-500";
      case "screening": return "bg-blue-500";
      case "interview": return "bg-purple-500";
      case "offer": return "bg-green-500";
      case "rejected": return "bg-red-500";
    }
  };

  const getStatusLabel = (status: Application["status"]) => {
    switch (status) {
      case "applied": return "Application Submitted";
      case "screening": return "Under Review";
      case "interview": return "Interview Stage";
      case "offer": return "Offer Received";
      case "rejected": return "Not Selected";
    }
  };

  const activeApplications = applications.filter(a => a.status !== "rejected");
  const rejectedApplications = applications.filter(a => a.status === "rejected");

  return (
    <div className="space-y-6">
      <div>
        <h2>Application Tracker</h2>
        <p className="text-gray-600">Real-time updates and AI-powered feedback on your applications</p>
      </div>

      {/* Overview Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Total Applied
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl text-blue-600">{applications.length}</div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-purple-50 to-pink-50 border-2 border-purple-200">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <Clock className="h-4 w-4" />
              In Progress
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl text-purple-600">{activeApplications.length}</div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4" />
              Interview Stage
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl text-green-600">
              {applications.filter(a => a.status === "interview").length}
            </div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-orange-50 to-red-50 border-2 border-orange-200">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <Target className="h-4 w-4" />
              Avg Match
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl text-orange-600">
              {Math.round(applications.reduce((sum, a) => sum + a.matchScore, 0) / applications.length)}%
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Applications Tabs */}
      <Tabs defaultValue="active" className="space-y-4">
        <TabsList>
          <TabsTrigger value="active">Active ({activeApplications.length})</TabsTrigger>
          <TabsTrigger value="rejected">Archived ({rejectedApplications.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="active" className="space-y-4">
          {activeApplications.map((app) => (
            <Card key={app.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <h3>{app.jobTitle}</h3>
                      <Badge className={getStatusColor(app.status)}>
                        {getStatusLabel(app.status)}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600">{app.company}</p>
                    <div className="flex gap-4 mt-2 text-sm text-gray-600">
                      <div className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        Applied {app.appliedDate}
                      </div>
                      <div className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        Updated {app.lastUpdate}
                      </div>
                    </div>
                  </div>
                  <div className="text-center px-4 py-2 rounded-lg bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200">
                    <div className="text-2xl text-green-600">{app.matchScore}%</div>
                    <div className="text-xs text-gray-600">Match</div>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Timeline */}
                <div>
                  <div className="text-sm mb-3">Application Progress</div>
                  <div className="relative">
                    <div className="absolute top-4 left-0 right-0 h-0.5 bg-gray-200" />
                    <div className="relative flex justify-between">
                      {app.timeline.map((stage, index) => (
                        <div key={index} className="flex flex-col items-center">
                          <div
                            className={`h-8 w-8 rounded-full flex items-center justify-center border-2 z-10 ${
                              stage.status === "completed"
                                ? "bg-green-500 border-green-500"
                                : stage.status === "current"
                                ? "bg-blue-500 border-blue-500 animate-pulse"
                                : "bg-white border-gray-300"
                            }`}
                          >
                            {stage.status === "completed" ? (
                              <CheckCircle2 className="h-4 w-4 text-white" />
                            ) : stage.status === "current" ? (
                              <Clock className="h-4 w-4 text-white" />
                            ) : (
                              <div className="h-2 w-2 rounded-full bg-gray-300" />
                            )}
                          </div>
                          <div className="text-xs text-center mt-2 max-w-[80px]">
                            <div className={stage.status === "current" ? "font-medium" : ""}>
                              {stage.stage}
                            </div>
                            <div className="text-gray-500">{stage.date}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Next Steps */}
                {app.nextSteps && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Sparkles className="h-4 w-4 text-blue-600" />
                      <span className="text-sm text-blue-900">Next Steps</span>
                    </div>
                    <ul className="space-y-1">
                      {app.nextSteps.map((step, i) => (
                        <li key={i} className="text-sm text-gray-700">• {step}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* AI Feedback */}
                {app.aiFeedback && (
                  <div className="space-y-3">
                    <div className="flex items-center gap-2 mb-2">
                      <Brain className="h-4 w-4 text-purple-600" />
                      <span className="text-sm text-purple-900">AI Feedback & Recommendations</span>
                    </div>

                    <div className="grid md:grid-cols-2 gap-3">
                      <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                        <div className="flex items-center gap-2 mb-2">
                          <TrendingUp className="h-4 w-4 text-green-600" />
                          <span className="text-sm text-green-900">Your Strengths</span>
                        </div>
                        <ul className="space-y-1">
                          {app.aiFeedback.strengths.map((strength, i) => (
                            <li key={i} className="text-xs text-gray-700">• {strength}</li>
                          ))}
                        </ul>
                      </div>

                      <div className="bg-orange-50 border border-orange-200 rounded-lg p-3">
                        <div className="flex items-center gap-2 mb-2">
                          <AlertCircle className="h-4 w-4 text-orange-600" />
                          <span className="text-sm text-orange-900">Skill Gaps Identified</span>
                        </div>
                        <ul className="space-y-1">
                          {app.aiFeedback.gaps.map((gap, i) => (
                            <li key={i} className="text-xs text-gray-700">• {gap}</li>
                          ))}
                        </ul>
                      </div>
                    </div>

                    {/* Learning Recommendations */}
                    <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-4">
                      <div className="flex items-center gap-2 mb-3">
                        <BookOpen className="h-4 w-4 text-purple-600" />
                        <span className="text-sm text-purple-900">Recommended Learning Path</span>
                      </div>
                      {app.aiFeedback.learningResources.map((resource, i) => (
                        <div key={i} className="mb-3 last:mb-0">
                          <div className="text-sm mb-2">
                            <Badge variant="outline" className="mr-2">{resource.skill}</Badge>
                          </div>
                          <div className="grid gap-2 md:grid-cols-3">
                            {resource.resources.map((item, j) => (
                              <Button key={j} variant="outline" size="sm" className="justify-start text-xs">
                                <Lightbulb className="h-3 w-3 mr-2" />
                                {item.title}
                              </Button>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Action Recommendations */}
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                      <div className="flex items-center gap-2 mb-2">
                        <Target className="h-4 w-4 text-blue-600" />
                        <span className="text-sm text-blue-900">Action Items</span>
                      </div>
                      <ul className="space-y-1">
                        {app.aiFeedback.recommendations.map((rec, i) => (
                          <li key={i} className="text-xs text-gray-700 flex items-start gap-2">
                            <CheckCircle2 className="h-3 w-3 text-blue-600 flex-shrink-0 mt-0.5" />
                            {rec}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                <div className="flex gap-2 pt-2">
                  <Button variant="outline" size="sm" className="gap-2">
                    <MessageSquare className="h-3 w-3" />
                    Message Recruiter
                  </Button>
                  <Button variant="outline" size="sm" className="gap-2">
                    <Calendar className="h-3 w-3" />
                    View Details
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="rejected" className="space-y-4">
          {rejectedApplications.map((app) => (
            <Card key={app.id} className="opacity-75">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <h3>{app.jobTitle}</h3>
                      <Badge className="bg-red-500">Not Selected</Badge>
                    </div>
                    <p className="text-sm text-gray-600">{app.company}</p>
                    <div className="text-sm text-gray-600 mt-1">
                      Applied {app.appliedDate}
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* AI Feedback for Improvement */}
                {app.aiFeedback && (
                  <div className="space-y-3">
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <div className="flex items-center gap-2 mb-3">
                        <Brain className="h-4 w-4 text-blue-600" />
                        <span className="text-sm text-blue-900">Learning from This Application</span>
                      </div>

                      <div className="space-y-3">
                        <div>
                          <div className="text-xs text-gray-600 mb-1">What you did well:</div>
                          <ul className="space-y-1">
                            {app.aiFeedback.strengths.map((strength, i) => (
                              <li key={i} className="text-xs text-gray-700">✓ {strength}</li>
                            ))}
                          </ul>
                        </div>

                        <div>
                          <div className="text-xs text-gray-600 mb-1">Areas that need strengthening:</div>
                          <ul className="space-y-1">
                            {app.aiFeedback.gaps.map((gap, i) => (
                              <li key={i} className="text-xs text-gray-700">→ {gap}</li>
                            ))}
                          </ul>
                        </div>

                        <div>
                          <div className="text-xs text-gray-600 mb-2">Recommended next steps:</div>
                          {app.aiFeedback.learningResources.map((resource, i) => (
                            <div key={i} className="mb-2">
                              <Badge variant="outline" className="text-xs mb-1">{resource.skill}</Badge>
                              <div className="flex gap-2 flex-wrap">
                                {resource.resources.map((item, j) => (
                                  <Button key={j} variant="outline" size="sm" className="text-xs h-7">
                                    {item.title}
                                  </Button>
                                ))}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>

                    <Button variant="outline" size="sm" className="w-full gap-2">
                      <Award className="h-3 w-3" />
                      Start Learning Path
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </TabsContent>
      </Tabs>
    </div>
  );
}
