"""
ATTOM Bridge API Test Script
===========================

Comprehensive test script for validating all endpoints in the ATTOM Bridge API.
This script tests all functionality including property search, valuation, 
market analysis, and error handling.

Usage:
    python test_attom_bridge_api.py

Make sure the bridge API is running on localhost:8000 before running tests.
"""

import requests
import json
import time
from typing import Dict, Any, List
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AttomBridgeAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test_result(self, test_name: str, success: bool, details: str = "", response_time: float = 0):
        """Log test result"""
        result = {
            "test_name": test_name,
            "success": success,
            "details": details,
            "response_time_ms": round(response_time * 1000, 2)
        }
        self.test_results.append(result)
        
        status = "PASS" if success else "FAIL"
        logger.info(f"[{status}] {test_name} - {details} ({result['response_time_ms']}ms)")
        
    def run_test(self, test_name: str, test_func):
        """Run a test function and log the result"""
        try:
            start_time = time.time()
            success, details = test_func()
            response_time = time.time() - start_time
            self.log_test_result(test_name, success, details, response_time)
            return success
        except Exception as e:
            response_time = time.time() - start_time if 'start_time' in locals() else 0
            self.log_test_result(test_name, False, f"Exception: {str(e)}", response_time)
            return False
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                if "service" in data and "ATTOM" in data["service"]:
                    return True, f"Root endpoint working: {data['service']}"
                else:
                    return False, f"Unexpected response format: {data}"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
        except Exception as e:
            return False, f"Request failed: {str(e)}"
    
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") in ["healthy", "degraded"]:
                    api_status = "connected" if data.get("api_connection") else "disconnected"
                    return True, f"Health check: {data['status']} (ATTOM API: {api_status})"
                else:
                    return False, f"Invalid health status: {data.get('status')}"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
        except Exception as e:
            return False, f"Request failed: {str(e)}"
    
    def test_property_search_by_zip(self):
        """Test property search by ZIP code"""
        try:
            params = {
                "zip_code": "22030",
                "page_size": 5
            }
            response = self.session.get(f"{self.base_url}/properties/search", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("count", 0) > 0:
                    return True, f"Found {data['count']} properties in ZIP 22030"
                elif data.get("success") and data.get("count") == 0:
                    return True, "Search successful but no properties found (valid response)"
                else:
                    return False, f"Unexpected response: {data}"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
        except Exception as e:
            return False, f"Request failed: {str(e)}"
    
    def test_property_search_by_address(self):
        """Test property search by address"""
        try:
            params = {
                "address": "1600 Pennsylvania Avenue NW",
                "city": "Washington",
                "state": "DC"
            }
            response = self.session.get(f"{self.base_url}/properties/search", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    count = data.get("count", 0)
                    return True, f"Address search successful: {count} properties found"
                else:
                    return False, f"Search failed: {data}"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
        except Exception as e:
            return False, f"Request failed: {str(e)}"
    
    def test_property_search_by_coordinates(self):
        """Test property search by coordinates"""
        try:
            params = {
                "latitude": 38.9072,
                "longitude": -77.0369,
                "radius": 1.0,
                "page_size": 5
            }
            response = self.session.get(f"{self.base_url}/properties/search", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    count = data.get("count", 0)
                    return True, f"Coordinate search successful: {count} properties found"
                else:
                    return False, f"Search failed: {data}"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
        except Exception as e:
            return False, f"Request failed: {str(e)}"
    
    def test_property_search_with_filters(self):
        """Test property search with filters"""
        try:
            params = {
                "zip_code": "22030",
                "min_beds": 2,
                "max_beds": 4,
                "property_type": "sfr",
                "page_size": 3
            }
            response = self.session.get(f"{self.base_url}/properties/search", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    count = data.get("count", 0)
                    return True, f"Filtered search successful: {count} properties found"
                else:
                    return False, f"Search failed: {data}"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
        except Exception as e:
            return False, f"Request failed: {str(e)}"
    
    def test_property_valuation(self):
        """Test property valuation endpoint"""
        try:
            request_data = {
                "address": "123 Main Street",
                "city": "Arlington",
                "state": "VA",
                "zip_code": "22030"
            }
            response = self.session.post(
                f"{self.base_url}/properties/valuation",
                json=request_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    found = data.get("property_found", False)
                    return True, f"Valuation request successful (property found: {found})"
                else:
                    return False, f"Valuation failed: {data}"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
        except Exception as e:
            return False, f"Request failed: {str(e)}"
    
    def test_neighborhood_analysis(self):
        """Test neighborhood analysis endpoint"""
        try:
            zip_code = "22030"
            response = self.session.get(f"{self.base_url}/neighborhoods/{zip_code}/analysis")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    prop_count = data.get("property_count", 0)
                    return True, f"Neighborhood analysis successful: {prop_count} properties analyzed"
                else:
                    return False, f"Analysis failed: {data}"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
        except Exception as e:
            return False, f"Request failed: {str(e)}"
    
    def test_property_comparison(self):
        """Test property comparison endpoint"""
        try:
            addresses = [
                {"address": "123 Oak Street", "city": "Arlington", "state": "VA", "zip_code": "22030"},
                {"address": "456 Pine Avenue", "city": "Arlington", "state": "VA", "zip_code": "22030"}
            ]
            response = self.session.post(
                f"{self.base_url}/properties/compare",
                json=addresses
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    found = data.get("properties_found", 0)
                    requested = data.get("properties_requested", 0)
                    return True, f"Comparison successful: {found}/{requested} properties found"
                else:
                    return False, f"Comparison failed: {data}"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
        except Exception as e:
            return False, f"Request failed: {str(e)}"
    
    def test_market_trends(self):
        """Test market trends endpoint"""
        try:
            zip_code = "22030"
            response = self.session.get(f"{self.base_url}/market/trends/{zip_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    trends = data.get("trends", {})
                    total_props = trends.get("total_properties", 0)
                    return True, f"Market trends retrieved: {total_props} properties analyzed"
                else:
                    return False, f"Trends analysis failed: {data}"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
        except Exception as e:
            return False, f"Request failed: {str(e)}"
    
    def test_value_estimation(self):
        """Test quick value estimation endpoint"""
        try:
            params = {
                "address": "123 Main Street",
                "city": "Arlington",
                "state": "VA",
                "zip_code": "22030"
            }
            response = self.session.get(f"{self.base_url}/properties/estimate-value", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    estimated_value = data.get("estimated_value")
                    confidence = data.get("confidence_score")
                    return True, f"Value estimate: ${estimated_value:,.2f} (confidence: {confidence:.2f})" if estimated_value else "Estimation successful"
                else:
                    return False, f"Estimation failed: {data}"
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
        except Exception as e:
            return False, f"Request failed: {str(e)}"
    
    def test_error_handling(self):
        """Test error handling with invalid requests"""
        try:
            # Test missing required parameters
            response = self.session.get(f"{self.base_url}/properties/search")
            
            if response.status_code == 400:
                return True, "Error handling working: properly rejected invalid request"
            elif response.status_code == 422:
                return True, "Error handling working: validation error returned"
            else:
                return False, f"Expected error response but got HTTP {response.status_code}"
        except Exception as e:
            return False, f"Request failed: {str(e)}"
    
    def test_property_details(self):
        """Test property details endpoint (requires property ID)"""
        try:
            # First get a property ID from search
            search_response = self.session.get(
                f"{self.base_url}/properties/search", 
                params={"zip_code": "22030", "page_size": 1}
            )
            
            if search_response.status_code == 200:
                search_data = search_response.json()
                if search_data.get("success") and search_data.get("count", 0) > 0:
                    property_id = search_data["properties"][0]["property_id"]
                    
                    # Test details endpoint
                    response = self.session.get(f"{self.base_url}/properties/{property_id}/details")
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("success"):
                            return True, f"Property details retrieved for ID: {property_id}"
                        else:
                            return False, f"Details request failed: {data}"
                    else:
                        return False, f"HTTP {response.status_code}: {response.text}"
                else:
                    return True, "No properties found for details test (valid scenario)"
            else:
                return False, f"Could not get property for details test: HTTP {search_response.status_code}"
        except Exception as e:
            return False, f"Request failed: {str(e)}"
    
    def run_all_tests(self):
        """Run all test cases"""
        print("="*80)
        print("ATTOM BRIDGE API COMPREHENSIVE TEST SUITE")
        print("="*80)
        print(f"Testing API at: {self.base_url}")
        print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        tests = [
            ("Root Endpoint", self.test_root_endpoint),
            ("Health Check", self.test_health_endpoint),
            ("Property Search by ZIP", self.test_property_search_by_zip),
            ("Property Search by Address", self.test_property_search_by_address),
            ("Property Search by Coordinates", self.test_property_search_by_coordinates),
            ("Property Search with Filters", self.test_property_search_with_filters),
            ("Property Valuation", self.test_property_valuation),
            ("Neighborhood Analysis", self.test_neighborhood_analysis),
            ("Property Comparison", self.test_property_comparison),
            ("Market Trends", self.test_market_trends),
            ("Value Estimation", self.test_value_estimation),
            ("Property Details", self.test_property_details),
            ("Error Handling", self.test_error_handling)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            success = self.run_test(test_name, test_func)
            if success:
                passed += 1
            time.sleep(0.5)  # Small delay between tests
        
        print()
        print("="*80)
        print("TEST RESULTS SUMMARY")
        print("="*80)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        print()
        
        # Show detailed results
        print("DETAILED RESULTS:")
        print("-" * 80)
        for result in self.test_results:
            status = "✓" if result["success"] else "✗"
            print(f"{status} {result['test_name']}: {result['details']} ({result['response_time_ms']}ms)")
        
        print()
        print("="*80)
        
        return passed, total
    
    def test_api_documentation(self):
        """Test that API documentation is available"""
        try:
            # Test Swagger UI
            response = self.session.get(f"{self.base_url}/docs")
            docs_available = response.status_code == 200
            
            # Test OpenAPI spec
            response = self.session.get(f"{self.base_url}/openapi.json")
            openapi_available = response.status_code == 200
            
            if docs_available and openapi_available:
                return True, "API documentation and OpenAPI spec available"
            elif docs_available:
                return True, "Swagger UI available (OpenAPI spec may be at different endpoint)"
            else:
                return False, "API documentation not accessible"
        except Exception as e:
            return False, f"Documentation test failed: {str(e)}"

def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test ATTOM Bridge API")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--quick", action="store_true", help="Run only basic tests")
    args = parser.parse_args()
    
    tester = AttomBridgeAPITester(args.url)
    
    print("Checking if API is running...")
    try:
        response = requests.get(f"{args.url}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ API not responding properly at {args.url}")
            print("Make sure the bridge API is running:")
            print("  python attom_bridge_api.py")
            return
    except requests.exceptions.RequestException:
        print(f"❌ Cannot connect to API at {args.url}")
        print("Make sure the bridge API is running:")
        print("  python attom_bridge_api.py")
        return
    
    print(f"✅ API is running at {args.url}")
    print()
    
    if args.quick:
        # Run only essential tests
        essential_tests = [
            ("Health Check", tester.test_health_endpoint),
            ("Property Search by ZIP", tester.test_property_search_by_zip),
            ("Value Estimation", tester.test_value_estimation)
        ]
        
        passed = 0
        for test_name, test_func in essential_tests:
            success = tester.run_test(test_name, test_func)
            if success:
                passed += 1
        
        print(f"\nQuick test results: {passed}/{len(essential_tests)} passed")
    else:
        # Run comprehensive test suite
        passed, total = tester.run_all_tests()
        
        if passed == total:
            print("🎉 All tests passed! The API is working correctly.")
        elif passed > total * 0.8:
            print("⚠️  Most tests passed. Some issues detected but API is largely functional.")
        else:
            print("❌ Multiple test failures detected. Check API configuration and ATTOM API connection.")

if __name__ == "__main__":
    main()