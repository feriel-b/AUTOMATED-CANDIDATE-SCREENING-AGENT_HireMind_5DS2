import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Upload, FileText, CheckCircle2, Sparkles } from "lucide-react";
import { toast } from "sonner@2.0.3";
import { Avatar, AvatarFallback } from "./ui/avatar";

interface Candidate {
  id: string;
  name: string;
  email: string;
  phone: string;
  location: string;
  skills: string[];
  experience: string;
  education: string;
  currentRole: string;
}

export function CandidateImport() {
  const [uploading, setUploading] = useState(false);
  const [candidates, setCandidates] = useState<Candidate[]>([]);

  const mockCandidates: Candidate[] = [
    {
      id: "1",
      name: "Sarah Johnson",
      email: "sarah.j@email.com",
      phone: "+1 (555) 123-4567",
      location: "New York, NY",
      skills: ["React", "TypeScript", "Node.js", "AWS"],
      experience: "6 years",
      education: "BS Computer Science, MIT",
      currentRole: "Senior Frontend Engineer",
    },
    {
      id: "2",
      name: "Michael Chen",
      email: "m.chen@email.com",
      phone: "+1 (555) 234-5678",
      location: "San Francisco, CA",
      skills: ["Python", "Django", "PostgreSQL", "Docker"],
      experience: "8 years",
      education: "MS Software Engineering, Stanford",
      currentRole: "Lead Backend Engineer",
    },
    {
      id: "3",
      name: "Emily Rodriguez",
      email: "emily.r@email.com",
      phone: "+1 (555) 345-6789",
      location: "Austin, TX",
      skills: ["React", "Vue.js", "GraphQL", "MongoDB"],
      experience: "5 years",
      education: "BS Computer Science, UT Austin",
      currentRole: "Full Stack Developer",
    },
    {
      id: "4",
      name: "David Kim",
      email: "david.kim@email.com",
      phone: "+1 (555) 456-7890",
      location: "Seattle, WA",
      skills: ["Java", "Spring Boot", "Kubernetes", "AWS"],
      experience: "7 years",
      education: "MS Computer Science, University of Washington",
      currentRole: "Senior Software Engineer",
    },
  ];

  const handleUpload = () => {
    setUploading(true);
    setTimeout(() => {
      setCandidates(mockCandidates);
      setUploading(false);
      toast.success(`Successfully imported ${mockCandidates.length} resumes!`);
    }, 2000);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2>Import Candidates</h2>
        <p className="text-gray-600">Upload resumes and let AI extract candidate information</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Resume Upload</CardTitle>
          <CardDescription>Upload multiple resumes (PDF, DOCX supported)</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-indigo-400 transition-colors">
            <Upload className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <h3 className="mb-2">Drop files here or click to upload</h3>
            <p className="text-sm text-gray-500 mb-4">Supports PDF and DOCX files, up to 10MB each</p>
            <Button onClick={handleUpload} disabled={uploading} className="gap-2">
              {uploading ? (
                <>
                  <Sparkles className="h-4 w-4 animate-pulse" />
                  Processing with AI...
                </>
              ) : (
                <>
                  <Upload className="h-4 w-4" />
                  Select Files
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {candidates.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle2 className="h-5 w-5 text-green-600" />
                  Extracted Candidates
                </CardTitle>
                <CardDescription>AI has extracted information from {candidates.length} resumes</CardDescription>
              </div>
              <Button>Proceed to Screening</Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {candidates.map((candidate) => (
                <Card key={candidate.id}>
                  <CardContent className="pt-6">
                    <div className="flex items-start gap-4">
                      <Avatar className="h-12 w-12">
                        <AvatarFallback className="bg-indigo-100 text-indigo-600">
                          {candidate.name.split(" ").map(n => n[0]).join("")}
                        </AvatarFallback>
                      </Avatar>
                      <div className="flex-1 space-y-3">
                        <div>
                          <h3>{candidate.name}</h3>
                          <p className="text-sm text-gray-600">{candidate.currentRole}</p>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-3 text-sm">
                          <div>
                            <span className="text-gray-500">Email:</span> {candidate.email}
                          </div>
                          <div>
                            <span className="text-gray-500">Phone:</span> {candidate.phone}
                          </div>
                          <div>
                            <span className="text-gray-500">Location:</span> {candidate.location}
                          </div>
                          <div>
                            <span className="text-gray-500">Experience:</span> {candidate.experience}
                          </div>
                        </div>

                        <div>
                          <div className="text-sm text-gray-500 mb-1">Education</div>
                          <p className="text-sm">{candidate.education}</p>
                        </div>

                        <div>
                          <div className="text-sm text-gray-500 mb-2">Skills Extracted</div>
                          <div className="flex gap-2 flex-wrap">
                            {candidate.skills.map((skill) => (
                              <Badge key={skill} variant="secondary">
                                {skill}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
