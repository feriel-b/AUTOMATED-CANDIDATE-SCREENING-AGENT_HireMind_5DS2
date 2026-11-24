import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Alert, AlertDescription } from "./ui/alert";
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { TrendingUp, AlertTriangle, Users, Target, Sparkles, Shield } from "lucide-react";

export function AIInsightsDashboard() {
  const diversityData = [
    { name: "Male", value: 58, color: "#6366f1" },
    { name: "Female", value: 35, color: "#ec4899" },
    { name: "Non-binary", value: 5, color: "#8b5cf6" },
    { name: "Prefer not to say", value: 2, color: "#d1d5db" },
  ];

  const ethnicityData = [
    { name: "Asian", count: 45 },
    { name: "White", count: 38 },
    { name: "Hispanic", count: 22 },
    { name: "Black", count: 18 },
    { name: "Other", count: 12 },
  ];

  const skillGapData = [
    { skill: "React", required: 100, available: 85 },
    { skill: "TypeScript", required: 100, available: 72 },
    { skill: "AWS", required: 80, available: 45 },
    { skill: "Node.js", required: 90, available: 68 },
    { skill: "PostgreSQL", required: 70, available: 52 },
  ];

  const aiInsights = [
    {
      type: "warning",
      icon: AlertTriangle,
      title: "Possible Duplicates Detected",
      description: "3 candidates appear to have submitted multiple applications",
      candidates: ["John Smith (2x)", "Maria Garcia (2x)", "Alex Wong (2x)"],
    },
    {
      type: "info",
      icon: Shield,
      title: "Spam Detection",
      description: "2 applications flagged as potential spam",
      candidates: ["resume_template_001.pdf", "test_application.pdf"],
    },
    {
      type: "success",
      icon: Target,
      title: "High Quality Pool",
      description: "87% of candidates meet minimum requirements",
      candidates: [],
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2>AI Insights & Analytics</h2>
        <p className="text-gray-600">Comprehensive analysis of your candidate pool</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm">Total Candidates</CardTitle>
            <Users className="h-4 w-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl">135</div>
            <p className="text-xs text-gray-500 mt-1">
              <span className="text-green-600">+12%</span> from last week
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm">Avg Fit Score</CardTitle>
            <TrendingUp className="h-4 w-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl">78.5%</div>
            <p className="text-xs text-gray-500 mt-1">
              <span className="text-green-600">+5.2%</span> improvement
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm">Shortlisted</CardTitle>
            <Target className="h-4 w-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl">24</div>
            <p className="text-xs text-gray-500 mt-1">Top 18% of applicants</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm">AI Processed</CardTitle>
            <Sparkles className="h-4 w-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl">135</div>
            <p className="text-xs text-gray-500 mt-1">100% automated screening</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Gender Diversity</CardTitle>
            <CardDescription>Distribution across candidate pool</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={diversityData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {diversityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Ethnicity Distribution</CardTitle>
            <CardDescription>Candidate demographics</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={ethnicityData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#6366f1" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Skill Gap Analysis</CardTitle>
          <CardDescription>Required skills vs. available talent pool</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={skillGapData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="skill" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="required" fill="#6366f1" name="Required %" />
              <Bar dataKey="available" fill="#10b981" name="Available %" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-indigo-600" />
            AI-Powered Alerts
          </CardTitle>
          <CardDescription>Automated quality checks and insights</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {aiInsights.map((insight, index) => (
            <Alert key={index} className={
              insight.type === "warning" ? "border-yellow-200 bg-yellow-50" :
              insight.type === "info" ? "border-blue-200 bg-blue-50" :
              "border-green-200 bg-green-50"
            }>
              <insight.icon className="h-4 w-4" />
              <AlertDescription>
                <div className="space-y-2">
                  <div>
                    <div className="flex items-center gap-2">
                      <span>{insight.title}</span>
                      {insight.type === "warning" && <Badge variant="outline">Action Required</Badge>}
                    </div>
                    <p className="text-sm text-gray-600 mt-1">{insight.description}</p>
                  </div>
                  {insight.candidates.length > 0 && (
                    <div className="flex gap-2 flex-wrap">
                      {insight.candidates.map((candidate) => (
                        <Badge key={candidate} variant="secondary" className="text-xs">
                          {candidate}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>
              </AlertDescription>
            </Alert>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
