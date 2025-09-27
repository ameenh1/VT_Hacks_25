"""
ATTOM API Raw Response Inspector
Debug what fields are actually available in ATTOM API responses
"""

import asyncio
import sys
import os
import json
from datetime import datetime
import logging

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.attom_api import ATTOMDataBridge, APIEndpoints
from dotenv import load_dotenv
import httpx

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def inspect_attom_response():
    """Get raw ATTOM API response to see actual data structure"""
    print("🔍 ATTOM API Raw Response Inspector")
    print("=" * 60)
    
    try:
        load_dotenv()
        api_key = os.getenv('ATTOM_API_KEY')
        
        headers = {
            "Accept": "application/json",
            "apikey": api_key
        }
        
        # Make direct API call to see raw response
        async with httpx.AsyncClient(timeout=30.0) as client:
            params = {
                "format": "json",
                "pageSize": 1,  # Just get one property for inspection
                "postalcode": "24060"
            }
            
            response = await client.get(APIEndpoints.PROPERTY_SEARCH, params=params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response Status: {response.status_code}")
                print(f"✅ Total Properties: {len(data.get('property', []))}")
                
                if data.get('property'):
                    print("\n📋 Raw Property Data Structure:")
                    prop = data['property'][0]
                    
                    # Pretty print the JSON structure
                    print(json.dumps(prop, indent=2))
                    
                    print("\n📊 Available Top-Level Keys:")
                    for key in prop.keys():
                        print(f"  - {key}")
                        
                    print("\n🏠 Address Structure:")
                    if 'address' in prop:
                        address_keys = prop['address'].keys() if prop['address'] else []
                        for key in address_keys:
                            value = prop['address'][key]
                            print(f"  - address.{key}: {value}")
                    
                    print("\n🏗️ Building Structure:")
                    if 'building' in prop:
                        building_keys = prop['building'].keys() if prop['building'] else []
                        for key in building_keys:
                            print(f"  - building.{key}: {prop['building'][key]}")
                    
                    print("\n📈 Assessment Structure:")
                    if 'assessment' in prop:
                        assessment_keys = prop['assessment'].keys() if prop['assessment'] else []
                        for key in assessment_keys:
                            print(f"  - assessment.{key}: {prop['assessment'][key]}")
                    
                    print("\n💰 Sale Structure:")
                    if 'sale' in prop:
                        sale_keys = prop['sale'].keys() if prop['sale'] else []
                        for key in sale_keys:
                            print(f"  - sale.{key}: {prop['sale'][key]}")
                    else:
                        print("  - No 'sale' data in basic profile")
                    
                    print("\n🎯 AVM Structure:")
                    if 'avm' in prop:
                        avm_keys = prop['avm'].keys() if prop['avm'] else []
                        for key in avm_keys:
                            print(f"  - avm.{key}: {prop['avm'][key]}")
                    else:
                        print("  - No 'avm' data in basic profile")
                        
                    return True
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_different_endpoints():
    """Test different ATTOM endpoints to find where valuation data lives"""
    print("\n" + "=" * 60)
    print("Testing Different ATTOM Endpoints")
    print("=" * 60)
    
    load_dotenv()
    api_key = os.getenv('ATTOM_API_KEY')
    
    headers = {
        "Accept": "application/json",
        "apikey": api_key
    }
    
    # Test basic property detail endpoint (might have more data)
    print("\n🔍 Testing Property Detail Endpoint:")
    async with httpx.AsyncClient(timeout=30.0) as client:
        params = {
            "format": "json",
            "postalcode": "24060"
        }
        
        detail_url = "https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/detail"
        response = await client.get(detail_url, params=params, headers=headers)
        print(f"Property Detail Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('property'):
                prop = data['property'][0]
                print("Available sections in detail endpoint:")
                for key in prop.keys():
                    print(f"  - {key}")
                    
                # Check if this has AVM or sale data
                if 'avm' in prop:
                    print(f"  AVM data found: {prop['avm']}")
                if 'sale' in prop:
                    print(f"  Sale data found: {prop['sale']}")
        else:
            print(f"Detail endpoint failed: {response.text}")
    
    # Test AVM endpoint specifically
    print("\n🔍 Testing AVM Endpoint:")
    async with httpx.AsyncClient(timeout=30.0) as client:
        params = {
            "format": "json",
            "postalcode": "24060"
        }
        
        response = await client.get(APIEndpoints.ESTIMATED_VALUE, params=params, headers=headers)
        print(f"AVM Endpoint Status: {response.status_code}")
        if response.status_code != 200:
            print(f"AVM endpoint error: {response.text}")

async def main():
    print("🏠 ATTOM API Data Structure Investigation")
    print("Understanding why key fields are missing")
    
    await inspect_attom_response()
    await test_different_endpoints()
    
    print("\n" + "=" * 60)
    print("🎯 INVESTIGATION COMPLETE")
    print("Check the output above to see:")
    print("1. What fields are actually available in ATTOM responses")
    print("2. Which endpoints provide valuation data")
    print("3. How to properly extract address, sale, and AVM data")

if __name__ == "__main__":
    asyncio.run(main())