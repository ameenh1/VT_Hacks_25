import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { MapPin, TrendingUp, Calculator, Users, Star, ArrowRight, Play, Zap, Target, Shield } from 'lucide-react';
import heroHouse from '@/assets/hero-house.jpg';
import housesGrid from '@/assets/houses-grid.jpg';
import investmentHouse from '@/assets/investment-house.jpg';

const Home = () => {
  const features = [
    {
      icon: <TrendingUp className="h-12 w-12 text-primary animate-float" />,
      title: "Equity scoring in real-time",
      description: "AI-powered analysis of market data and comparable sales to identify properties with the highest profit potential.",
      gradient: "from-emerald-50 to-green-100"
    },
    {
      icon: <Calculator className="h-12 w-12 text-primary animate-float" />,
      title: "Rehab cost modeling in minutes", 
      description: "Instantly estimate renovation costs with our proprietary database of contractor bids and material prices.",
      gradient: "from-blue-50 to-emerald-100"
    },
    {
      icon: <Users className="h-12 w-12 text-primary animate-float" />,
      title: "Agent introductions when you're ready",
      description: "Connect with proven local agents who specialize in investment properties and close deals fast.",
      gradient: "from-green-50 to-teal-100"
    }
  ];

  const testimonials = [
    {
      quote: "EquityAI helped me identify 3 profitable deals in my first month. The equity scores are incredibly accurate.",
      author: "Jennifer Martinez",
      role: "Real Estate Investor",
      profit: "$127K",
      deals: "8 deals"
    },
    {
      quote: "The rehab cost estimates saved me hours of research. I closed on my best flip property using their agent network.",
      author: "David Thompson", 
      role: "Fix & Flip Investor",
      profit: "$89K",
      deals: "12 deals"
    }
  ];

  const stats = [
    { number: "10,000+", label: "Properties Analyzed" },
    { number: "$2.1M+", label: "Investor Profits" },
    { number: "95%", label: "Success Rate" },
    { number: "18 Days", label: "Avg. Time to Close" }
  ];

  return (
    <div className="min-h-screen overflow-hidden">
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center gradient-hero">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-5">
          <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg%20width=%2260%22%20height=%2260%22%20viewBox=%220%200%2060%2060%22%20xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cg%20fill=%22none%22%20fill-rule=%22evenodd%22%3E%3Cg%20fill=%22%23000%22%20fill-opacity=%220.1%22%3E%3Cpath%20d=%22M36%2034v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6%2034v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6%204V0H4v4H0v2h4v4h2V6h4V4H6z%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] bg-repeat"></div>
        </div>
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <div className="animate-fade-in-up">
              <Badge className="mb-6 bg-primary/10 text-primary border-primary/20 hover:bg-primary/20 transition-colors">
                <Zap className="h-4 w-4 mr-2" />
                AI-Powered Real Estate Intelligence
              </Badge>
              
              <h1 className="text-6xl lg:text-7xl font-black text-foreground mb-8 leading-tight">
                Find{' '}
                <span className="bg-gradient-to-r from-primary to-emerald-500 bg-clip-text text-transparent"> undervalued </span>
                homes faster than ever
              </h1>
              
              <p className="text-xl text-muted-foreground mb-10 leading-relaxed max-w-lg">
                EquityAI scans millions of records and market signals to surface properties with{' '}
                <span className="text-primary font-semibold">real profit potential</span>.{' '}
                Then we connect you with proven agents so you can move first.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-6 mb-12">
                <Link to="/signup">
                  <Button size="lg" className="group bg-primary text-primary-foreground hover:bg-primary/90 shadow-elegant hover:shadow-glow transition-all duration-300 text-lg px-8 py-4">
                    <Zap className="h-5 w-5 mr-2 group-hover:animate-pulse" />
                    Try EquityAI Free
                    <ArrowRight className="h-5 w-5 ml-2 group-hover:translate-x-1 transition-transform" />
                  </Button>
                </Link>
                
                <Button variant="outline" size="lg" className="group border-2 border-primary/20 hover:border-primary hover:bg-primary/5 text-lg px-8 py-4 transition-all duration-300">
                  <Play className="h-5 w-5 mr-2 group-hover:scale-110 transition-transform" />
                  Watch Demo
                </Button>
              </div>
              
              {/* Stats Row */}
              <div className="grid grid-cols-4 gap-6 animate-fade-in">
                {stats.map((stat, index) => (
                  <div key={index} className="text-center">
                    <div className="text-2xl font-bold text-primary">{stat.number}</div>
                    <div className="text-sm text-muted-foreground">{stat.label}</div>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="relative animate-scale-in">
              {/* Main Hero Image */}
              <div className="relative rounded-3xl overflow-hidden shadow-elegant group">
                <img 
                  src={heroHouse} 
                  alt="Luxury Investment Property" 
                  className="w-full h-[600px] object-cover group-hover:scale-105 transition-transform duration-700"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent"></div>
                
                {/* Floating Cards */}
                <div className="absolute top-6 right-6 glass-effect rounded-xl p-4 animate-float">
                  <div className="text-white">
                    <div className="text-2xl font-bold text-emerald-400">87</div>
                    <div className="text-sm opacity-90">Equity Score</div>
                  </div>
                </div>
                
                <div className="absolute bottom-6 left-6 glass-effect rounded-xl p-4 animate-float">
                  <div className="text-white">
                    <div className="text-xl font-bold text-green-400">$127K</div>
                    <div className="text-sm opacity-90">Est. Profit</div>
                  </div>
                </div>
              </div>
              
              {/* Secondary Images */}
              <div className="absolute -top-12 -left-12 w-32 h-32 rounded-2xl overflow-hidden shadow-card animate-float" style={{animationDelay: '1s'}}>
                <img src={housesGrid} alt="Property Grid" className="w-full h-full object-cover" />
              </div>
              
              <div className="absolute -bottom-8 -right-8 w-40 h-28 rounded-2xl overflow-hidden shadow-card animate-float" style={{animationDelay: '2s'}}>
                <img src={investmentHouse} alt="Investment House" className="w-full h-full object-cover" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Trust Logos */}
      <section className="py-16 bg-white/50 backdrop-blur-sm border-y border-border/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-muted-foreground mb-12 text-lg">Trusted by successful investors nationwide</p>
          <div className="flex justify-center items-center space-x-16 opacity-40">
            {[1,2,3,4,5].map(i => (
              <div key={i} className="bg-gradient-to-br from-muted to-muted/50 rounded-lg p-6 w-32 h-16 flex items-center justify-center animate-fade-in hover:opacity-80 transition-opacity" style={{animationDelay: `${i * 0.2}s`}}>
                <span className="text-sm font-semibold text-muted-foreground">Partner {i}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-32 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-emerald-50/30 via-white to-green-50/30"></div>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
          <div className="text-center mb-20 animate-fade-in-up">
            <Badge className="mb-6 bg-primary/10 text-primary border-primary/20">
              Powerful Features
            </Badge>
            <h2 className="text-5xl font-bold text-foreground mb-6">
              Everything you need to{' '}
              <span className="bg-gradient-to-r from-primary to-emerald-500 bg-clip-text text-transparent">invest smarter</span>
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Our AI analyzes over 200 data points to find the most profitable opportunities
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <Card key={index} className={`relative p-8 shadow-card hover:shadow-elegant transition-all duration-500 hover:-translate-y-2 border-0 bg-gradient-to-br ${feature.gradient} group animate-fade-in`} style={{animationDelay: `${index * 0.2}s`}}>
                <CardContent className="space-y-6 p-0">
                  <div className="flex justify-center group-hover:scale-110 transition-transform duration-300">
                    {feature.icon}
                  </div>
                  <h3 className="text-2xl font-bold text-foreground text-center group-hover:text-primary transition-colors">
                    {feature.title}
                  </h3>
                  <p className="text-muted-foreground text-center leading-relaxed">
                    {feature.description}
                  </p>
                </CardContent>
                
                {/* Hover Effect */}
                <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-primary/0 to-emerald-500/0 group-hover:from-primary/5 group-hover:to-emerald-500/5 transition-all duration-500"></div>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-32 bg-gradient-to-br from-primary/5 via-emerald-50/50 to-green-100/30 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-20 animate-fade-in-up">
            <Badge className="mb-6 bg-primary/10 text-primary border-primary/20">
              Success Stories
            </Badge>
            <h2 className="text-5xl font-bold text-foreground mb-6">
              What investors are saying
            </h2>
            <p className="text-xl text-muted-foreground">
              Real profits from real investors using EquityAI
            </p>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            {testimonials.map((testimonial, index) => (
              <Card key={index} className="p-10 shadow-elegant hover:shadow-glow transition-all duration-500 hover:-translate-y-1 border-0 gradient-card group animate-fade-in" style={{animationDelay: `${index * 0.3}s`}}>
                <CardContent className="space-y-8 p-0">
                  <div className="flex mb-6">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className="h-6 w-6 fill-yellow-400 text-yellow-400 group-hover:animate-pulse" style={{animationDelay: `${i * 0.1}s`}} />
                    ))}
                  </div>
                  
                  <blockquote className="text-xl text-foreground italic leading-relaxed">
                    "{testimonial.quote}"
                  </blockquote>
                  
                  <div className="flex justify-between items-end">
                    <div>
                      <p className="font-bold text-lg text-foreground">{testimonial.author}</p>
                      <p className="text-muted-foreground">{testimonial.role}</p>
                    </div>
                    
                    <div className="text-right">
                      <div className="text-2xl font-bold text-primary">{testimonial.profit}</div>
                      <div className="text-sm text-muted-foreground">{testimonial.deals}</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-32 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-primary via-emerald-600 to-green-700"></div>
        <div className="absolute inset-0 opacity-20">
          <img 
            src={investmentHouse} 
            alt="Investment Property" 
            className="w-full h-full object-cover"
          />
        </div>
        <div className="absolute inset-0 bg-gradient-to-r from-primary/90 via-emerald-600/90 to-green-700/90"></div>
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10 animate-fade-in-up">
          <Badge className="mb-8 bg-white/20 text-white border-white/30 hover:bg-white/30 transition-colors">
            <Target className="h-4 w-4 mr-2" />
            Start Your Journey Today
          </Badge>
          
          <h2 className="text-6xl font-bold mb-8 text-white leading-tight">
            Try EquityAI for{' '}
            <span className="text-yellow-300">14 days</span>
            <br />
            then $999/month
          </h2>
          
          <p className="text-2xl mb-12 text-white/90 max-w-2xl mx-auto leading-relaxed">
            Start finding profitable deals today.{' '}
            <span className="text-yellow-300 font-semibold">Cancel anytime.</span>
          </p>
          
          <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
            <Link to="/signup">
              <Button size="lg" className="group bg-white text-primary hover:bg-gray-100 shadow-2xl hover:shadow-glow transition-all duration-300 text-xl px-12 py-6">
                <Shield className="h-6 w-6 mr-3 group-hover:animate-pulse" />
                Start Free Trial
                <ArrowRight className="h-6 w-6 ml-3 group-hover:translate-x-1 transition-transform" />
              </Button>
            </Link>
            
            <div className="text-white/80 text-lg">
              No credit card required • 30-day guarantee
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;