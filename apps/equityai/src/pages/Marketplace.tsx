import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { Property, SearchFilters } from '@/types/property';
import { mockProperties } from '@/data/mockData';
import { MapPin, Heart, BarChart3, Clock, Calculator } from 'lucide-react';

const Marketplace = () => {
  const { toast } = useToast();
  const [filters, setFilters] = useState<SearchFilters>({
    state: 'TX',
    priceMin: 0,
    priceMax: 1000000,
    marginMin: 10,
    daysOnMarketMax: 90
  });
  const [properties, setProperties] = useState<Property[]>(mockProperties);
  const [savedProperties, setSavedProperties] = useState<string[]>([]);
  const [sortBy, setSortBy] = useState('equity-score');

  useEffect(() => {
    // Load saved properties from localStorage
    const saved = localStorage.getItem('savedProperties');
    if (saved) {
      setSavedProperties(JSON.parse(saved));
    }
  }, []);

  const calculateMargin = (property: Property) => {
    const totalCost = property.price + property.rehabEstimate + (property.price * 0.08); // 8% closing costs
    return Math.round(((property.arv - totalCost) / totalCost) * 100);
  };

  const handleSaveProperty = (propertyId: string) => {
    const newSaved = savedProperties.includes(propertyId)
      ? savedProperties.filter(id => id !== propertyId)
      : [...savedProperties, propertyId];
    
    setSavedProperties(newSaved);
    localStorage.setItem('savedProperties', JSON.stringify(newSaved));
    
    toast({
      title: savedProperties.includes(propertyId) ? "Property removed" : "Property saved",
      description: savedProperties.includes(propertyId) ? 
        "Removed from your saved properties" : 
        "Added to your saved properties",
    });
  };

  const filteredProperties = properties.filter(property => {
    const margin = calculateMargin(property);
    return (
      property.state === filters.state &&
      property.price >= (filters.priceMin || 0) &&
      property.price <= (filters.priceMax || 1000000) &&
      (!filters.beds || property.beds >= filters.beds) &&
      (!filters.propertyType || property.propertyType === filters.propertyType) &&
      (filters.needsWork === undefined || property.needsWork === filters.needsWork) &&
      margin >= (filters.marginMin || 0) &&
      property.dom <= (filters.daysOnMarketMax || 90)
    );
  });

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Filter Sidebar */}
          <div className="w-full lg:w-80">
            <Card className="sticky top-24">
              <CardHeader>
                <CardTitle>Filters</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Location */}
                <div className="space-y-2">
                  <Label>Location</Label>
                  <Input
                    placeholder="City or ZIP code"
                    value={filters.city || filters.zip || ''}
                    onChange={(e) => setFilters({...filters, city: e.target.value})}
                  />
                  <Select value={filters.state} onValueChange={(value) => setFilters({...filters, state: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select state" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="TX">Texas</SelectItem>
                      <SelectItem value="FL">Florida</SelectItem>
                      <SelectItem value="GA">Georgia</SelectItem>
                      <SelectItem value="NC">North Carolina</SelectItem>
                      <SelectItem value="TN">Tennessee</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Price Range */}
                <div className="space-y-2">
                  <Label>Price Range</Label>
                  <div className="px-2">
                    <Slider
                      value={[filters.priceMin || 0, filters.priceMax || 1000000]}
                      onValueChange={([min, max]) => setFilters({...filters, priceMin: min, priceMax: max})}
                      max={1000000}
                      step={10000}
                      className="w-full"
                    />
                  </div>
                  <div className="flex justify-between text-sm text-muted-foreground">
                    <span>${(filters.priceMin || 0).toLocaleString()}</span>
                    <span>${(filters.priceMax || 1000000).toLocaleString()}</span>
                  </div>
                </div>

                {/* Bedrooms */}
                <div className="space-y-2">
                  <Label>Minimum Bedrooms</Label>
                  <Select value={filters.beds?.toString()} onValueChange={(value) => setFilters({...filters, beds: parseInt(value)})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Any" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1">1+</SelectItem>
                      <SelectItem value="2">2+</SelectItem>
                      <SelectItem value="3">3+</SelectItem>
                      <SelectItem value="4">4+</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Property Type */}
                <div className="space-y-2">
                  <Label>Property Type</Label>
                  <Select value={filters.propertyType} onValueChange={(value) => setFilters({...filters, propertyType: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="All types" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="single-family">Single Family</SelectItem>
                      <SelectItem value="condo">Condo</SelectItem>
                      <SelectItem value="townhouse">Townhouse</SelectItem>
                      <SelectItem value="multi-family">Multi-family</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Needs Work Toggle */}
                <div className="flex items-center justify-between">
                  <Label htmlFor="needs-work">Needs work only</Label>
                  <Switch
                    id="needs-work"
                    checked={filters.needsWork || false}
                    onCheckedChange={(checked) => setFilters({...filters, needsWork: checked})}
                  />
                </div>

                {/* Margin Slider */}
                <div className="space-y-2">
                  <Label>Minimum Margin (%)</Label>
                  <div className="px-2">
                    <Slider
                      value={[filters.marginMin || 0]}
                      onValueChange={([value]) => setFilters({...filters, marginMin: value})}
                      max={100}
                      step={5}
                      className="w-full"
                    />
                  </div>
                  <div className="text-sm text-muted-foreground">{filters.marginMin || 0}%+</div>
                </div>

                {/* Days on Market */}
                <div className="space-y-2">
                  <Label>Days on Market (max)</Label>
                  <div className="px-2">
                    <Slider
                      value={[filters.daysOnMarketMax || 90]}
                      onValueChange={([value]) => setFilters({...filters, daysOnMarketMax: value})}
                      max={365}
                      step={1}
                      className="w-full"
                    />
                  </div>
                  <div className="text-sm text-muted-foreground">{filters.daysOnMarketMax || 90} days</div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Content */}
          <div className="flex-1">
            {/* Header */}
            <div className="flex justify-between items-center mb-6">
              <div>
                <h1 className="text-3xl font-bold text-foreground">Property Marketplace</h1>
                <p className="text-muted-foreground">{filteredProperties.length} properties found</p>
              </div>
              <div className="flex gap-4">
                <Select value={sortBy} onValueChange={setSortBy}>
                  <SelectTrigger className="w-48">
                    <SelectValue placeholder="Sort by" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="equity-score">Highest Equity Score</SelectItem>
                    <SelectItem value="margin">Highest Margin</SelectItem>
                    <SelectItem value="price-low">Price: Low to High</SelectItem>
                    <SelectItem value="price-high">Price: High to Low</SelectItem>
                    <SelectItem value="days-market">Newest Listings</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Map Placeholder */}
            <Card className="mb-6">
              <CardContent className="p-6">
                <div className="bg-muted rounded-lg h-64 flex items-center justify-center">
                  <div className="text-center">
                    <MapPin className="h-12 w-12 text-primary mx-auto mb-2" />
                    <p className="text-muted-foreground">Interactive Property Map</p>
                    <p className="text-sm text-muted-foreground">Coming Soon</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Property Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
              {filteredProperties.map((property) => {
                const margin = calculateMargin(property);
                const isSaved = savedProperties.includes(property.id);
                
                return (
                  <Card key={property.id} className="hover:shadow-lg transition-shadow">
                    <CardContent className="p-6">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h3 className="font-semibold text-lg text-foreground">{property.address}</h3>
                          <p className="text-muted-foreground">{property.city}, {property.state} {property.zip}</p>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleSaveProperty(property.id)}
                          className={isSaved ? 'text-red-500' : 'text-muted-foreground'}
                        >
                          <Heart className={`h-4 w-4 ${isSaved ? 'fill-current' : ''}`} />
                        </Button>
                      </div>

                      <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                        <div>
                          <p className="text-muted-foreground">Price</p>
                          <p className="font-semibold">${property.price.toLocaleString()}</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">ARV</p>
                          <p className="font-semibold">${property.arv.toLocaleString()}</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Beds/Baths</p>
                          <p className="font-semibold">{property.beds}br / {property.baths}ba</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Sq Ft</p>
                          <p className="font-semibold">{property.sqft.toLocaleString()}</p>
                        </div>
                      </div>

                      <div className="space-y-3">
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-muted-foreground">Equity Score</span>
                          <Badge variant="secondary" className="bg-primary/10 text-primary">
                            {property.equityScore}/100
                          </Badge>
                        </div>
                        
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-muted-foreground">Rehab Est.</span>
                          <span className="text-sm font-medium">${property.rehabEstimate.toLocaleString()}</span>
                        </div>

                        <div className="flex justify-between items-center">
                          <span className="text-sm text-muted-foreground">Profit Margin</span>
                          <span className={`text-sm font-medium ${margin > 20 ? 'text-green-600' : margin > 10 ? 'text-yellow-600' : 'text-red-600'}`}>
                            {margin}%
                          </span>
                        </div>

                        <div className="flex justify-between items-center">
                          <span className="text-sm text-muted-foreground flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            Days on Market
                          </span>
                          <span className="text-sm font-medium">{property.dom}</span>
                        </div>
                      </div>

                      <div className="flex gap-2 mt-6">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleSaveProperty(property.id)}
                          className="flex-1"
                        >
                          {isSaved ? 'Saved' : 'Save'}
                        </Button>
                        <Button size="sm" className="flex-1">
                          <Calculator className="h-4 w-4 mr-1" />
                          Analyze
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            {filteredProperties.length === 0 && (
              <Card className="p-12 text-center">
                <CardContent>
                  <BarChart3 className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-foreground mb-2">No properties found</h3>
                  <p className="text-muted-foreground mb-4">Try adjusting your filters to see more results.</p>
                  <Button onClick={() => setFilters({ state: 'TX', priceMin: 0, priceMax: 1000000, marginMin: 10, daysOnMarketMax: 90 })}>
                    Reset filters
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Marketplace;