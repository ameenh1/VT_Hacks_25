"""
Enhanced Deal Finder with Listing Data Integration
Combines ATTOM property data with current market listing prices
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta

# Import your existing components
from agents.deal_finder import DealFinder, SearchCriteria, PropertyAlert, AlertType, AlertPriority
from integrations.attom_api import ATTOMDataBridge
from integrations.listing_bridge import ListingDataBridge, EnhancedDealAnalyzer

logger = logging.getLogger(__name__)


class EnhancedDealFinder(DealFinder):
    """
    Enhanced Deal Finder with listing data integration
    Combines ATTOM property data with current market listing prices for accurate deal analysis
    """
    
    def __init__(self, attom_bridge: Optional[ATTOMDataBridge] = None, 
                 analysis_engine=None, rapidapi_key: Optional[str] = None):
        """Initialize Enhanced Deal Finder with listing data support"""
        super().__init__(attom_bridge, analysis_engine)
        
        # Add listing data integration
        self.listing_bridge = ListingDataBridge(rapidapi_key)
        self.deal_analyzer = EnhancedDealAnalyzer(self.listing_bridge)
        
        logger.info("Enhanced Deal Finder initialized with listing data support")
    
    async def _analyze_property_for_deal(self, property_data, criteria: SearchCriteria) -> Optional[PropertyAlert]:
        """Enhanced property analysis using both ATTOM and listing data"""
        
        # Skip if already processed recently
        property_key = f"{property_data.address}_{datetime.now().date()}"
        if property_key in self.processed_properties:
            return None
        
        self.processed_properties.add(property_key)
        
        try:
            # Enhanced analysis with listing data
            deal_analysis = await self.deal_analyzer.analyze_deal_with_listing(property_data, criteria)
            
            if not deal_analysis:
                logger.debug(f"No deal analysis possible for {property_data.address}")
                return None
            
            # Check if it meets deal criteria
            if not deal_analysis["is_good_deal"]:
                logger.debug(f"Property {property_data.address} doesn't meet deal criteria")
                return None
            
            # Check user price limits
            listing_price = deal_analysis["current_listing_price"]
            if criteria.max_price and listing_price > criteria.max_price:
                return None
            
            # Create enhanced property alert
            alert = self._create_enhanced_alert(deal_analysis, property_data)
            
            logger.info(f"Found potential deal: {property_data.address} - {deal_analysis['profit_percentage']:.1f}% profit")
            return alert
            
        except Exception as e:
            logger.error(f"Error analyzing property {property_data.address}: {e}")
            return None
    
    def _create_enhanced_alert(self, deal_analysis: Dict, property_data) -> PropertyAlert:
        """Create a PropertyAlert with enhanced listing data"""
        
        profit_percentage = deal_analysis["profit_percentage"]
        
        # Determine alert type based on enhanced data
        alert_type = self._determine_enhanced_alert_type(deal_analysis)
        priority = self._determine_enhanced_priority(deal_analysis)
        
        # Enhanced description with listing insights
        description = self._generate_enhanced_description(deal_analysis, property_data)
        
        alert = PropertyAlert(
            alert_id=f"enhanced_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            property_address=property_data.address,
            alert_type=alert_type,
            priority=priority,
            title=f"Great Deal: {profit_percentage:.1f}% Profit Potential",
            description=description,
            key_metrics={
                # Enhanced metrics with listing data
                "attom_estimated_value": deal_analysis["attom_estimated_value"],
                "current_listing_price": deal_analysis["current_listing_price"],
                "zestimate": deal_analysis.get("zestimate"),
                "profit_percentage": profit_percentage,
                "potential_profit": deal_analysis["potential_profit"],
                "days_on_market": deal_analysis.get("days_on_market"),
                "listing_status": deal_analysis.get("listing_status"),
                "seller_motivation": deal_analysis.get("seller_motivation"),
                "rental_estimate": deal_analysis.get("rental_estimate"),
                "bedrooms": property_data.bedrooms,
                "bathrooms": property_data.bathrooms,
                "square_footage": property_data.square_footage
            },
            estimated_value=deal_analysis["attom_estimated_value"],
            listing_price=deal_analysis["current_listing_price"],
            potential_profit=deal_analysis["potential_profit"],
            confidence_score=deal_analysis["deal_confidence"],
            expires_at=datetime.now() + timedelta(days=self.alert_retention_days)
        )
        
        return alert
    
    def _determine_enhanced_alert_type(self, deal_analysis: Dict) -> AlertType:
        """Determine alert type using enhanced listing data"""
        profit_percentage = deal_analysis["profit_percentage"]
        days_on_market = deal_analysis.get("days_on_market", 0)
        
        # High profit potential
        if profit_percentage > 25:
            return AlertType.UNDERVALUED_PROPERTY
        
        # Good profit with motivated seller
        elif profit_percentage > 15 and days_on_market > 45:
            return AlertType.HIGH_CASH_FLOW
        
        # Price drop opportunity
        elif len(deal_analysis.get("price_history", [])) > 1:
            return AlertType.PRICE_DROP
        
        # General opportunity
        else:
            return AlertType.NEW_LISTING
    
    def _determine_enhanced_priority(self, deal_analysis: Dict) -> AlertPriority:
        """Determine alert priority using enhanced data"""
        profit_percentage = deal_analysis["profit_percentage"]
        seller_motivation = deal_analysis.get("seller_motivation", "unknown")
        
        # Urgent: High profit + motivated seller
        if profit_percentage > 20 and seller_motivation in ["highly_motivated", "motivated"]:
            return AlertPriority.URGENT
        
        # High: Good profit or very motivated seller
        elif profit_percentage > 15 or seller_motivation == "highly_motivated":
            return AlertPriority.HIGH
        
        # Medium: Decent profit
        elif profit_percentage > 10:
            return AlertPriority.MEDIUM
        
        else:
            return AlertPriority.LOW
    
    def _generate_enhanced_description(self, deal_analysis: Dict, property_data) -> str:
        """Generate enhanced alert description with listing insights"""
        profit_percentage = deal_analysis["profit_percentage"]
        days_on_market = deal_analysis.get("days_on_market")
        seller_motivation = deal_analysis.get("seller_motivation", "unknown")
        
        bedrooms = property_data.bedrooms or "?"
        bathrooms = property_data.bathrooms or "?"
        square_footage = property_data.square_footage or 0
        
        size_info = f"{square_footage:,.0f} sqft" if square_footage else "size unknown"
        
        description = f"Property shows {profit_percentage:.1f}% profit potential! "
        description += f"{bedrooms}BR/{bathrooms}BA, {size_info}. "
        
        # Add listing insights
        if days_on_market:
            description += f"Listed {days_on_market} days ago"
            if seller_motivation in ["highly_motivated", "motivated"]:
                description += " - seller may be motivated to negotiate. "
            else:
                description += ". "
        
        # Add rental info if available
        rental_estimate = deal_analysis.get("rental_estimate")
        if rental_estimate:
            description += f"Estimated rent: ${rental_estimate:,.0f}/month. "
        
        description += "Recommend immediate analysis!"
        
        return description
    
    async def get_api_usage_stats(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        listing_stats = self.listing_bridge.get_api_usage_stats()
        
        return {
            "listing_api": listing_stats,
            "deal_finder_status": self.get_monitoring_status()
        }


# Test function
async def test_enhanced_deal_finder():
    """Test the enhanced deal finder with real data"""
    
    print("🏠 Testing Enhanced Deal Finder with Listing Data")
    print("=" * 60)
    
    # Initialize components (you'll need to add your API keys to .env)
    from dotenv import load_dotenv
    import os
    load_dotenv()
    
    attom_key = os.getenv('ATTOM_API_KEY')
    rapidapi_key = os.getenv('RAPIDAPI_KEY')  # Add this to your .env file
    
    if not rapidapi_key:
        print("⚠️  Warning: No RAPIDAPI_KEY found in .env file")
        print("   Sign up at https://rapidapi.com and get a free API key")
        print("   Then add RAPIDAPI_KEY=your_key_here to your .env file")
        return
    
    # Initialize enhanced deal finder
    attom_bridge = ATTOMDataBridge(api_key=attom_key)
    enhanced_deal_finder = EnhancedDealFinder(
        attom_bridge=attom_bridge,
        rapidapi_key=rapidapi_key
    )
    
    # Test with Blacksburg area
    criteria = SearchCriteria(
        max_price=800000,  # Higher limit to catch deals
        target_locations=["24060"],
        property_types=["SFR"],
        min_deal_score=60.0  # Lower threshold for testing
    )
    
    print("🔍 Searching for enhanced deals...")
    deals = await enhanced_deal_finder.find_deals_now(criteria, max_results=5)
    
    if deals:
        print(f"✅ Found {len(deals)} enhanced deals:")
        for i, deal in enumerate(deals, 1):
            print(f"\n📊 Deal {i}:")
            print(f"   Address: {deal.property_address}")
            print(f"   Alert Type: {deal.alert_type.value}")
            print(f"   Priority: {deal.priority.name}")
            print(f"   Profit Potential: {deal.key_metrics.get('profit_percentage', 0):.1f}%")
            print(f"   ATTOM Value: ${deal.key_metrics.get('attom_estimated_value', 0):,.0f}")
            print(f"   Listing Price: ${deal.key_metrics.get('current_listing_price', 0):,.0f}")
            
            days_on_market = deal.key_metrics.get('days_on_market')
            if days_on_market:
                print(f"   Days on Market: {days_on_market}")
            
            seller_motivation = deal.key_metrics.get('seller_motivation')
            if seller_motivation:
                print(f"   Seller Motivation: {seller_motivation}")
            
            print(f"   Confidence: {deal.confidence_score:.0%}")
            print(f"   Description: {deal.description}")
    else:
        print("⚠️  No enhanced deals found with current criteria")
        print("   This could mean:")
        print("   1. No properties meet the profit threshold")
        print("   2. Properties aren't currently listed for sale")
        print("   3. API rate limits reached")
    
    # Show API usage
    stats = await enhanced_deal_finder.get_api_usage_stats()
    print(f"\n📊 API Usage Statistics:")
    print(f"   Listing API requests: {stats['listing_api']['requests_made']}")
    print(f"   Requests remaining: {stats['listing_api']['requests_remaining']}")


if __name__ == "__main__":
    asyncio.run(test_enhanced_deal_finder())