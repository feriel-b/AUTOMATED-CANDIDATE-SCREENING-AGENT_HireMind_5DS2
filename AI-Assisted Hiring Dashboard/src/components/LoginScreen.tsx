import { Button } from "./ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Users, Building2, Sparkles } from "lucide-react";
import hiremindLogo from "figma:asset/546a4a954d15091706c425f397a221b3336468dd.png";

interface LoginScreenProps {
  onLogin: (role: string) => void;
}

export function LoginScreen({ onLogin }: LoginScreenProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            <img 
              src={hiremindLogo} 
              alt="HireMind" 
              className="h-20 w-auto object-contain"
            />
          </div>
          <CardDescription className="text-base mt-2">
            Intelligent recruitment powered by AI
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <h3 className="text-sm text-gray-600">Sign in with</h3>
            <div className="space-y-2">
              <Button variant="outline" className="w-full justify-start gap-2">
                <svg className="h-5 w-5" viewBox="0 0 24 24">
                  <path
                    fill="currentColor"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  />
                  <path
                    fill="currentColor"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  />
                  <path
                    fill="currentColor"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                  />
                  <path
                    fill="currentColor"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                  />
                </svg>
                Continue with Google
              </Button>
              <Button variant="outline" className="w-full justify-start gap-2">
                <Building2 className="h-5 w-5" />
                Continue with Microsoft SSO
              </Button>
            </div>
          </div>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-white px-2 text-gray-500">Select your role</span>
            </div>
          </div>

          <div className="space-y-2">
            <Button
              onClick={() => onLogin("candidate")}
              className="w-full justify-start gap-3 h-auto py-4 border-2 border-purple-200 bg-gradient-to-r from-purple-50 to-pink-50 hover:from-purple-100 hover:to-pink-100"
              variant="outline"
            >
              <div className="h-10 w-10 rounded-lg bg-purple-100 flex items-center justify-center">
                <Sparkles className="h-5 w-5 text-purple-600" />
              </div>
              <div className="text-left">
                <div>Job Seeker</div>
                <div className="text-xs text-gray-500">Find jobs and practice interviews</div>
              </div>
            </Button>
            <Button
              onClick={() => onLogin("recruiter")}
              className="w-full justify-start gap-3 h-auto py-4"
              variant="outline"
            >
              <div className="h-10 w-10 rounded-lg bg-indigo-100 flex items-center justify-center">
                <Users className="h-5 w-5 text-indigo-600" />
              </div>
              <div className="text-left">
                <div>Recruiter</div>
                <div className="text-xs text-gray-500">Manage jobs and candidates</div>
              </div>
            </Button>
            <Button
              onClick={() => onLogin("hiring-manager")}
              className="w-full justify-start gap-3 h-auto py-4"
              variant="outline"
            >
              <div className="h-10 w-10 rounded-lg bg-blue-100 flex items-center justify-center">
                <Building2 className="h-5 w-5 text-blue-600" />
              </div>
              <div className="text-left">
                <div>Hiring Manager</div>
                <div className="text-xs text-gray-500">Review shortlists and make decisions</div>
              </div>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
