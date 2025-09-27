"""
Test ATTOM API with specific address - trying different parameter approaches
"""

import asyncio
import sys
import os
from datetime import datetime
import logging

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.attom_api import ATTOMDataBridge, APIEndpoints
from models.data_models import ATTOMSearchCriteria
from dotenv import load_dotenv
import httpx

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_attom_api_direct():
    """Test ATTOM API with direct HTTP requests to understand parameter requirements"""
    print("🔧 Testing ATTOM API Direct HTTP Requests")
    print("=" * 60)
    
    try:
        load_dotenv()
        api_key = os.getenv('ATTOM_API_KEY')
        
        headers = {
            "Accept": "application/json",
            "apikey": api_key
        }
        
        # Test 1: Try just postal code
        print("\n🔍 Test 1: Search by postal code only...")
        async with httpx.AsyncClient(timeout=30.0) as client:
            params = {
                "format": "json",
                "pageSize": 5,
                "postalcode": "24060"  # Blacksburg, VA zip code
            }
            
            response = await client.get(APIEndpoints.PROPERTY_SEARCH, params=params, headers=headers)
            print(f"Response Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success! Found {len(data.get('property', []))} properties")
                if data.get('property'):
                    prop = data['property'][0]
                    address = prop.get('address', {}).get('oneline', 'N/A')
                    print(f"First property: {address}")
            else:
                print(f"❌ Failed: {response.text}")
        
        # Test 2: Try different parameter format for city/state
        print("\n🔍 Test 2: Search by city/state with different params...")
        async with httpx.AsyncClient(timeout=30.0) as client:
            params = {
                "format": "json",
                "pageSize": 5,
                "address2": "Blacksburg VA"  # Try combined city/state
            }
            
            response = await client.get(APIEndpoints.PROPERTY_SEARCH, params=params, headers=headers)
            print(f"Response Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success! Found {len(data.get('property', []))} properties")
            else:
                print(f"❌ Failed: {response.text}")
        
        # Test 3: Try geoid (geographic identifier)
        print("\n🔍 Test 3: Search by geographic area...")
        async with httpx.AsyncClient(timeout=30.0) as client:
            params = {
                "format": "json",
                "pageSize": 5,
                "geoid": "51161"  # Montgomery County, VA (where Blacksburg is)
            }
            
            response = await client.get(APIEndpoints.PROPERTY_SEARCH, params=params, headers=headers)
            print(f"Response Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success! Found {len(data.get('property', []))} properties")
                if data.get('property'):
                    for i, prop in enumerate(data['property'][:3], 1):
                        address = prop.get('address', {}).get('oneline', 'N/A')
                        print(f"  Property {i}: {address}")
            else:
                print(f"❌ Failed: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Direct API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_working_parameters():
    """Test ATTOM bridge with parameters we know work"""
    print("\n" + "=" * 60)
    print("Testing ATTOM Bridge with Working Parameters")
    print("=" * 60)
    
    try:
        load_dotenv()
        api_key = os.getenv('ATTOM_API_KEY')
        
        # Initialize ATTOM bridge
        attom_bridge = ATTOMDataBridge(api_key=api_key)
        
        # Try search with just postal code
        print("🔍 Testing with postal code search...")
        criteria = ATTOMSearchCriteria(
            zip_code="24060",  # Blacksburg, VA
            max_results=5
        )
        
        properties = await attom_bridge.search_properties(criteria)
        
        if properties:
            print(f"✅ Found {len(properties)} properties in Blacksburg area:")
            for i, prop in enumerate(properties, 1):
                print(f"\n  Property {i}:")
                print(f"    Address: {prop.address}")
                print(f"    City: {prop.city}")
                print(f"    State: {prop.state}")
                print(f"    Zip: {prop.zip_code}")
                if prop.bedrooms:
                    print(f"    Bedrooms: {prop.bedrooms}")
                if prop.bathrooms:
                    print(f"    Bathrooms: {prop.bathrooms}")
                if prop.square_footage:
                    print(f"    Square Feet: {prop.square_footage:,.0f}")
        else:
            print("⚠️  No properties found")
            
        return len(properties) > 0
        
    except Exception as e:
        print(f"❌ ATTOM bridge test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run parameter discovery tests"""
    
    print("🏠 ATTOM API Parameter Discovery Tests")
    print("Finding the correct parameters for property search")
    
    # Test direct API calls to understand parameters
    test1_result = await test_attom_api_direct()
    
    # Test ATTOM bridge with working parameters
    test2_result = await test_working_parameters()
    
    print("\n" + "=" * 60)
    print("PARAMETER TEST SUMMARY")
    print("=" * 60)
    print(f"Direct API Parameter Test: {'✅ PASSED' if test1_result else '❌ FAILED'}")
    print(f"ATTOM Bridge Test:         {'✅ PASSED' if test2_result else '❌ FAILED'}")
    
    if test1_result or test2_result:
        print("\n🎉 Found working parameters for ATTOM API!")
        print("Now we can integrate these with Deal Finder")
    else:
        print("\n⚠️  Need to investigate ATTOM API documentation further")

if __name__ == "__main__":
    asyncio.run(main())