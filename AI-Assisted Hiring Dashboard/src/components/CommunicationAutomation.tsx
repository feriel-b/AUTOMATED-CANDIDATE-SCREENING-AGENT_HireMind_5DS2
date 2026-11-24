import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Badge } from "./ui/badge";
import { Avatar, AvatarFallback } from "./ui/avatar";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { ScrollArea } from "./ui/scroll-area";
import { Send, Bot, Mail, CheckCircle2, Clock, MessageSquare } from "lucide-react";

interface Message {
  id: string;
  candidate: string;
  subject: string;
  status: "sent" | "delivered" | "opened" | "replied";
  sentAt: string;
  type: "auto" | "manual";
}

interface ChatMessage {
  id: string;
  sender: "bot" | "candidate";
  text: string;
  timestamp: string;
}

export function CommunicationAutomation() {
  const [chatInput, setChatInput] = useState("");
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: "1",
      sender: "candidate",
      text: "Hi, I applied for the Senior Full Stack Engineer position. When can I expect to hear back?",
      timestamp: "10:30 AM",
    },
    {
      id: "2",
      sender: "bot",
      text: "Thank you for your interest! Our team is currently reviewing all applications. You should hear back within 5-7 business days. Is there anything specific you'd like to know about the role?",
      timestamp: "10:31 AM",
    },
    {
      id: "3",
      sender: "candidate",
      text: "Yes, is this position remote or hybrid?",
      timestamp: "10:32 AM",
    },
    {
      id: "4",
      sender: "bot",
      text: "This position offers flexible remote work with optional hybrid arrangements. The team meets in the San Francisco office 1-2 times per month.",
      timestamp: "10:32 AM",
    },
  ]);

  const messages: Message[] = [
    {
      id: "1",
      candidate: "Sarah Johnson",
      subject: "Application Received - Senior Full Stack Engineer",
      status: "opened",
      sentAt: "2 hours ago",
      type: "auto",
    },
    {
      id: "2",
      candidate: "Michael Chen",
      subject: "Application Received - Senior Full Stack Engineer",
      status: "delivered",
      sentAt: "3 hours ago",
      type: "auto",
    },
    {
      id: "3",
      candidate: "Emily Rodriguez",
      subject: "Next Steps - Interview Invitation",
      status: "replied",
      sentAt: "5 hours ago",
      type: "manual",
    },
    {
      id: "4",
      candidate: "David Kim",
      subject: "Application Received - Senior Full Stack Engineer",
      status: "sent",
      sentAt: "6 hours ago",
      type: "auto",
    },
    {
      id: "5",
      candidate: "Amanda Lee",
      subject: "Thank you for your interest",
      status: "opened",
      sentAt: "1 day ago",
      type: "auto",
    },
  ];

  const handleSendChat = () => {
    if (!chatInput.trim()) return;
    
    const newMessage: ChatMessage = {
      id: Date.now().toString(),
      sender: "candidate",
      text: chatInput,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
    
    setChatMessages([...chatMessages, newMessage]);
    setChatInput("");

    // Simulate bot response
    setTimeout(() => {
      const botResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: "bot",
        text: "Thank you for your message. Our AI assistant has noted your query and a recruiter will follow up with you shortly if needed.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setChatMessages(prev => [...prev, botResponse]);
    }, 1000);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "sent":
        return <Clock className="h-4 w-4 text-gray-400" />;
      case "delivered":
        return <CheckCircle2 className="h-4 w-4 text-blue-500" />;
      case "opened":
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case "replied":
        return <MessageSquare className="h-4 w-4 text-indigo-500" />;
      default:
        return null;
    }
  };

  const getStatusText = (status: string) => {
    return status.charAt(0).toUpperCase() + status.slice(1);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2>Communication Automation</h2>
        <p className="text-gray-600">Automated messaging and AI chatbot for candidate queries</p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm">Messages Sent</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl">247</div>
            <p className="text-xs text-gray-500 mt-1">Last 30 days</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm">Open Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl text-green-600">84%</div>
            <p className="text-xs text-gray-500 mt-1">Above industry avg</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm">Response Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl text-blue-600">67%</div>
            <p className="text-xs text-gray-500 mt-1">Candidate engagement</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="messages" className="w-full">
        <TabsList>
          <TabsTrigger value="messages" className="gap-2">
            <Mail className="h-4 w-4" />
            Message Dashboard
          </TabsTrigger>
          <TabsTrigger value="chatbot" className="gap-2">
            <Bot className="h-4 w-4" />
            AI Chatbot
          </TabsTrigger>
        </TabsList>

        <TabsContent value="messages" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Sent Messages</CardTitle>
                  <CardDescription>Track all automated and manual communications</CardDescription>
                </div>
                <Button className="gap-2">
                  <Mail className="h-4 w-4" />
                  Compose Message
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {messages.map((message) => (
                  <Card key={message.id}>
                    <CardContent className="pt-4">
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-3 flex-1">
                          <Avatar className="h-10 w-10">
                            <AvatarFallback className="bg-gray-100 text-gray-600">
                              {message.candidate.split(" ").map(n => n[0]).join("")}
                            </AvatarFallback>
                          </Avatar>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span>{message.candidate}</span>
                              {message.type === "auto" && (
                                <Badge variant="outline" className="gap-1">
                                  <Bot className="h-3 w-3" />
                                  Auto
                                </Badge>
                              )}
                            </div>
                            <p className="text-sm text-gray-600">{message.subject}</p>
                            <p className="text-xs text-gray-500 mt-1">{message.sentAt}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {getStatusIcon(message.status)}
                          <span className="text-sm text-gray-600">
                            {getStatusText(message.status)}
                          </span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="chatbot">
          <Card className="h-[600px] flex flex-col">
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center">
                  <Bot className="h-5 w-5 text-indigo-600" />
                </div>
                <div>
                  <CardTitle>AI Candidate Assistant</CardTitle>
                  <CardDescription>Automated responses to common candidate queries</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="flex-1 flex flex-col">
              <ScrollArea className="flex-1 pr-4">
                <div className="space-y-4">
                  {chatMessages.map((msg) => (
                    <div
                      key={msg.id}
                      className={`flex ${msg.sender === "bot" ? "justify-start" : "justify-end"}`}
                    >
                      <div
                        className={`max-w-[70%] rounded-lg p-3 ${
                          msg.sender === "bot"
                            ? "bg-gray-100 text-gray-900"
                            : "bg-indigo-600 text-white"
                        }`}
                      >
                        {msg.sender === "bot" && (
                          <div className="flex items-center gap-2 mb-1">
                            <Bot className="h-3 w-3" />
                            <span className="text-xs">AI Assistant</span>
                          </div>
                        )}
                        <p className="text-sm">{msg.text}</p>
                        <p className={`text-xs mt-1 ${
                          msg.sender === "bot" ? "text-gray-500" : "text-indigo-100"
                        }`}>
                          {msg.timestamp}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
              <div className="flex gap-2 pt-4 border-t mt-4">
                <Input
                  placeholder="Type a message as a candidate..."
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && handleSendChat()}
                />
                <Button onClick={handleSendChat} size="icon">
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
