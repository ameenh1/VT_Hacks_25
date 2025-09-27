import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";
import Home from "./pages/Home";
import Marketplace from "./pages/Marketplace";
import DealAnalyzer from "./pages/DealAnalyzer";
import AgentConnect from "./pages/AgentConnect";
import Pricing from "./pages/Pricing";
import SignIn from "./pages/SignIn";
import CreateAccount from "./pages/CreateAccount";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <div className="min-h-screen bg-background text-foreground">
          <Navigation />
          <main>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/marketplace" element={<Marketplace />} />
              <Route path="/analyzer" element={<DealAnalyzer />} />
              <Route path="/agent-connect" element={<AgentConnect />} />
              <Route path="/pricing" element={<Pricing />} />
              <Route path="/signin" element={<SignIn />} />
              <Route path="/signup" element={<CreateAccount />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
