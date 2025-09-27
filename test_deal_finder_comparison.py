"""
Test showing the difference between old and new Deal Finder
Demonstrates the power of listing data integration
"""

import asyncio
import logging
from dotenv import load_dotenv
import os

from agents.deal_finder import DealFinder, SearchCriteria
from integrations.attom_api import ATTOMDataBridge

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def compare_deal_finders():
    """Compare old Deal Finder vs new Enhanced Deal Finder"""
    
    print("🏠 DEAL FINDER COMPARISON TEST")
    print("=" * 60)
    
    # Load API keys
    load_dotenv()
    attom_key = os.getenv('ATTOM_API_KEY')
    rapidapi_key = os.getenv('RAPIDAPI_KEY')
    
    if not attom_key:
        print("❌ No ATTOM_API_KEY found")
        return
    
    # Initialize ATTOM bridge
    attom_bridge = ATTOMDataBridge(api_key=attom_key)
    
    # Test criteria
    criteria = SearchCriteria(
        max_price=500000,
        target_locations=["24060"],  # Blacksburg
        property_types=["SFR"],
        min_deal_score=60.0
    )
    
    print("🔍 Testing both versions with same criteria...")
    print(f"   Location: {criteria.target_locations}")
    print(f"   Max Price: ${criteria.max_price:,.0f}")
    print(f"   Property Types: {criteria.property_types}")
    
    # Test 1: Old Deal Finder (without listing data)
    print("\n1️⃣ OLD DEAL FINDER (No Current Listing Prices):")
    print("-" * 50)
    
    old_deal_finder = DealFinder(attom_bridge=attom_bridge)  # No rapidapi_key
    old_deals = await old_deal_finder.find_deals_now(criteria, max_results=3)
    
    if old_deals:
        for i, deal in enumerate(old_deals, 1):
            print(f"\n   Deal {i}: {deal.property_address}")
            print(f"   Title: {deal.title}")
            print(f"   Estimated Value: ${deal.key_metrics.get('estimated_value', 0):,.0f}")
            print(f"   'Listing' Price: ${deal.key_metrics.get('listing_price', 0):,.0f}")
            print(f"   Profit %: {deal.key_metrics.get('profit_percentage', 0):.1f}%")
            print(f"   ⚠️  Note: {deal.key_metrics.get('note', 'Using historical/estimated prices')}")
    else:
        print("   ❌ No deals found with old method")
    
    # Test 2: New Enhanced Deal Finder (with listing data)
    if rapidapi_key:
        print("\n2️⃣ NEW ENHANCED DEAL FINDER (With Current Listing Prices):")
        print("-" * 50)
        
        new_deal_finder = DealFinder(
            attom_bridge=attom_bridge,
            rapidapi_key=rapidapi_key  # This enables listing integration
        )
        
        new_deals = await new_deal_finder.find_deals_now(criteria, max_results=3)
        
        if new_deals:
            for i, deal in enumerate(new_deals, 1):
                print(f"\n   Deal {i}: {deal.property_address}")
                print(f"   Title: {deal.title}")
                print(f"   ATTOM Value: ${deal.key_metrics.get('attom_estimated_value', 0):,.0f}")
                print(f"   Current Listing: ${deal.key_metrics.get('current_listing_price', 0):,.0f}")
                print(f"   Zestimate: ${deal.key_metrics.get('zestimate', 0):,.0f}")
                print(f"   Real Profit %: {deal.key_metrics.get('profit_percentage', 0):.1f}%")
                
                days_on_market = deal.key_metrics.get('days_on_market')
                if days_on_market:
                    print(f"   Days on Market: {days_on_market}")
                
                seller_motivation = deal.key_metrics.get('seller_motivation')
                if seller_motivation:
                    print(f"   Seller Motivation: {seller_motivation}")
                
                print(f"   Confidence: {deal.confidence_score:.0%}")
                print(f"   ✅ Note: Analysis based on current market data")
        else:
            print("   ⚠️  No deals found - properties may not be actively listed")
        
        # Show API usage
        status = new_deal_finder.get_monitoring_status()
        if 'listing_api_usage' in status:
            usage = status['listing_api_usage']
            print(f"\n   📊 API Usage: {usage['requests_made']} requests made")
            print(f"   📊 Remaining: {usage['requests_remaining']} requests")
    else:
        print("\n2️⃣ NEW ENHANCED DEAL FINDER:")
        print("-" * 50)
        print("   ⚠️  RAPIDAPI_KEY not found in .env file")
        print("   ⚠️  Cannot test enhanced features without API key")
        print("   ⚠️  Get free key at: https://rapidapi.com/apimaker/api/zillow-com1/")
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY:")
    print("   Old Method: Uses historical prices - often inaccurate")
    print("   New Method: Uses current listing prices - finds REAL deals!")
    print("   Enhanced Method includes:")
    print("   • Current market listing prices")
    print("   • Seller motivation analysis") 
    print("   • Days on market insights")
    print("   • Rental income estimates")
    print("   • More accurate profit calculations")


if __name__ == "__main__":
    asyncio.run(compare_deal_finders())