
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import CoursePlanning from "./pages/CoursePlanning";
import InteractiveLearning from "./pages/InteractiveLearning";
import NotFound from "./pages/NotFound";
import { ChatProvider } from "./contexts/ChatContext";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <ChatProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/course-planning" element={<CoursePlanning />} />
            <Route path="/interactive-learning" element={<InteractiveLearning />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </ChatProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
