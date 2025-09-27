import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Calculator, FileText, TrendingUp, Home, DollarSign } from 'lucide-react';

const DealAnalyzer = () => {
  const [analysis, setAnalysis] = useState({
    purchasePrice: 285000,
    closingCosts: 22800, // 8% of purchase
    rehabItems: [
      { item: 'Kitchen renovation', cost: 25000 },
      { item: 'Bathroom updates', cost: 12000 },
      { item: 'Flooring', cost: 8000 }
    ],
    totalRehab: 45000,
    arv: 365000,
    confidence: 85
  });

  const totalInvestment = analysis.purchasePrice + analysis.closingCosts + analysis.totalRehab;
  const grossProfit = analysis.arv - totalInvestment;
  const netProfit = grossProfit - (analysis.arv * 0.06); // 6% selling costs
  const marginPercent = Math.round((netProfit / totalInvestment) * 100);

  const addRehabItem = () => {
    setAnalysis(prev => ({
      ...prev,
      rehabItems: [...prev.rehabItems, { item: '', cost: 0 }]
    }));
  };

  const updateRehabItem = (index: number, field: 'item' | 'cost', value: string | number) => {
    setAnalysis(prev => ({
      ...prev,
      rehabItems: prev.rehabItems.map((item, i) => 
        i === index ? { ...item, [field]: value } : item
      ),
      totalRehab: prev.rehabItems.reduce((sum, item, i) => 
        i === index 
          ? sum + (field === 'cost' ? Number(value) : item.cost)
          : sum + item.cost, 0)
    }));
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2">Deal Analyzer</h1>
          <p className="text-muted-foreground">Analyze potential returns and rehab costs for any property</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Analysis Tabs */}
          <div className="lg:col-span-2">
            <Tabs defaultValue="valuation" className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="valuation">Valuation</TabsTrigger>
                <TabsTrigger value="rehab">Rehab</TabsTrigger>
                <TabsTrigger value="comps">Comps</TabsTrigger>
              </TabsList>

              <TabsContent value="valuation" className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Calculator className="h-5 w-5" />
                      Purchase Details
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="purchase-price">Purchase Price</Label>
                        <Input
                          id="purchase-price"
                          type="number"
                          value={analysis.purchasePrice}
                          onChange={(e) => setAnalysis(prev => ({ 
                            ...prev, 
                            purchasePrice: Number(e.target.value),
                            closingCosts: Number(e.target.value) * 0.08
                          }))}
                        />
                      </div>
                      <div>
                        <Label htmlFor="closing-costs">Closing Costs (8%)</Label>
                        <Input
                          id="closing-costs"
                          type="number"
                          value={analysis.closingCosts}
                          onChange={(e) => setAnalysis(prev => ({ ...prev, closingCosts: Number(e.target.value) }))}
                        />
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Home className="h-5 w-5" />
                      After Repair Value (ARV)
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label htmlFor="arv">Estimated ARV</Label>
                      <Input
                        id="arv"
                        type="number"
                        value={analysis.arv}
                        onChange={(e) => setAnalysis(prev => ({ ...prev, arv: Number(e.target.value) }))}
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Confidence Level</span>
                      <Badge variant={analysis.confidence >= 80 ? 'default' : 'secondary'} className="bg-primary/10 text-primary">
                        {analysis.confidence}%
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="rehab" className="space-y-6">
                <Card>
                  <CardHeader>
                    <div className="flex justify-between items-center">
                      <CardTitle className="flex items-center gap-2">
                        <TrendingUp className="h-5 w-5" />
                        Rehab Items
                      </CardTitle>
                      <Button onClick={addRehabItem} size="sm">Add Item</Button>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {analysis.rehabItems.map((item, index) => (
                      <div key={index} className="grid grid-cols-2 gap-4">
                        <Input
                          placeholder="Rehab item"
                          value={item.item}
                          onChange={(e) => updateRehabItem(index, 'item', e.target.value)}
                        />
                        <Input
                          type="number"
                          placeholder="Cost"
                          value={item.cost}
                          onChange={(e) => updateRehabItem(index, 'cost', e.target.value)}
                        />
                      </div>
                    ))}
                    <Separator />
                    <div className="flex justify-between items-center font-semibold">
                      <span>Total Rehab Cost:</span>
                      <span>${analysis.totalRehab.toLocaleString()}</span>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="comps" className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Comparable Sales</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="bg-muted rounded-lg p-6 text-center">
                        <Home className="h-12 w-12 text-primary mx-auto mb-2" />
                        <p className="text-muted-foreground">Comparable sales data</p>
                        <p className="text-sm text-muted-foreground">Coming soon</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>

          {/* Results Panel */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <DollarSign className="h-5 w-5" />
                  Deal Summary
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Purchase Price:</span>
                    <span className="font-medium">${analysis.purchasePrice.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Closing Costs:</span>
                    <span className="font-medium">${analysis.closingCosts.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Rehab Costs:</span>
                    <span className="font-medium">${analysis.totalRehab.toLocaleString()}</span>
                  </div>
                  <Separator />
                  <div className="flex justify-between font-semibold">
                    <span>Total Investment:</span>
                    <span>${totalInvestment.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between font-semibold">
                    <span>ARV:</span>
                    <span>${analysis.arv.toLocaleString()}</span>
                  </div>
                  <Separator />
                  <div className="flex justify-between text-lg font-bold">
                    <span>Net Profit:</span>
                    <span className={netProfit > 0 ? 'text-green-600' : 'text-red-600'}>
                      ${netProfit.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between text-lg font-bold">
                    <span>Margin:</span>
                    <span className={marginPercent > 15 ? 'text-green-600' : marginPercent > 5 ? 'text-yellow-600' : 'text-red-600'}>
                      {marginPercent}%
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Investment Strategy</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="p-4 bg-primary/10 rounded-lg">
                    <h4 className="font-semibold text-primary mb-2">
                      {marginPercent > 15 ? 'Strong Deal' : marginPercent > 5 ? 'Marginal Deal' : 'Weak Deal'}
                    </h4>
                    <p className="text-sm text-muted-foreground">
                      {marginPercent > 15 
                        ? 'This property shows excellent profit potential. Consider moving quickly.'
                        : marginPercent > 5
                        ? 'This deal could work but requires careful execution.'
                        : 'Consider negotiating a lower price or finding additional value.'}
                    </p>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <Badge variant="outline" className="justify-center">
                      {netProfit > totalInvestment * 0.2 ? 'Hold' : 'Flip'}
                    </Badge>
                    <Badge variant="outline" className="justify-center">
                      {analysis.confidence >= 80 ? 'High Confidence' : 'Medium Risk'}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Button className="w-full" size="lg">
              <FileText className="h-4 w-4 mr-2" />
              Export Deal as PDF
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DealAnalyzer;