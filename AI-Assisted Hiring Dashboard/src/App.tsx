import { useState } from "react";
import { LoginScreen } from "./components/LoginScreen";
import { JobCreation } from "./components/JobCreation";
import { CandidateImport } from "./components/CandidateImport";
import { AutomatedScreening } from "./components/AutomatedScreening";
import { AIInsightsDashboard } from "./components/AIInsightsDashboard";
import { ShortlistReview } from "./components/ShortlistReview";
import { CommunicationAutomation } from "./components/CommunicationAutomation";
import { HiringManagerShortlist } from "./components/HiringManagerShortlist";
import { AIInterviewAssistant } from "./components/AIInterviewAssistant";
import { EvaluationSupport } from "./components/EvaluationSupport";
import { DecisionDashboard } from "./components/DecisionDashboard";
import { CandidateRegistration } from "./components/CandidateRegistration";
import { JobRecommendations } from "./components/JobRecommendations";
import { InterviewSimulation } from "./components/InterviewSimulation";
import { InterviewPracticeIntegrated } from "./components/InterviewPracticeIntegrated";
import { ApplicationTracking } from "./components/ApplicationTracking";
import { Button } from "./components/ui/button";
import { Toaster } from "./components/ui/sonner";
import {
  Briefcase,
  Upload,
  Users,
  BarChart3,
  Star,
  MessageSquare,
  LogOut,
  Menu,
  Target,
  Clipboard,
  TrendingUp,
  Sparkles,
  FileText,
  Play,
} from "lucide-react";
import hiremindLogo from "figma:asset/546a4a954d15091706c425f397a221b3336468dd.png";

type Screen =
  | "login"
  | "job-creation"
  | "candidate-import"
  | "screening"
  | "insights"
  | "shortlist"
  | "communication"
  | "hm-shortlist"
  | "hm-interview"
  | "hm-evaluation"
  | "hm-decision"
  | "candidate-registration"
  | "candidate-jobs"
  | "candidate-practice"
  | "candidate-tracking";

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<Screen>("login");
  const [userRole, setUserRole] = useState<string>("");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [selectedCandidateId, setSelectedCandidateId] = useState<string>("");
  const [candidateRegistered, setCandidateRegistered] = useState(false);

  const handleLogin = (role: string) => {
    setUserRole(role);
    if (role === "hiring-manager") {
      setCurrentScreen("hm-shortlist");
    } else if (role === "candidate") {
      setCurrentScreen("candidate-registration");
    } else {
      setCurrentScreen("job-creation");
    }
  };

  const handleLogout = () => {
    setUserRole("");
    setCurrentScreen("login");
    setSelectedCandidateId("");
    setCandidateRegistered(false);
  };

  const recruiterNavItems = [
    { id: "job-creation" as Screen, label: "Create Job", icon: Briefcase },
    { id: "candidate-import" as Screen, label: "Import Candidates", icon: Upload },
    { id: "screening" as Screen, label: "AI Screening", icon: Users },
    { id: "insights" as Screen, label: "AI Insights", icon: BarChart3 },
    { id: "shortlist" as Screen, label: "Shortlist Review", icon: Star },
    { id: "communication" as Screen, label: "Communication", icon: MessageSquare },
  ];

  const hiringManagerNavItems = [
    { id: "hm-shortlist" as Screen, label: "Candidate Shortlist", icon: Users },
    { id: "hm-interview" as Screen, label: "Interview Assistant", icon: Clipboard },
    { id: "hm-evaluation" as Screen, label: "Evaluation", icon: BarChart3 },
    { id: "hm-decision" as Screen, label: "Decision Dashboard", icon: Target },
  ];

  const candidateNavItems = [
    { id: "candidate-jobs" as Screen, label: "Job Matches", icon: Sparkles },
    { id: "candidate-practice" as Screen, label: "Interview Practice", icon: Play },
    { id: "candidate-tracking" as Screen, label: "My Applications", icon: FileText },
  ];

  const navItems = 
    userRole === "hiring-manager" ? hiringManagerNavItems : 
    userRole === "candidate" ? candidateNavItems :
    recruiterNavItems;

  if (currentScreen === "login") {
    return (
      <>
        <LoginScreen onLogin={handleLogin} />
        <Toaster />
      </>
    );
  }

  // Candidate registration flow
  if (userRole === "candidate" && currentScreen === "candidate-registration") {
    return (
      <>
        <CandidateRegistration onComplete={() => {
          setCandidateRegistered(true);
          setCurrentScreen("candidate-jobs");
        }} />
        <Toaster />
      </>
    );
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? "w-64" : "w-20"
        } bg-white border-r border-gray-200 transition-all duration-300 flex flex-col`}
      >
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            {sidebarOpen ? (
              <div className="flex items-center gap-2">
                <img 
                  src={hiremindLogo} 
                  alt="HireMind" 
                  className="h-8 w-auto object-contain"
                />
                <div className="text-xs text-gray-500">
                  {userRole === "hiring-manager" ? "Manager Portal" : 
                   userRole === "candidate" ? "Candidate Portal" :
                   "Recruiter Portal"}
                </div>
              </div>
            ) : (
              <img 
                src={hiremindLogo} 
                alt="HireMind" 
                className="h-8 w-8 object-contain mx-auto"
              />
            )}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className={!sidebarOpen ? "hidden" : ""}
            >
              <Menu className="h-4 w-4" />
            </Button>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          {navItems.map((item) => (
            <Button
              key={item.id}
              variant={currentScreen === item.id ? "default" : "ghost"}
              className={`w-full ${sidebarOpen ? "justify-start" : "justify-center"} gap-3`}
              onClick={() => setCurrentScreen(item.id)}
            >
              <item.icon className="h-4 w-4" />
              {sidebarOpen && <span>{item.label}</span>}
            </Button>
          ))}
        </nav>

        <div className="p-4 border-t border-gray-200">
          <Button
            variant="ghost"
            className={`w-full ${sidebarOpen ? "justify-start" : "justify-center"} gap-3 text-red-600 hover:text-red-700 hover:bg-red-50`}
            onClick={handleLogout}
          >
            <LogOut className="h-4 w-4" />
            {sidebarOpen && <span>Logout</span>}
          </Button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <div className="p-8 max-w-7xl mx-auto">
          {/* Recruiter Screens */}
          {currentScreen === "job-creation" && <JobCreation />}
          {currentScreen === "candidate-import" && <CandidateImport />}
          {currentScreen === "screening" && <AutomatedScreening />}
          {currentScreen === "insights" && <AIInsightsDashboard />}
          {currentScreen === "shortlist" && <ShortlistReview />}
          {currentScreen === "communication" && <CommunicationAutomation />}
          
          {/* Hiring Manager Screens */}
          {currentScreen === "hm-shortlist" && (
            <HiringManagerShortlist 
              onViewCandidate={(id) => {
                setSelectedCandidateId(id);
                setCurrentScreen("hm-interview");
              }}
              onScheduleInterview={(id) => {
                setSelectedCandidateId(id);
              }}
            />
          )}
          {currentScreen === "hm-interview" && (
            <AIInterviewAssistant 
              candidateId={selectedCandidateId}
              onBack={() => setCurrentScreen("hm-shortlist")}
              onStartEvaluation={() => setCurrentScreen("hm-evaluation")}
            />
          )}
          {currentScreen === "hm-evaluation" && (
            <EvaluationSupport 
              candidateId={selectedCandidateId}
              onBack={() => setCurrentScreen("hm-interview")}
              onCompleteEvaluation={() => setCurrentScreen("hm-decision")}
            />
          )}
          {currentScreen === "hm-decision" && <DecisionDashboard />}
          
          {/* Candidate Screens */}
          {currentScreen === "candidate-jobs" && <JobRecommendations />}
          {currentScreen === "candidate-practice" && <InterviewPracticeIntegrated />}
          {currentScreen === "candidate-tracking" && <ApplicationTracking />}
        </div>
      </main>

      <Toaster />
    </div>
  );
}
