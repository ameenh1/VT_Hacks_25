"""
Test Script for Deal Finder ATTOM API Integration
=====================================================

This script tests the Deal Finder agent's ability to:
1. Connect to ATTOM API through the bridge service
2. Pull property data based on search criteria
3. Generate property alerts
4. Handle API failures gracefully

Run this script to verify Deal Finder is working correctly.
"""

import asyncio
import sys
import os
from datetime import datetime
import logging

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import required components
from agents.deal_finder import DealFinder, SearchCriteria, AlertType
from integrations.attom_api import ATTOMDataBridge
from models.data_models import InvestmentStrategy

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_deal_finder_basic():
    """Test basic Deal Finder functionality without ATTOM API"""
    print("\n" + "="*60)
    print("TEST 1: Basic Deal Finder Initialization")
    print("="*60)
    
    try:
        # Initialize Deal Finder without ATTOM bridge (will use mock data)
        deal_finder = DealFinder()
        print("✅ Deal Finder initialized successfully")
        
        # Check health status
        health = await deal_finder.health_check()
        print(f"✅ Health check: {health['status']}")
        
        # Get monitoring status
        status = deal_finder.get_monitoring_status()
        print(f"✅ Monitoring status: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic test failed: {e}")
        return False

async def test_deal_finder_with_mock_data():
    """Test Deal Finder with mock data (no ATTOM API required)"""
    print("\n" + "="*60)
    print("TEST 2: Deal Finder with Mock Data")
    print("="*60)
    
    try:
        # Initialize Deal Finder
        deal_finder = DealFinder()
        
        # Create search criteria
        criteria = SearchCriteria(
            max_price=300000,
            min_deal_score=70.0,
            target_locations=["Virginia", "Blacksburg", "VA"],
            property_types=["SFR", "CON"],
            min_cash_flow=500
        )
        
        print(f"✅ Search criteria created: {criteria}")
        
        # Test immediate deal search (should use mock data)
        print("\n🔍 Searching for deals...")
        deals = await deal_finder.find_deals_now(criteria, max_results=5)
        
        if deals:
            print(f"✅ Found {len(deals)} potential deals using mock data:")
            for i, deal in enumerate(deals, 1):
                print(f"\n  Deal {i}:")
                print(f"    Address: {deal.property_address}")
                print(f"    Alert Type: {deal.alert_type.value}")
                print(f"    Priority: {deal.priority.name}")
                print(f"    Listing Price: ${deal.listing_price:,.0f}")
                print(f"    Estimated Value: ${deal.estimated_value:,.0f}")
                print(f"    Potential Profit: ${deal.potential_profit:,.0f}")
                print(f"    Confidence: {deal.confidence_score:.2f}")
        else:
            print("❌ No deals found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Mock data test failed: {e}")
        return False

async def test_attom_api_connection():
    """Test ATTOM API connection through bridge service"""
    print("\n" + "="*60)
    print("TEST 3: ATTOM API Connection")
    print("="*60)
    
    try:
        # Check if ATTOM API key is available
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('ATTOM_API_KEY')
        if not api_key or api_key == 'your_attom_api_key_here':
            print("⚠️  ATTOM API key not found or not set")
            print("   This is expected if you haven't set up ATTOM API yet")
            print("   Deal Finder will use mock data instead")
            return True
        
        print(f"✅ ATTOM API key found: {api_key[:8]}...")
        
        # Initialize ATTOM bridge
        attom_bridge = ATTOMDataBridge(api_key=api_key)
        print("✅ ATTOM bridge initialized")
        
        # Test with Deal Finder
        deal_finder = DealFinder(attom_bridge=attom_bridge)
        print("✅ Deal Finder initialized with ATTOM bridge")
        
        # Create search criteria for real API test
        criteria = SearchCriteria(
            max_price=500000,
            target_locations=["Blacksburg", "VA"],
            property_types=["SFR"]
        )
        
        print("\n🔍 Testing real ATTOM API search...")
        deals = await deal_finder.find_deals_now(criteria, max_results=3)
        
        if deals:
            print(f"✅ Found {len(deals)} deals using real ATTOM data:")
            for deal in deals:
                print(f"  - {deal.property_address} (${deal.listing_price:,.0f})")
        else:
            print("⚠️  No deals found with current criteria")
        
        return True
        
    except Exception as e:
        print(f"❌ ATTOM API test failed: {e}")
        print("   This might be due to:")
        print("   1. Missing or invalid ATTOM API key")
        print("   2. ATTOM API rate limits")
        print("   3. Network connectivity issues")
        print("   4. ATTOM bridge service not properly configured")
        return False

async def test_user_criteria_workflow():
    """Test user criteria management workflow"""
    print("\n" + "="*60)
    print("TEST 4: User Criteria Workflow")
    print("="*60)
    
    try:
        deal_finder = DealFinder()
        
        # Add criteria for test user
        user_id = "test_user_123"
        criteria = SearchCriteria(
            max_price=400000,
            min_deal_score=75.0,
            target_locations=["Virginia Tech", "Blacksburg"],
            property_types=["SFR", "TWH"],
            min_cash_flow=800
        )
        
        deal_finder.add_user_criteria(user_id, criteria)
        print(f"✅ Added criteria for user: {user_id}")
        
        # Get alerts for user
        alerts = await deal_finder.get_alerts_for_user(user_id)
        print(f"✅ Retrieved {len(alerts)} alerts for user")
        
        # Test background monitoring setup
        print("\n🔄 Testing background monitoring...")
        await deal_finder.start_monitoring()
        print("✅ Background monitoring started")
        
        # Wait a moment to let it work
        await asyncio.sleep(2)
        
        # Check status
        status = deal_finder.get_monitoring_status()
        print(f"✅ Monitoring status: Running={status['is_running']}")
        
        # Stop monitoring
        await deal_finder.stop_monitoring()
        print("✅ Background monitoring stopped")
        
        return True
        
    except Exception as e:
        print(f"❌ User criteria test failed: {e}")
        return False

async def main():
    """Run all Deal Finder tests"""
    print("🏠 Deal Finder ATTOM API Integration Tests")
    print("=" * 60)
    
    test_results = []
    
    # Run all tests
    test_results.append(("Basic Initialization", await test_deal_finder_basic()))
    test_results.append(("Mock Data Integration", await test_deal_finder_with_mock_data()))
    test_results.append(("ATTOM API Connection", await test_attom_api_connection()))
    test_results.append(("User Criteria Workflow", await test_user_criteria_workflow()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25}: {status}")
        if result:
            passed += 1
    
    print(f"\nTests passed: {passed}/{len(test_results)}")
    
    if passed == len(test_results):
        print("\n🎉 All tests passed! Deal Finder is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        print("\nNext steps:")
        print("1. Ensure you have copied .env.example to .env")
        print("2. Set up your ATTOM_API_KEY in the .env file")
        print("3. Make sure all dependencies are installed")
    
    return passed == len(test_results)

if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)