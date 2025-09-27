"""
Listing Data Bridge - Integrates free listing APIs with Deal Finder
Combines ATTOM property data with current market listing prices
"""

import asyncio
import httpx
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
import os

logger = logging.getLogger(__name__)


@dataclass
class ListingData:
    """Current listing information for a property"""
    listing_price: Optional[float] = None
    zestimate: Optional[float] = None
    days_on_market: Optional[int] = None
    status: Optional[str] = None  # "FOR_SALE", "SOLD", "OFF_MARKET"
    price_history: list = None
    rental_estimate: Optional[float] = None
    last_updated: Optional[str] = None
    
    def __post_init__(self):
        if self.price_history is None:
            self.price_history = []


class ListingDataBridge:
    """
    Free listing data integration for Deal Finder
    Uses RapidAPI Zillow API (free tier: 100 requests/month)
    """
    
    def __init__(self, rapidapi_key: Optional[str] = None):
        """Initialize with RapidAPI key"""
        self.rapidapi_key = rapidapi_key or os.getenv('RAPIDAPI_KEY')
        
        if not self.rapidapi_key:
            logger.warning("No RapidAPI key provided - listing data will be limited")
        
        self.zillow_headers = {
            "X-RapidAPI-Key": self.rapidapi_key,
            "X-RapidAPI-Host": "zillow56.p.rapidapi.com"
        }
        
        # Rate limiting
        self.request_count = 0
        self.max_requests_per_hour = 50  # Conservative rate limiting
        
    async def get_listing_data(self, address: str) -> Optional[ListingData]:
        """Get current listing data for a property address"""
        
        if not self.rapidapi_key:
            logger.warning(f"No API key - cannot get listing data for {address}")
            return None
            
        if self.request_count >= self.max_requests_per_hour:
            logger.warning("Rate limit reached for listing API")
            return None
        
        try:
            # Step 1: Search for property by address
            zpid = await self._search_property(address)
            if not zpid:
                return None
            
            # Step 2: Get detailed property information
            listing_data = await self._get_property_details(zpid)
            return listing_data
            
        except Exception as e:
            logger.error(f"Error getting listing data for {address}: {e}")
            return None
    
    async def _search_property(self, address: str) -> Optional[str]:
        """Search for property and get Zillow property ID (ZPID)"""
        try:
            self.request_count += 1
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = "https://zillow56.p.rapidapi.com/search"
                params = {
                    "location": address,
                    "output": "json"
                }
                
                response = await client.get(url, headers=self.zillow_headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('results', [])
                    
                    if results:
                        # Get the first matching property
                        property_data = results[0]
                        zpid = property_data.get('zpid')
                        logger.info(f"Found ZPID {zpid} for address {address}")
                        return str(zpid) if zpid else None
                else:
                    logger.warning(f"Zillow search failed for {address}: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Property search error for {address}: {e}")
        
        return None
    
    async def _get_property_details(self, zpid: str) -> Optional[ListingData]:
        """Get detailed property information from ZPID"""
        try:
            self.request_count += 1
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = "https://zillow56.p.rapidapi.com/property"
                params = {
                    "zpid": zpid
                }
                
                response = await client.get(url, headers=self.zillow_headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract key listing information
                    listing_data = ListingData(
                        listing_price=self._safe_get_price(data.get('price')),
                        zestimate=self._safe_get_price(data.get('zestimate')),
                        days_on_market=data.get('daysOnZillow'),
                        status=data.get('homeStatus'),
                        price_history=data.get('priceHistory', []),
                        rental_estimate=self._safe_get_price(data.get('rentZestimate')),
                        last_updated=data.get('datePosted')
                    )
                    
                    logger.info(f"Retrieved listing data for ZPID {zpid}")
                    return listing_data
                else:
                    logger.warning(f"Property details failed for ZPID {zpid}: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Property details error for ZPID {zpid}: {e}")
        
        return None
    
    def _safe_get_price(self, price_data) -> Optional[float]:
        """Safely extract price from various formats"""
        if not price_data:
            return None
            
        # Handle different price formats
        if isinstance(price_data, (int, float)):
            return float(price_data)
        elif isinstance(price_data, str):
            # Remove $ and commas, convert to float
            clean_price = price_data.replace('$', '').replace(',', '')
            try:
                return float(clean_price)
            except ValueError:
                return None
        elif isinstance(price_data, dict):
            # Some APIs return price as object with value
            return self._safe_get_price(price_data.get('value'))
        
        return None
    
    def get_api_usage_stats(self) -> Dict[str, Any]:
        """Get current API usage statistics"""
        return {
            "requests_made": self.request_count,
            "requests_remaining": max(0, self.max_requests_per_hour - self.request_count),
            "api_configured": bool(self.rapidapi_key)
        }
    
    def reset_usage_counter(self):
        """Reset the usage counter (call this hourly)"""
        self.request_count = 0


# Enhanced Deal Finder Integration
class EnhancedDealAnalyzer:
    """Enhanced deal analysis combining ATTOM + listing data"""
    
    def __init__(self, listing_bridge: ListingDataBridge):
        self.listing_bridge = listing_bridge
    
    async def analyze_deal_with_listing(self, attom_property, criteria) -> Optional[Dict[str, Any]]:
        """Analyze deal using both ATTOM and current listing data"""
        
        # Get current listing information
        listing_data = await self.listing_bridge.get_listing_data(attom_property.address)
        
        if not listing_data:
            logger.info(f"No listing data found for {attom_property.address}")
            return None
        
        # Use ATTOM for estimated value, listing API for current price
        estimated_value = attom_property.avm_value or attom_property.assessed_value
        current_listing_price = listing_data.listing_price
        
        if not estimated_value or not current_listing_price:
            logger.info(f"Missing valuation data for {attom_property.address}")
            return None
        
        # Calculate deal metrics
        potential_profit = estimated_value - current_listing_price
        profit_percentage = (potential_profit / current_listing_price) * 100 if current_listing_price > 0 else 0
        
        # Enhanced deal analysis
        deal_analysis = {
            "address": attom_property.address,
            "attom_estimated_value": estimated_value,
            "current_listing_price": current_listing_price,
            "zestimate": listing_data.zestimate,
            "potential_profit": potential_profit,
            "profit_percentage": profit_percentage,
            "days_on_market": listing_data.days_on_market,
            "listing_status": listing_data.status,
            "rental_estimate": listing_data.rental_estimate,
            "price_history": listing_data.price_history,
            "is_good_deal": profit_percentage >= 10,  # 10% profit threshold
            "seller_motivation": self._assess_seller_motivation(listing_data),
            "deal_confidence": self._calculate_deal_confidence(attom_property, listing_data)
        }
        
        return deal_analysis
    
    def _assess_seller_motivation(self, listing_data: ListingData) -> str:
        """Assess seller motivation based on listing data"""
        if not listing_data.days_on_market:
            return "unknown"
        
        if listing_data.days_on_market > 90:
            return "highly_motivated"
        elif listing_data.days_on_market > 45:
            return "motivated" 
        elif listing_data.days_on_market > 14:
            return "somewhat_motivated"
        else:
            return "not_motivated"
    
    def _calculate_deal_confidence(self, attom_property, listing_data: ListingData) -> float:
        """Calculate confidence score for the deal"""
        confidence = 0.5  # Base confidence
        
        # Higher confidence if ATTOM and Zillow estimates align
        if attom_property.avm_value and listing_data.zestimate:
            value_difference = abs(attom_property.avm_value - listing_data.zestimate) / attom_property.avm_value
            if value_difference < 0.1:  # Less than 10% difference
                confidence += 0.2
        
        # Higher confidence for longer days on market (motivated seller)
        if listing_data.days_on_market:
            if listing_data.days_on_market > 60:
                confidence += 0.2
            elif listing_data.days_on_market > 30:
                confidence += 0.1
        
        # Cap confidence at 0.9
        return min(0.9, confidence)


# Example usage function
async def test_listing_integration():
    """Test the listing data integration"""
    
    # Initialize with your RapidAPI key
    listing_bridge = ListingDataBridge()
    
    # Test address from our ATTOM results
    test_address = "400 PLEASANT VIEW CIR, BLACKSBURG, VA 24060"
    
    print(f"Testing listing data for: {test_address}")
    listing_data = await listing_bridge.get_listing_data(test_address)
    
    if listing_data:
        print(f"✅ Found listing data:")
        print(f"  Listing Price: ${listing_data.listing_price:,.0f}" if listing_data.listing_price else "  Listing Price: N/A")
        print(f"  Zestimate: ${listing_data.zestimate:,.0f}" if listing_data.zestimate else "  Zestimate: N/A")
        print(f"  Days on Market: {listing_data.days_on_market}")
        print(f"  Status: {listing_data.status}")
        if listing_data.rental_estimate:
            print(f"  Rental Estimate: ${listing_data.rental_estimate:,.0f}/month")
    else:
        print("❌ No listing data found")
    
    # Show API usage
    stats = listing_bridge.get_api_usage_stats()
    print(f"\nAPI Usage: {stats}")


if __name__ == "__main__":
    asyncio.run(test_listing_integration())