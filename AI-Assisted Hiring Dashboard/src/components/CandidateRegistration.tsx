import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Progress } from "./ui/progress";
import { Badge } from "./ui/badge";
import { 
  Upload, 
  Linkedin, 
  FileText, 
  CheckCircle2, 
  Loader2,
  Sparkles,
  User,
  Mail,
  Phone,
  MapPin,
  Briefcase
} from "lucide-react";
import { toast } from "sonner@2.0.3";
import hiremindLogo from "figma:asset/546a4a954d15091706c425f397a221b3336468dd.png";

interface CandidateRegistrationProps {
  onComplete: () => void;
}

export function CandidateRegistration({ onComplete }: CandidateRegistrationProps) {
  const [step, setStep] = useState<"upload" | "parsing" | "review">("upload");
  const [uploadMethod, setUploadMethod] = useState<"resume" | "linkedin" | null>(null);
  const [parsingProgress, setParsingProgress] = useState(0);
  const [parsedData, setParsedData] = useState({
    name: "Alex Morgan",
    email: "alex.morgan@email.com",
    phone: "+1 (555) 123-4567",
    location: "San Francisco, CA",
    title: "Senior Software Engineer",
    experience: "7 years",
    skills: ["React", "TypeScript", "Node.js", "Python", "AWS", "Docker", "GraphQL", "MongoDB"],
    education: "BS Computer Science, UC Berkeley",
    summary: "Passionate software engineer with 7 years of experience building scalable web applications. Specialized in modern JavaScript frameworks and cloud architecture.",
  });

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setUploadMethod("resume");
      simulateParsing();
    }
  };

  const handleLinkedInConnect = () => {
    setUploadMethod("linkedin");
    simulateParsing();
  };

  const simulateParsing = () => {
    setStep("parsing");
    setParsingProgress(0);
    
    const interval = setInterval(() => {
      setParsingProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          setTimeout(() => {
            setStep("review");
            toast.success("Profile parsed successfully!");
          }, 500);
          return 100;
        }
        return prev + 10;
      });
    }, 200);
  };

  const handleComplete = () => {
    onComplete();
  };

  if (step === "upload") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-4">
        <Card className="w-full max-w-2xl">
          <CardHeader className="text-center">
            <div className="flex justify-center mb-4">
              <img 
                src={hiremindLogo} 
                alt="HireMind" 
                className="h-20 w-auto object-contain"
              />
            </div>
            <CardTitle>Welcome to HireMind!</CardTitle>
            <CardDescription className="text-base">
              Let's create your profile in seconds using AI
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid gap-4 md:grid-cols-2">
              {/* Resume Upload */}
              <div 
                className="relative group"
                onClick={() => document.getElementById('resume-upload')?.click()}
              >
                <input
                  id="resume-upload"
                  type="file"
                  accept=".pdf,.doc,.docx"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                <Card className="cursor-pointer border-2 border-dashed hover:border-blue-500 hover:bg-blue-50 transition-all h-full">
                  <CardContent className="flex flex-col items-center justify-center p-8 space-y-4">
                    <div className="h-16 w-16 rounded-full bg-blue-100 flex items-center justify-center group-hover:bg-blue-200 transition-colors">
                      <Upload className="h-8 w-8 text-blue-600" />
                    </div>
                    <div className="text-center">
                      <h3 className="mb-1">Upload Resume</h3>
                      <p className="text-sm text-gray-600">
                        PDF, DOC, or DOCX
                      </p>
                    </div>
                    <Button variant="outline" size="sm">
                      <FileText className="h-4 w-4 mr-2" />
                      Choose File
                    </Button>
                  </CardContent>
                </Card>
              </div>

              {/* LinkedIn Connect */}
              <Card 
                className="cursor-pointer border-2 border-dashed hover:border-blue-500 hover:bg-blue-50 transition-all h-full"
                onClick={handleLinkedInConnect}
              >
                <CardContent className="flex flex-col items-center justify-center p-8 space-y-4">
                  <div className="h-16 w-16 rounded-full bg-blue-100 flex items-center justify-center hover:bg-blue-200 transition-colors">
                    <Linkedin className="h-8 w-8 text-blue-600" />
                  </div>
                  <div className="text-center">
                    <h3 className="mb-1">Connect LinkedIn</h3>
                    <p className="text-sm text-gray-600">
                      Import your profile
                    </p>
                  </div>
                  <Button variant="outline" size="sm" className="bg-[#0077B5] text-white hover:bg-[#006399] hover:text-white">
                    <Linkedin className="h-4 w-4 mr-2" />
                    Connect
                  </Button>
                </CardContent>
              </Card>
            </div>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-white px-2 text-gray-500">Or</span>
              </div>
            </div>

            <div className="text-center">
              <Button variant="ghost" onClick={() => setStep("review")}>
                Skip and fill manually
              </Button>
            </div>

            <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <Sparkles className="h-5 w-5 text-purple-600 mt-0.5" />
                <div>
                  <div className="text-sm text-purple-900 mb-1">AI-Powered Profile Creation</div>
                  <p className="text-sm text-gray-700">
                    Our AI will automatically extract your experience, skills, and education to create 
                    a comprehensive profile. You can review and edit everything before saving.
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (step === "parsing") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-4">
        <Card className="w-full max-w-2xl">
          <CardContent className="py-12">
            <div className="flex flex-col items-center space-y-6">
              <div className="h-20 w-20 rounded-full bg-gradient-to-r from-blue-600 to-purple-600 flex items-center justify-center animate-pulse">
                <Loader2 className="h-10 w-10 text-white animate-spin" />
              </div>
              <div className="text-center space-y-2">
                <h2>AI is analyzing your {uploadMethod === "resume" ? "resume" : "LinkedIn profile"}...</h2>
                <p className="text-gray-600">This will only take a moment</p>
              </div>
              
              <div className="w-full max-w-md space-y-3">
                <Progress value={parsingProgress} className="h-3" />
                <div className="text-center text-sm text-gray-600">{parsingProgress}%</div>
              </div>

              <div className="grid gap-2 w-full max-w-md">
                <div className={`flex items-center gap-2 text-sm ${parsingProgress >= 20 ? 'text-green-600' : 'text-gray-400'}`}>
                  {parsingProgress >= 20 ? <CheckCircle2 className="h-4 w-4" /> : <Loader2 className="h-4 w-4 animate-spin" />}
                  Extracting personal information
                </div>
                <div className={`flex items-center gap-2 text-sm ${parsingProgress >= 40 ? 'text-green-600' : 'text-gray-400'}`}>
                  {parsingProgress >= 40 ? <CheckCircle2 className="h-4 w-4" /> : <Loader2 className="h-4 w-4 animate-spin" />}
                  Identifying skills and technologies
                </div>
                <div className={`flex items-center gap-2 text-sm ${parsingProgress >= 60 ? 'text-green-600' : 'text-gray-400'}`}>
                  {parsingProgress >= 60 ? <CheckCircle2 className="h-4 w-4" /> : <Loader2 className="h-4 w-4 animate-spin" />}
                  Parsing work experience
                </div>
                <div className={`flex items-center gap-2 text-sm ${parsingProgress >= 80 ? 'text-green-600' : 'text-gray-400'}`}>
                  {parsingProgress >= 80 ? <CheckCircle2 className="h-4 w-4" /> : <Loader2 className="h-4 w-4 animate-spin" />}
                  Analyzing education background
                </div>
                <div className={`flex items-center gap-2 text-sm ${parsingProgress >= 100 ? 'text-green-600' : 'text-gray-400'}`}>
                  {parsingProgress >= 100 ? <CheckCircle2 className="h-4 w-4" /> : <Loader2 className="h-4 w-4 animate-spin" />}
                  Finalizing your profile
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-4 py-8">
      <div className="max-w-4xl mx-auto">
        <Card className="mb-6 border-2 border-green-200 bg-green-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-full bg-green-500 flex items-center justify-center">
                <CheckCircle2 className="h-6 w-6 text-white" />
              </div>
              <div>
                <h3 className="text-green-900">Profile Parsed Successfully!</h3>
                <p className="text-sm text-green-700">Review your information below and make any edits</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-5 w-5" />
              Your Profile
            </CardTitle>
            <CardDescription>Review and edit your AI-parsed information</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Personal Information */}
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label>Full Name</Label>
                <div className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg border border-gray-200">
                  <User className="h-4 w-4 text-gray-500" />
                  <Input 
                    value={parsedData.name} 
                    onChange={(e) => setParsedData({...parsedData, name: e.target.value})}
                    className="border-0 bg-transparent p-0 h-auto"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label>Email</Label>
                <div className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg border border-gray-200">
                  <Mail className="h-4 w-4 text-gray-500" />
                  <Input 
                    value={parsedData.email} 
                    onChange={(e) => setParsedData({...parsedData, email: e.target.value})}
                    className="border-0 bg-transparent p-0 h-auto"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label>Phone</Label>
                <div className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg border border-gray-200">
                  <Phone className="h-4 w-4 text-gray-500" />
                  <Input 
                    value={parsedData.phone} 
                    onChange={(e) => setParsedData({...parsedData, phone: e.target.value})}
                    className="border-0 bg-transparent p-0 h-auto"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label>Location</Label>
                <div className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg border border-gray-200">
                  <MapPin className="h-4 w-4 text-gray-500" />
                  <Input 
                    value={parsedData.location} 
                    onChange={(e) => setParsedData({...parsedData, location: e.target.value})}
                    className="border-0 bg-transparent p-0 h-auto"
                  />
                </div>
              </div>
            </div>

            {/* Professional Info */}
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label>Current Title</Label>
                <div className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg border border-gray-200">
                  <Briefcase className="h-4 w-4 text-gray-500" />
                  <Input 
                    value={parsedData.title} 
                    onChange={(e) => setParsedData({...parsedData, title: e.target.value})}
                    className="border-0 bg-transparent p-0 h-auto"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label>Experience</Label>
                <Input 
                  value={parsedData.experience} 
                  onChange={(e) => setParsedData({...parsedData, experience: e.target.value})}
                />
              </div>
            </div>

            {/* Skills */}
            <div className="space-y-2">
              <Label>Skills (AI-detected)</Label>
              <div className="flex gap-2 flex-wrap p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200">
                {parsedData.skills.map((skill) => (
                  <Badge key={skill} className="bg-blue-600">
                    {skill}
                  </Badge>
                ))}
              </div>
            </div>

            {/* Education */}
            <div className="space-y-2">
              <Label>Education</Label>
              <Input 
                value={parsedData.education} 
                onChange={(e) => setParsedData({...parsedData, education: e.target.value})}
              />
            </div>

            {/* Summary */}
            <div className="space-y-2">
              <Label>Professional Summary (AI-generated)</Label>
              <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                <p className="text-sm text-gray-700">{parsedData.summary}</p>
              </div>
            </div>

            <div className="flex gap-3 pt-4">
              <Button onClick={handleComplete} size="lg" className="flex-1 gap-2">
                <CheckCircle2 className="h-5 w-5" />
                Complete Profile
              </Button>
              <Button variant="outline" size="lg" onClick={() => setStep("upload")}>
                Start Over
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
