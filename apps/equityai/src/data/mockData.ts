import { Property, Agent } from '@/types/property';

export const mockProperties: Property[] = [
  {
    id: '1',
    address: '123 Main St',
    city: 'Austin',
    state: 'TX',
    zip: '73301',
    beds: 3,
    baths: 2,
    sqft: 1850,
    price: 285000,
    arv: 365000,
    rehabEstimate: 45000,
    dom: 14,
    equityScore: 87,
    lat: 30.2672,
    lng: -97.7431,
    needsWork: true,
    propertyType: 'single-family'
  },
  {
    id: '2',
    address: '456 Oak Ave',
    city: 'Dallas',
    state: 'TX',
    zip: '75201',
    beds: 4,
    baths: 3,
    sqft: 2340,
    price: 425000,
    arv: 520000,
    rehabEstimate: 28000,
    dom: 7,
    equityScore: 92,
    lat: 32.7767,
    lng: -96.7970,
    needsWork: false,
    propertyType: 'single-family'
  },
  {
    id: '3',
    address: '789 Pine Rd',
    city: 'Houston',
    state: 'TX',
    zip: '77001',
    beds: 2,
    baths: 1,
    sqft: 1200,
    price: 195000,
    arv: 285000,
    rehabEstimate: 52000,
    dom: 28,
    equityScore: 74,
    lat: 29.7604,
    lng: -95.3698,
    needsWork: true,
    propertyType: 'condo'
  },
  {
    id: '4',
    address: '321 Elm St',
    city: 'San Antonio',
    state: 'TX',
    zip: '78201',
    beds: 3,
    baths: 2,
    sqft: 1650,
    price: 235000,
    arv: 315000,
    rehabEstimate: 35000,
    dom: 21,
    equityScore: 81,
    lat: 29.4241,
    lng: -98.4936,
    needsWork: true,
    propertyType: 'townhouse'
  }
];

export const mockAgents: Agent[] = [
  {
    id: '1',
    name: 'Sarah Johnson',
    photo: 'https://images.unsplash.com/photo-1494790108755-2616b612b750?w=150',
    rating: 4.9,
    reviewCount: 127,
    dealsCompleted: 89,
    avgDaysToClose: 18,
    specialties: ['Investment Properties', 'Fix & Flip', 'Market Analysis'],
    bio: 'Specializing in investment properties with 8+ years of experience helping investors maximize returns in the Austin market.'
  },
  {
    id: '2',
    name: 'Michael Chen',
    photo: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150',
    rating: 4.8,
    reviewCount: 94,
    dealsCompleted: 156,
    avgDaysToClose: 22,
    specialties: ['Wholesale Deals', 'Distressed Properties', 'REO Sales'],
    bio: 'Expert in distressed properties and wholesale deals. Known for closing fast and identifying hidden gems in Dallas metro.'
  }
];