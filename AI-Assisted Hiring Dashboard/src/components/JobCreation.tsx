import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Badge } from "./ui/badge";
import { Sparkles, Upload, X } from "lucide-react";
import { toast } from "sonner@2.0.3";

export function JobCreation() {
  const [rawJD, setRawJD] = useState("");
  const [parsed, setParsed] = useState(false);
  const [jobData, setJobData] = useState({
    title: "",
    skills: [] as string[],
    experience: "",
    location: "",
    department: "",
    employmentType: "",
  });
  const [newSkill, setNewSkill] = useState("");

  const handleParse = () => {
    // Simulate AI parsing
    const mockParsedData = {
      title: "Senior Full Stack Engineer",
      skills: ["React", "Node.js", "TypeScript", "AWS", "PostgreSQL"],
      experience: "5+ years",
      location: "San Francisco, CA (Remote)",
      department: "Engineering",
      employmentType: "Full-time",
    };
    setJobData(mockParsedData);
    setParsed(true);
    toast.success("Job description parsed successfully!");
  };

  const addSkill = () => {
    if (newSkill && !jobData.skills.includes(newSkill)) {
      setJobData({ ...jobData, skills: [...jobData.skills, newSkill] });
      setNewSkill("");
    }
  };

  const removeSkill = (skill: string) => {
    setJobData({
      ...jobData,
      skills: jobData.skills.filter((s) => s !== skill),
    });
  };

  const handleSave = () => {
    toast.success("Job posted successfully!");
  };

  return (
    <div className="space-y-6">
      <div>
        <h2>Create New Job</h2>
        <p className="text-gray-600">Upload or paste a job description and let AI extract the details</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Job Description Input</CardTitle>
            <CardDescription>Paste or upload your job description</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Textarea
                placeholder="Paste job description here..."
                className="min-h-[300px]"
                value={rawJD}
                onChange={(e) => setRawJD(e.target.value)}
              />
            </div>
            <div className="flex gap-2">
              <Button onClick={handleParse} disabled={!rawJD} className="gap-2">
                <Sparkles className="h-4 w-4" />
                Parse with AI
              </Button>
              <Button variant="outline" className="gap-2">
                <Upload className="h-4 w-4" />
                Upload File
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Extracted Details</CardTitle>
            <CardDescription>Review and edit AI-parsed information</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {!parsed ? (
              <div className="flex items-center justify-center h-[300px] text-gray-400">
                <div className="text-center">
                  <Sparkles className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p>Parse a job description to see extracted details</p>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <Label>Job Title</Label>
                  <Input
                    value={jobData.title}
                    onChange={(e) => setJobData({ ...jobData, title: e.target.value })}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Experience Required</Label>
                    <Input
                      value={jobData.experience}
                      onChange={(e) => setJobData({ ...jobData, experience: e.target.value })}
                    />
                  </div>
                  <div>
                    <Label>Employment Type</Label>
                    <Input
                      value={jobData.employmentType}
                      onChange={(e) => setJobData({ ...jobData, employmentType: e.target.value })}
                    />
                  </div>
                </div>

                <div>
                  <Label>Location</Label>
                  <Input
                    value={jobData.location}
                    onChange={(e) => setJobData({ ...jobData, location: e.target.value })}
                  />
                </div>

                <div>
                  <Label>Department</Label>
                  <Input
                    value={jobData.department}
                    onChange={(e) => setJobData({ ...jobData, department: e.target.value })}
                  />
                </div>

                <div>
                  <Label>Required Skills</Label>
                  <div className="flex gap-2 mt-2 mb-2 flex-wrap">
                    {jobData.skills.map((skill) => (
                      <Badge key={skill} variant="secondary" className="gap-1">
                        {skill}
                        <X
                          className="h-3 w-3 cursor-pointer"
                          onClick={() => removeSkill(skill)}
                        />
                      </Badge>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <Input
                      placeholder="Add skill..."
                      value={newSkill}
                      onChange={(e) => setNewSkill(e.target.value)}
                      onKeyPress={(e) => e.key === "Enter" && addSkill()}
                    />
                    <Button onClick={addSkill} variant="outline">
                      Add
                    </Button>
                  </div>
                </div>

                <Button onClick={handleSave} className="w-full">
                  Post Job
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
