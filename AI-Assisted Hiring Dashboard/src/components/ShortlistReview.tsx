import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Avatar, AvatarFallback } from "./ui/avatar";
import { Textarea } from "./ui/textarea";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "./ui/dialog";
import { Star, Mail, Phone, MapPin, Award, Share2, CheckCircle2, X } from "lucide-react";
import { Progress } from "./ui/progress";
import { toast } from "sonner@2.0.3";

interface ShortlistCandidate {
  id: string;
  name: string;
  email: string;
  phone: string;
  location: string;
  currentRole: string;
  experience: string;
  fitScore: number;
  skills: string[];
  education: string;
  strengths: string[];
  concerns: string[];
  status: "pending" | "approved" | "rejected";
}

export function ShortlistReview() {
  const [candidates, setCandidates] = useState<ShortlistCandidate[]>([
    {
      id: "1",
      name: "Sarah Johnson",
      email: "sarah.j@email.com",
      phone: "+1 (555) 123-4567",
      location: "New York, NY",
      currentRole: "Senior Frontend Engineer",
      experience: "6 years",
      fitScore: 94,
      skills: ["React", "TypeScript", "Node.js", "AWS"],
      education: "BS Computer Science, MIT",
      strengths: ["Strong React expertise", "Leadership experience", "Excellent communication"],
      concerns: ["Limited backend experience"],
      status: "pending",
    },
    {
      id: "2",
      name: "Michael Chen",
      email: "m.chen@email.com",
      phone: "+1 (555) 234-5678",
      location: "San Francisco, CA",
      currentRole: "Lead Backend Engineer",
      experience: "8 years",
      fitScore: 89,
      skills: ["Python", "Django", "PostgreSQL", "Docker"],
      education: "MS Software Engineering, Stanford",
      strengths: ["Scalable systems design", "Team leadership", "Strong technical skills"],
      concerns: ["May be overqualified", "Salary expectations high"],
      status: "pending",
    },
    {
      id: "3",
      name: "Emily Rodriguez",
      email: "emily.r@email.com",
      phone: "+1 (555) 345-6789",
      location: "Austin, TX",
      currentRole: "Full Stack Developer",
      experience: "5 years",
      fitScore: 87,
      skills: ["React", "Vue.js", "GraphQL", "MongoDB"],
      education: "BS Computer Science, UT Austin",
      strengths: ["Full stack expertise", "Quick learner", "Modern tech stack"],
      concerns: ["Requires relocation support"],
      status: "pending",
    },
  ]);

  const [shareNotes, setShareNotes] = useState("");

  const updateCandidateStatus = (id: string, status: "approved" | "rejected") => {
    setCandidates((prev) =>
      prev.map((c) => (c.id === id ? { ...c, status } : c))
    );
    toast.success(`Candidate ${status === "approved" ? "approved" : "rejected"}`);
  };

  const handleShare = () => {
    const approved = candidates.filter((c) => c.status === "approved");
    if (approved.length === 0) {
      toast.error("Please approve at least one candidate before sharing");
      return;
    }
    toast.success(`Shortlist shared with hiring manager (${approved.length} candidates)`);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2>Shortlist Review</h2>
          <p className="text-gray-600">Review and approve candidates for hiring manager</p>
        </div>
        <Dialog>
          <DialogTrigger asChild>
            <Button className="gap-2">
              <Share2 className="h-4 w-4" />
              Share with Hiring Manager
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Share Shortlist</DialogTitle>
              <DialogDescription>
                Send the approved candidates to the hiring manager for final review
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 pt-4">
              <div>
                <p className="text-sm mb-2">
                  Approved Candidates: {candidates.filter((c) => c.status === "approved").length}
                </p>
                <div className="space-y-2">
                  {candidates
                    .filter((c) => c.status === "approved")
                    .map((c) => (
                      <div key={c.id} className="flex items-center gap-2 text-sm">
                        <CheckCircle2 className="h-4 w-4 text-green-600" />
                        <span>{c.name}</span>
                        <Badge variant="secondary">{c.fitScore}%</Badge>
                      </div>
                    ))}
                </div>
              </div>
              <div>
                <label className="text-sm">Add a note (optional)</label>
                <Textarea
                  placeholder="Add any additional context for the hiring manager..."
                  value={shareNotes}
                  onChange={(e) => setShareNotes(e.target.value)}
                  className="mt-2"
                />
              </div>
              <Button onClick={handleShare} className="w-full">
                Send Shortlist
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm">Total Shortlisted</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl">{candidates.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm">Approved</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl text-green-600">
              {candidates.filter((c) => c.status === "approved").length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm">Pending Review</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl text-yellow-600">
              {candidates.filter((c) => c.status === "pending").length}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="space-y-4">
        {candidates.map((candidate) => (
          <Card key={candidate.id} className={
            candidate.status === "approved" ? "border-green-200 bg-green-50" :
            candidate.status === "rejected" ? "border-gray-200 bg-gray-50 opacity-60" :
            ""
          }>
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
                      <div className="flex items-center gap-2">
                        <h3>{candidate.name}</h3>
                        {candidate.status === "approved" && (
                          <Badge className="bg-green-600 gap-1">
                            <CheckCircle2 className="h-3 w-3" />
                            Approved
                          </Badge>
                        )}
                        {candidate.status === "rejected" && (
                          <Badge variant="secondary">Rejected</Badge>
                        )}
                      </div>
                      <p className="text-sm text-gray-600">{candidate.currentRole}</p>
                      <div className="flex items-center gap-3 mt-2 text-sm text-gray-600">
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
                    <div className="text-center px-4 py-2 rounded-lg bg-indigo-50 border border-indigo-200">
                      <div className="text-2xl text-indigo-600">
                        {candidate.fitScore}%
                      </div>
                      <div className="text-xs text-gray-600">AI Fit Score</div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-sm text-gray-600 mb-1">
                        <Mail className="h-3 w-3 inline mr-1" />
                        Email
                      </div>
                      <p className="text-sm">{candidate.email}</p>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600 mb-1">
                        <Phone className="h-3 w-3 inline mr-1" />
                        Phone
                      </div>
                      <p className="text-sm">{candidate.phone}</p>
                    </div>
                  </div>

                  <div>
                    <div className="text-sm text-gray-600 mb-2">Education</div>
                    <p className="text-sm">{candidate.education}</p>
                  </div>

                  <div>
                    <div className="text-sm text-gray-600 mb-2">Skills</div>
                    <div className="flex gap-2 flex-wrap">
                      {candidate.skills.map((skill) => (
                        <Badge key={skill} variant="outline">
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-sm text-gray-600 mb-2 flex items-center gap-1">
                        <Star className="h-3 w-3 text-green-600" />
                        Strengths
                      </div>
                      <ul className="text-sm space-y-1">
                        {candidate.strengths.map((strength, i) => (
                          <li key={i} className="text-gray-700">• {strength}</li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600 mb-2">Considerations</div>
                      <ul className="text-sm space-y-1">
                        {candidate.concerns.map((concern, i) => (
                          <li key={i} className="text-gray-700">• {concern}</li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {candidate.status === "pending" && (
                    <div className="flex gap-2 pt-2">
                      <Button
                        onClick={() => updateCandidateStatus(candidate.id, "approved")}
                        className="gap-2 bg-green-600 hover:bg-green-700"
                      >
                        <CheckCircle2 className="h-4 w-4" />
                        Approve
                      </Button>
                      <Button
                        onClick={() => updateCandidateStatus(candidate.id, "rejected")}
                        variant="outline"
                        className="gap-2"
                      >
                        <X className="h-4 w-4" />
                        Reject
                      </Button>
                      <Button variant="outline">View Full Profile</Button>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
