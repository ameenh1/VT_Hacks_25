"""
Simple ATTOM API Test - Test real data connection without complex filters
"""

import asyncio
import sys
import os
from datetime import datetime
import logging

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.deal_finder import DealFinder, SearchCriteria
from integrations.attom_api import ATTOMDataBridge
from models.data_models import ATTOMSearchCriteria
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_simple_attom_search():
    """Test ATTOM API with minimal parameters"""
    print("🏠 Testing ATTOM API with Simple Search Parameters")
    print("=" * 60)
    
    try:
        # Load environment variables
        load_dotenv()
        api_key = os.getenv('ATTOM_API_KEY')
        
        if not api_key or api_key == 'your_attom_api_key_here':
            print("❌ ATTOM API key not found")
            return False
        
        print(f"✅ ATTOM API key found: {api_key[:8]}...")
        
        # Initialize ATTOM bridge
        attom_bridge = ATTOMDataBridge(api_key=api_key)
        
        # Try a very simple search - just city and state, no price filters
        print("\n🔍 Testing simple search: Blacksburg, VA")
        
        simple_criteria = ATTOMSearchCriteria(
            city="Blacksburg",
            state="VA",
            max_results=5
        )
        
        properties = await attom_bridge.search_properties(simple_criteria)
        
        if properties:
            print(f"✅ Found {len(properties)} properties:")
            for i, prop in enumerate(properties, 1):
                print(f"\n  Property {i}:")
                print(f"    Address: {prop.address}")
                print(f"    Bedrooms: {prop.bedrooms}")
                print(f"    Bathrooms: {prop.bathrooms}")
                print(f"    Square Feet: {prop.square_feet}")
                print(f"    Last Sale Price: ${prop.last_sale_price:,.0f}" if prop.last_sale_price else "    Last Sale Price: N/A")
                print(f"    Estimated Value: ${prop.estimated_value:,.0f}" if prop.estimated_value else "    Estimated Value: N/A")
        else:
            print("⚠️  No properties found")
        
        return True
        
    except Exception as e:
        print(f"❌ ATTOM API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_deal_finder_with_location_only():
    """Test Deal Finder with location-only criteria"""
    print("\n" + "=" * 60)
    print("Testing Deal Finder with Location-Only Search")
    print("=" * 60)
    
    try:
        # Load environment variables
        load_dotenv()
        api_key = os.getenv('ATTOM_API_KEY')
        
        # Initialize ATTOM bridge and Deal Finder
        attom_bridge = ATTOMDataBridge(api_key=api_key)
        deal_finder = DealFinder(attom_bridge=attom_bridge)
        
        # Create simple search criteria - no price limit
        criteria = SearchCriteria(
            target_locations=["Blacksburg", "VA"],
            property_types=["SFR"]
            # Removed max_price to avoid API parameter issues
        )
        
        print("🔍 Searching for deals in Blacksburg, VA...")
        deals = await deal_finder.find_deals_now(criteria, max_results=5)
        
        if deals:
            print(f"✅ Found {len(deals)} potential deals:")
            for i, deal in enumerate(deals, 1):
                print(f"\n  Deal {i}:")
                print(f"    Address: {deal.property_address}")
                print(f"    Alert Type: {deal.alert_type.value}")
                print(f"    Priority: {deal.priority.name}")
                if deal.listing_price:
                    print(f"    Listing Price: ${deal.listing_price:,.0f}")
                if deal.estimated_value:
                    print(f"    Estimated Value: ${deal.estimated_value:,.0f}")
                if deal.potential_profit:
                    print(f"    Potential Profit: ${deal.potential_profit:,.0f}")
                print(f"    Confidence: {deal.confidence_score:.2f}")
        else:
            print("⚠️  No deals found")
            
        return len(deals) > 0
        
    except Exception as e:
        print(f"❌ Deal Finder test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run simplified ATTOM API tests"""
    
    # Test 1: Direct ATTOM API
    test1_result = await test_simple_attom_search()
    
    # Test 2: Deal Finder with ATTOM
    test2_result = await test_deal_finder_with_location_only()
    
    print("\n" + "=" * 60)
    print("SIMPLE TEST SUMMARY")
    print("=" * 60)
    print(f"Direct ATTOM API Test:     {'✅ PASSED' if test1_result else '❌ FAILED'}")
    print(f"Deal Finder ATTOM Test:    {'✅ PASSED' if test2_result else '❌ FAILED'}")
    
    if test1_result and test2_result:
        print("\n🎉 ATTOM API is working with real data!")
        print("Next step: Fine-tune search parameters for better deal finding")
    else:
        print("\n⚠️  Some tests failed - check ATTOM API parameters")

if __name__ == "__main__":
    asyncio.run(main())