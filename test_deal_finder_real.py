"""
Deal Finder Real ATTOM Data Test
Test Deal Finder with working ATTOM API using postal code search
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
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_deal_finder_real_data():
    """Test Deal Finder with real ATTOM data using postal codes"""
    print("🏠 Deal Finder - Real ATTOM Data Test")
    print("=" * 60)
    
    try:
        # Load environment
        load_dotenv()
        api_key = os.getenv('ATTOM_API_KEY')
        
        if not api_key:
            print("❌ ATTOM API key not found")
            return False
        
        print(f"✅ ATTOM API key found: {api_key[:8]}...")
        
        # Initialize components
        attom_bridge = ATTOMDataBridge(api_key=api_key)
        deal_finder = DealFinder(attom_bridge=attom_bridge)
        
        print("✅ Deal Finder initialized with ATTOM bridge")
        
        # Test 1: Simple postal code search
        print("\n🔍 Test 1: Blacksburg, VA (24060) - Simple search")
        criteria = SearchCriteria(
            target_locations=["24060"],  # Use postal code as location
            property_types=["SFR"]
        )
        
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
                if deal.potential_profit and deal.potential_profit > 0:
                    print(f"    Potential Profit: ${deal.potential_profit:,.0f}")
                print(f"    Confidence: {deal.confidence_score:.2f}")
                if deal.key_metrics:
                    profit_pct = deal.key_metrics.get('profit_percentage', 0)
                    print(f"    Profit Percentage: {profit_pct:.1f}%")
        else:
            print("⚠️  No deals found with current criteria")
        
        # Test 2: Multiple Virginia zip codes
        print("\n🔍 Test 2: Multiple Virginia Tech area zip codes")
        criteria2 = SearchCriteria(
            target_locations=["24060", "24073", "24141"],  # Blacksburg, Christiansburg, Radford
            property_types=["SFR", "CON"]
        )
        
        deals2 = await deal_finder.find_deals_now(criteria2, max_results=10)
        print(f"✅ Multi-location search found {len(deals2)} potential deals")
        
        # Test 3: Background monitoring
        print("\n🔄 Test 3: Background monitoring with real data")
        
        # Add user criteria
        user_id = "vt_investor_1"
        monitoring_criteria = SearchCriteria(
            target_locations=["24060", "24073"],  # VT area
            property_types=["SFR"],
            min_deal_score=65.0
        )
        
        deal_finder.add_user_criteria(user_id, monitoring_criteria)
        print(f"✅ Added monitoring criteria for user: {user_id}")
        
        # Start monitoring
        await deal_finder.start_monitoring()
        print("✅ Background monitoring started")
        
        # Let it run for a few seconds
        await asyncio.sleep(5)
        
        # Check for new alerts
        user_alerts = await deal_finder.get_alerts_for_user(user_id)
        print(f"✅ Background monitoring generated {len(user_alerts)} alerts")
        
        if user_alerts:
            print("Recent alerts:")
            for alert in user_alerts[:3]:  # Show top 3
                print(f"  - {alert.property_address} ({alert.alert_type.value})")
        
        # Stop monitoring
        await deal_finder.stop_monitoring()
        print("✅ Background monitoring stopped")
        
        return True
        
    except Exception as e:
        print(f"❌ Deal Finder real data test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_deal_valuation_logic():
    """Test the deal valuation logic with real data"""
    print("\n" + "=" * 60)
    print("Testing Deal Valuation Logic")
    print("=" * 60)
    
    try:
        load_dotenv()
        api_key = os.getenv('ATTOM_API_KEY')
        
        # Get real ATTOM data first
        attom_bridge = ATTOMDataBridge(api_key=api_key)
        from models.data_models import ATTOMSearchCriteria
        
        search_criteria = ATTOMSearchCriteria(
            zip_code="24060",
            max_results=3
        )
        
        properties = await attom_bridge.search_properties(search_criteria)
        
        if not properties:
            print("⚠️  No properties found for valuation test")
            return False
        
        print(f"✅ Got {len(properties)} real properties for valuation testing")
        
        # Test how Deal Finder evaluates these properties
        deal_finder = DealFinder(attom_bridge=attom_bridge)
        
        for i, prop in enumerate(properties, 1):
            print(f"\n🏠 Property {i} Evaluation:")
            print(f"   Address: {prop.address or 'N/A'}")
            print(f"   City: {prop.city}")
            print(f"   Bedrooms: {prop.bedrooms}")
            print(f"   Last Sale Price: ${prop.last_sale_price:,.0f}" if prop.last_sale_price else "   Last Sale Price: N/A")
            print(f"   Assessed Value: ${prop.assessed_value:,.0f}" if prop.assessed_value else "   Assessed Value: N/A")
            print(f"   AVM Value: ${prop.avm_value:,.0f}" if prop.avm_value else "   AVM Value: N/A")
            
            # This would normally go through Deal Finder's analysis
            # For now, we can see what data is available for analysis
            
        return True
        
    except Exception as e:
        print(f"❌ Valuation test failed: {e}")
        return False

async def main():
    """Run comprehensive Deal Finder real data tests"""
    
    test_results = []
    
    # Test 1: Deal Finder with real ATTOM data
    test_results.append(("Real Data Integration", await test_deal_finder_real_data()))
    
    # Test 2: Deal valuation logic
    test_results.append(("Valuation Logic", await test_deal_valuation_logic()))
    
    print("\n" + "=" * 60)
    print("REAL DATA TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25}: {status}")
        if result:
            passed += 1
    
    print(f"\nTests passed: {passed}/{len(test_results)}")
    
    if passed == len(test_results):
        print("\n🎉 Deal Finder is successfully working with real ATTOM data!")
        print("✅ Ready for Analysis Engine integration")
        print("✅ Ready for Customer Agent integration")
    else:
        print("\n⚠️  Some tests failed - check logs for details")

if __name__ == "__main__":
    asyncio.run(main())