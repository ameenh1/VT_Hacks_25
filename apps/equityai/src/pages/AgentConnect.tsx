import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { useToast } from '@/hooks/use-toast';
import { mockAgents } from '@/data/mockData';
import { Star, Award, Clock, Target, Users } from 'lucide-react';

const AgentConnect = () => {
  const { toast } = useToast();
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    phone: '',
    city: '',
    timeline: ''
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    toast({
      title: "Request submitted",
      description: "We'll connect you with a qualified agent within 24 hours.",
    });
  };

  const handleRequestIntro = (agentName: string) => {
    toast({
      title: "Introduction requested",
      description: `We'll connect you with ${agentName} within 24 hours.`,
    });
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-foreground mb-4">Work with a proven closer</h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Our network of investment-focused agents have track records of closing deals fast. 
            They understand the numbers and can help you move quickly on the best opportunities.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* Contact Form */}
          <div>
            <Card>
              <CardHeader>
                <CardTitle>Get Connected</CardTitle>
                <p className="text-muted-foreground">Tell us about your investment goals and we'll match you with the right agent.</p>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="fullName">Full Name</Label>
                      <Input
                        id="fullName"
                        value={formData.fullName}
                        onChange={(e) => setFormData(prev => ({ ...prev, fullName: e.target.value }))}
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="email">Email</Label>
                      <Input
                        id="email"
                        type="email"
                        value={formData.email}
                        onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                        required
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="phone">Phone</Label>
                      <Input
                        id="phone"
                        type="tel"
                        value={formData.phone}
                        onChange={(e) => setFormData(prev => ({ ...prev, phone: e.target.value }))}
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="city">City</Label>
                      <Input
                        id="city"
                        value={formData.city}
                        onChange={(e) => setFormData(prev => ({ ...prev, city: e.target.value }))}
                        placeholder="Where are you investing?"
                        required
                      />
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="timeline">Investment Timeline</Label>
                    <Select value={formData.timeline} onValueChange={(value) => setFormData(prev => ({ ...prev, timeline: value }))}>
                      <SelectTrigger>
                        <SelectValue placeholder="When are you looking to buy?" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="now">Ready to buy now</SelectItem>
                        <SelectItem value="3-months">Within 3 months</SelectItem>
                        <SelectItem value="6-months">Within 6 months</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Button type="submit" className="w-full" size="lg">
                    Find My Agent
                  </Button>
                </form>
              </CardContent>
            </Card>

            {/* Why Choose Our Agents */}
            <Card className="mt-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Award className="h-5 w-5 text-primary" />
                  Why Our Agents?
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-start gap-3">
                    <Target className="h-5 w-5 text-primary mt-1" />
                    <div>
                      <h4 className="font-semibold">Investment Specialists</h4>
                      <p className="text-sm text-muted-foreground">They understand ARV, rehab costs, and profit margins.</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Clock className="h-5 w-5 text-primary mt-1" />
                    <div>
                      <h4 className="font-semibold">Fast Closings</h4>
                      <p className="text-sm text-muted-foreground">Average 21 days to close vs 30+ day market average.</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Users className="h-5 w-5 text-primary mt-1" />
                    <div>
                      <h4 className="font-semibold">Proven Track Record</h4>
                      <p className="text-sm text-muted-foreground">All agents have completed 50+ investment transactions.</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Featured Agents */}
          <div>
            <h2 className="text-2xl font-bold text-foreground mb-6">Featured Agents</h2>
            <div className="space-y-6">
              {mockAgents.map((agent) => (
                <Card key={agent.id}>
                  <CardContent className="p-6">
                    <div className="flex items-start gap-4">
                      <Avatar className="h-16 w-16">
                        <AvatarImage src={agent.photo} alt={agent.name} />
                        <AvatarFallback>{agent.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                      </Avatar>
                      <div className="flex-1">
                        <div className="flex justify-between items-start mb-2">
                          <h3 className="text-xl font-semibold text-foreground">{agent.name}</h3>
                          <div className="flex items-center gap-1">
                            <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                            <span className="text-sm font-medium">{agent.rating}</span>
                            <span className="text-sm text-muted-foreground">({agent.reviewCount})</span>
                          </div>
                        </div>
                        
                        <p className="text-muted-foreground text-sm mb-4">{agent.bio}</p>
                        
                        <div className="grid grid-cols-3 gap-4 mb-4 text-sm">
                          <div className="text-center">
                            <p className="font-semibold text-foreground">{agent.dealsCompleted}</p>
                            <p className="text-muted-foreground">Deals Closed</p>
                          </div>
                          <div className="text-center">
                            <p className="font-semibold text-foreground">{agent.avgDaysToClose}</p>
                            <p className="text-muted-foreground">Avg Days</p>
                          </div>
                          <div className="text-center">
                            <p className="font-semibold text-foreground">{agent.rating}</p>
                            <p className="text-muted-foreground">Rating</p>
                          </div>
                        </div>
                        
                        <div className="flex flex-wrap gap-2 mb-4">
                          {agent.specialties.map((specialty, index) => (
                            <Badge key={index} variant="secondary" className="text-xs">
                              {specialty}
                            </Badge>
                          ))}
                        </div>
                        
                        <Button 
                          className="w-full" 
                          onClick={() => handleRequestIntro(agent.name)}
                        >
                          Request Introduction
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
            
            <Card className="mt-6 bg-primary/5 border-primary/20">
              <CardContent className="p-6 text-center">
                <h3 className="font-semibold text-foreground mb-2">Need an agent in another market?</h3>
                <p className="text-muted-foreground mb-4">We have qualified agents in all major US markets.</p>
                <Button variant="outline">
                  View All Markets
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentConnect;