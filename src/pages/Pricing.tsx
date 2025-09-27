import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Check, Star, Zap, Shield } from 'lucide-react';

const Pricing = () => {
  const features = [
    'Daily property alerts',
    'Nationwide property search',
    'AI-powered equity scoring',
    'Deal analyzer with ARV estimates',
    'Unlimited property saves',
    'Agent network access',
    'Market trend analysis',
    'Rehab cost calculator'
  ];

  const faqs = [
    {
      question: "What's included in the 14-day free trial?",
      answer: "Full access to all EquityAI features including property search, equity scoring, deal analysis, and agent connections. No credit card required to start."
    },
    {
      question: "Can I cancel anytime?",
      answer: "Yes, you can cancel your subscription at any time. There are no long-term contracts or cancellation fees."
    },
    {
      question: "How accurate are the equity scores?",
      answer: "Our AI analyzes over 200 data points including recent sales, market trends, and property conditions. Scores have shown 87% accuracy in predicting profitable deals."
    },
    {
      question: "Do you offer refunds?",
      answer: "We offer a 30-day money-back guarantee if you're not satisfied with EquityAI within your first month of paid subscription."
    },
    {
      question: "How do agent introductions work?",
      answer: "We connect you with pre-vetted agents in your target markets who specialize in investment properties. Introductions are included at no extra cost."
    },
    {
      question: "Is there a setup fee?",
      answer: "No setup fees, no hidden costs. Just $999/month after your free trial ends."
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {/* Header */}
        <div className="text-center mb-16">
          <Badge className="mb-4 bg-primary/10 text-primary border-primary/20">
            Simple Pricing
          </Badge>
          <h1 className="text-5xl font-bold text-foreground mb-6">
            One plan, everything included
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Get access to our complete platform for finding and analyzing profitable real estate investments.
          </p>
        </div>

        {/* Pricing Card */}
        <div className="max-w-lg mx-auto mb-16">
          <Card className="border-2 border-primary relative">
            <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
              <Badge className="bg-primary text-primary-foreground px-6 py-1">
                Most Popular
              </Badge>
            </div>
            <CardHeader className="text-center pb-2">
              <CardTitle className="text-2xl font-bold">EquityAI Pro</CardTitle>
              <div className="mt-4">
                <span className="text-5xl font-bold text-primary">$999</span>
                <span className="text-xl text-muted-foreground">/month</span>
              </div>
              <p className="text-muted-foreground mt-2">Everything you need to invest smarter</p>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="space-y-4">
                {features.map((feature, index) => (
                  <div key={index} className="flex items-center gap-3">
                    <Check className="h-5 w-5 text-primary" />
                    <span>{feature}</span>
                  </div>
                ))}
              </div>
              
              <div className="mt-8 space-y-4">
                <Link to="/signup" className="w-full">
                  <Button size="lg" className="w-full bg-primary text-primary-foreground hover:bg-primary/90">
                    <Zap className="mr-2 h-5 w-5" />
                    Start 14-day free trial
                  </Button>
                </Link>
                <p className="text-center text-sm text-muted-foreground">
                  No credit card required • Cancel anytime
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          <div className="text-center">
            <div className="bg-primary/10 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <Star className="h-8 w-8 text-primary" />
            </div>
            <h3 className="text-xl font-semibold mb-2">14-Day Free Trial</h3>
            <p className="text-muted-foreground">Test all features risk-free before you commit.</p>
          </div>
          <div className="text-center">
            <div className="bg-primary/10 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <Shield className="h-8 w-8 text-primary" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Cancel Anytime</h3>
            <p className="text-muted-foreground">No long-term contracts or hidden fees.</p>
          </div>
          <div className="text-center">
            <div className="bg-primary/10 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <Check className="h-8 w-8 text-primary" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Money-Back Guarantee</h3>
            <p className="text-muted-foreground">30-day refund if you're not satisfied.</p>
          </div>
        </div>

        {/* FAQ Section */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-center text-foreground mb-8">
            Frequently Asked Questions
          </h2>
          <Accordion type="single" collapsible className="w-full">
            {faqs.map((faq, index) => (
              <AccordionItem key={index} value={`item-${index}`}>
                <AccordionTrigger className="text-left">
                  {faq.question}
                </AccordionTrigger>
                <AccordionContent>
                  {faq.answer}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>

        {/* Legal Disclaimer */}
        <div className="bg-muted/30 rounded-lg p-6 text-center">
          <h3 className="font-semibold text-foreground mb-2">Important Disclaimer</h3>
          <p className="text-sm text-muted-foreground">
            Valuations are estimates only and provided for informational purposes. 
            EquityAI does not provide financial advice. All investment decisions should be made 
            after consulting with qualified professionals. Past performance does not guarantee future results.
          </p>
        </div>

        {/* Final CTA */}
        <div className="text-center mt-12">
          <h3 className="text-2xl font-bold text-foreground mb-4">
            Ready to find your next profitable deal?
          </h3>
          <Link to="/signup">
            <Button size="lg" className="bg-primary text-primary-foreground hover:bg-primary/90">
              Start your free trial today
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Pricing;