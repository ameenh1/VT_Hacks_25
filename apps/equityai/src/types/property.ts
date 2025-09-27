export interface Property {
  id: string;
  address: string;
  city: string;
  state: string;
  zip: string;
  beds: number;
  baths: number;
  sqft: number;
  price: number;
  arv: number;
  rehabEstimate: number;
  dom: number; // Days on market
  equityScore: number; // 0-100 score
  lat: number;
  lng: number;
  needsWork: boolean;
  propertyType: 'single-family' | 'condo' | 'townhouse' | 'multi-family';
}

export interface Agent {
  id: string;
  name: string;
  photo: string;
  rating: number;
  reviewCount: number;
  dealsCompleted: number;
  avgDaysToClose: number;
  specialties: string[];
  bio: string;
}

export interface SearchFilters {
  city?: string;
  zip?: string;
  state: string;
  priceMin?: number;
  priceMax?: number;
  beds?: number;
  propertyType?: string;
  needsWork?: boolean;
  marginMin?: number;
  daysOnMarketMax?: number;
}