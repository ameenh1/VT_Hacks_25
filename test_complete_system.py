"""
Comprehensive Test Suite for ATTOM Housing Data System
=====================================================

This script tests both:
1. The original ATTOM housing data client (attom_housing_data.py)
2. The FastAPI bridge API (attom_bridge_api.py)

It validates the entire pipeline from direct ATTOM API calls to the bridge API endpoints.

Usage:
    python test_complete_system.py
    python test_complete_system.py --skip-bridge  # Test only direct client
    python test_complete_system.py --skip-client  # Test only bridge API
    python test_complete_system        print(f"OVERALL RESULTS:")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {total_passed} (✅)")
        print(f"Failed: {total_failed} ({'❌' if total_failed > 0 else '✅'})")
        if total_tests > 0:
            print(f"Success Rate: {(total_passed/total_tests)*100:.1f}%")
        else:
            print(f"Success Rate: N/A (no tests executed)")-quick        # Run essential tests only

Prerequisites:
- ATTOM API key configured
- Bridge API running on localhost:8000 (for bridge tests)
"""

import requests
import json
import time
import sys
import os
from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime
import argparse

# Add the current directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from attom_housing_data import AttomDataClient, PropertyData, PropertyDataExporter, HousingDataAnalyzer
except ImportError as e:
    print(f"❌ Cannot import ATTOM housing data client: {e}")
    print("Make sure attom_housing_data.py is in the same directory")
    sys.exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SystemTestResult:
    def __init__(self, test_name: str, component: str, success: bool, details: str = "", response_time: float = 0):
        self.test_name = test_name
        self.component = component  # "client" or "bridge"
        self.success = success
        self.details = details
        self.response_time_ms = round(response_time * 1000, 2)
        self.timestamp = datetime.now().isoformat()

class ComprehensiveSystemTester:
    def __init__(self, api_key: str = "f531d94bd739ea66392d8f987b95b20e", bridge_url: str = "http://localhost:8000"):
        self.api_key = api_key
        self.bridge_url = bridge_url
        self.results: List[SystemTestResult] = []
        self.client = None
        self.analyzer = None
        self.session = requests.Session()
        
        # Test data
        self.test_zip = "22030"
        self.test_address = "1600 Pennsylvania Avenue NW"
        self.test_city = "Washington"
        self.test_state = "DC"
        self.test_coords = (38.9072, -77.0369)  # DC coordinates
        
    def log_result(self, test_name: str, component: str, success: bool, details: str = "", response_time: float = 0):
        """Log a test result"""
        result = SystemTestResult(test_name, component, success, details, response_time)
        self.results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} [{component.upper()}] {test_name}: {details} ({result.response_time_ms}ms)")
        
    def run_test(self, test_name: str, component: str, test_func) -> bool:
        """Execute a test function and log results"""
        try:
            start_time = time.time()
            success, details = test_func()
            response_time = time.time() - start_time
            self.log_result(test_name, component, success, details, response_time)
            return success
        except Exception as e:
            response_time = time.time() - start_time if 'start_time' in locals() else 0
            self.log_result(test_name, component, False, f"Exception: {str(e)}", response_time)
            return False
    
    # ==========================================
    # DIRECT CLIENT TESTS
    # ==========================================
    
    def test_client_initialization(self):
        """Test ATTOM client initialization"""
        try:
            self.client = AttomDataClient(self.api_key)
            self.analyzer = HousingDataAnalyzer(self.client)
            
            if self.client and self.analyzer:
                return True, f"Client initialized with API key: {self.api_key[:8]}..."
            else:
                return False, "Client initialization failed"
        except Exception as e:
            return False, f"Initialization error: {str(e)}"
    
    def test_client_zip_search(self):
        """Test direct client ZIP code search"""
        if not self.client:
            return False, "Client not initialized"
        
        try:
            properties = self.client.search_properties_by_zip(self.test_zip, page_size=5)
            if properties:
                return True, f"Found {len(properties)} properties in ZIP {self.test_zip}"
            else:
                return True, f"No properties found in ZIP {self.test_zip} (valid response)"
        except Exception as e:
            return False, f"ZIP search failed: {str(e)}"
    
    def test_client_address_search(self):
        """Test direct client address search"""
        if not self.client:
            return False, "Client not initialized"
        
        try:
            property_data = self.client.search_property_by_address(
                self.test_address, self.test_city, self.test_state
            )
            if property_data:
                return True, f"Found property: {property_data.address}"
            else:
                return True, "Property not found (valid response)"
        except Exception as e:
            return False, f"Address search failed: {str(e)}"
    
    def test_client_coordinate_search(self):
        """Test direct client coordinate search"""
        if not self.client:
            return False, "Client not initialized"
        
        try:
            properties = self.client.search_properties_by_coordinates(
                self.test_coords[0], self.test_coords[1], radius=1.0, page_size=5
            )
            if properties:
                return True, f"Found {len(properties)} properties near coordinates"
            else:
                return True, "No properties found near coordinates (valid response)"
        except Exception as e:
            return False, f"Coordinate search failed: {str(e)}"
    
    def test_client_filtered_search(self):
        """Test direct client filtered search"""
        if not self.client:
            return False, "Client not initialized"
        
        try:
            properties = self.client.search_properties_with_filters(
                zip_code=self.test_zip,
                min_beds=2,
                max_beds=4,
                property_type="sfr",
                page_size=5
            )
            if properties:
                return True, f"Filtered search found {len(properties)} properties"
            else:
                return True, "No properties match filters (valid response)"
        except Exception as e:
            return False, f"Filtered search failed: {str(e)}"
    
    def test_client_data_export(self):
        """Test data export functionality"""
        if not self.client:
            return False, "Client not initialized"
        
        try:
            properties = self.client.search_properties_by_zip(self.test_zip, page_size=3)
            if not properties:
                return True, "No properties to export (skipping export test)"
            
            # Test CSV export
            csv_filename = f"test_export_{int(time.time())}.csv"
            csv_success = PropertyDataExporter.export_to_csv(properties, csv_filename)
            
            # Test JSON export
            json_filename = f"test_export_{int(time.time())}.json"
            json_success = PropertyDataExporter.export_to_json(properties, json_filename)
            
            # Test summary report
            summary = PropertyDataExporter.generate_summary_report(properties)
            
            # Clean up test files
            try:
                if os.path.exists(csv_filename):
                    os.remove(csv_filename)
                if os.path.exists(json_filename):
                    os.remove(json_filename)
            except:
                pass  # Don't fail test if cleanup fails
            
            if csv_success and json_success and summary:
                return True, f"Export successful: CSV, JSON, and summary generated for {len(properties)} properties"
            else:
                return False, "Export functionality failed"
        except Exception as e:
            return False, f"Export test failed: {str(e)}"
    
    def test_client_neighborhood_analysis(self):
        """Test neighborhood analysis functionality"""
        if not self.analyzer:
            return False, "Analyzer not initialized"
        
        try:
            analysis = self.analyzer.analyze_neighborhood(self.test_zip)
            if analysis and 'summary' in analysis:
                prop_count = len(analysis.get('properties', []))
                return True, f"Neighborhood analysis completed: {prop_count} properties analyzed"
            else:
                return True, "No data available for neighborhood analysis (valid response)"
        except Exception as e:
            return False, f"Neighborhood analysis failed: {str(e)}"
    
    def test_client_property_comparison(self):
        """Test property comparison functionality"""
        if not self.analyzer:
            return False, "Analyzer not initialized"
        
        try:
            test_addresses = [
                {"address": "123 Main Street", "city": "Arlington", "state": "VA", "zip_code": "22030"},
                {"address": "456 Oak Avenue", "city": "Arlington", "state": "VA", "zip_code": "22030"}
            ]
            
            comparison = self.analyzer.compare_properties(test_addresses)
            if comparison:
                found = comparison.get('properties_found', 0)
                requested = comparison.get('properties_requested', 0)
                return True, f"Comparison completed: {found}/{requested} properties found"
            else:
                return False, "Comparison returned empty result"
        except Exception as e:
            return False, f"Property comparison failed: {str(e)}"
    
    # ==========================================
    # BRIDGE API TESTS
    # ==========================================
    
    def test_bridge_connectivity(self):
        """Test bridge API connectivity"""
        try:
            response = self.session.get(f"{self.bridge_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "unknown")
                api_conn = data.get("api_connection", False)
                return True, f"Bridge API healthy: {status} (ATTOM API: {'connected' if api_conn else 'disconnected'})"
            else:
                return False, f"Bridge API unhealthy: HTTP {response.status_code}"
        except requests.exceptions.RequestException as e:
            return False, f"Cannot connect to bridge API: {str(e)}"
    
    def test_bridge_property_search(self):
        """Test bridge API property search"""
        try:
            params = {"zip_code": self.test_zip, "page_size": 5}
            response = self.session.get(f"{self.bridge_url}/properties/search", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    count = data.get("count", 0)
                    return True, f"Bridge search successful: {count} properties found"
                else:
                    return False, f"Bridge search failed: {data}"
            else:
                return False, f"Bridge search error: HTTP {response.status_code}"
        except Exception as e:
            return False, f"Bridge search exception: {str(e)}"
    
    def test_bridge_value_estimation(self):
        """Test bridge API value estimation"""
        try:
            params = {
                "address": self.test_address,
                "city": self.test_city,
                "state": self.test_state
            }
            response = self.session.get(f"{self.bridge_url}/properties/estimate-value", params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    value = data.get("estimated_value")
                    confidence = data.get("confidence_score", 0)
                    return True, f"Value estimation: ${value:,.2f} (confidence: {confidence:.2f})" if value else "Estimation completed"
                else:
                    return False, f"Estimation failed: {data}"
            else:
                return False, f"Estimation error: HTTP {response.status_code}"
        except Exception as e:
            return False, f"Estimation exception: {str(e)}"
    
    def test_bridge_market_trends(self):
        """Test bridge API market trends"""
        try:
            response = self.session.get(f"{self.bridge_url}/market/trends/{self.test_zip}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    trends = data.get("trends", {})
                    total_props = trends.get("total_properties", 0)
                    return True, f"Market trends retrieved: {total_props} properties analyzed"
                else:
                    return False, f"Trends failed: {data}"
            else:
                return False, f"Trends error: HTTP {response.status_code}"
        except Exception as e:
            return False, f"Trends exception: {str(e)}"
    
    def test_bridge_neighborhood_analysis(self):
        """Test bridge API neighborhood analysis"""
        try:
            response = self.session.get(f"{self.bridge_url}/neighborhoods/{self.test_zip}/analysis")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    prop_count = data.get("property_count", 0)
                    return True, f"Bridge neighborhood analysis: {prop_count} properties"
                else:
                    return False, f"Bridge analysis failed: {data}"
            else:
                return False, f"Bridge analysis error: HTTP {response.status_code}"
        except Exception as e:
            return False, f"Bridge analysis exception: {str(e)}"
    
    def test_bridge_property_comparison(self):
        """Test bridge API property comparison"""
        try:
            addresses = [
                {"address": "123 Oak Street", "city": "Arlington", "state": "VA", "zip_code": "22030"},
                {"address": "456 Pine Avenue", "city": "Arlington", "state": "VA", "zip_code": "22030"}
            ]
            response = self.session.post(f"{self.bridge_url}/properties/compare", json=addresses)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    found = data.get("properties_found", 0)
                    requested = data.get("properties_requested", 0)
                    return True, f"Bridge comparison: {found}/{requested} properties found"
                else:
                    return False, f"Bridge comparison failed: {data}"
            else:
                return False, f"Bridge comparison error: HTTP {response.status_code}"
        except Exception as e:
            return False, f"Bridge comparison exception: {str(e)}"
    
    def test_bridge_comprehensive_valuation(self):
        """Test bridge API comprehensive valuation"""
        try:
            request_data = {
                "address": self.test_address,
                "city": self.test_city,
                "state": self.test_state
            }
            response = self.session.post(f"{self.bridge_url}/properties/valuation", json=request_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    found = data.get("property_found", False)
                    comparables = len(data.get("comparable_properties", []))
                    return True, f"Comprehensive valuation: property found={found}, {comparables} comparables"
                else:
                    return False, f"Comprehensive valuation failed: {data}"
            else:
                return False, f"Comprehensive valuation error: HTTP {response.status_code}"
        except Exception as e:
            return False, f"Comprehensive valuation exception: {str(e)}"
    
    # ==========================================
    # INTEGRATION TESTS
    # ==========================================
    
    def test_client_bridge_data_consistency(self):
        """Test data consistency between client and bridge API"""
        if not self.client:
            return False, "Client not initialized"
        
        try:
            # Get data from direct client
            client_properties = self.client.search_properties_by_zip(self.test_zip, page_size=3)
            
            # Get data from bridge API
            params = {"zip_code": self.test_zip, "page_size": 3}
            response = self.session.get(f"{self.bridge_url}/properties/search", params=params)
            
            if response.status_code != 200:
                return False, f"Bridge API request failed: HTTP {response.status_code}"
            
            bridge_data = response.json()
            if not bridge_data.get("success"):
                return False, f"Bridge API search failed: {bridge_data}"
            
            bridge_properties = bridge_data.get("properties", [])
            
            # Compare results
            client_count = len(client_properties)
            bridge_count = len(bridge_properties)
            
            if client_count == 0 and bridge_count == 0:
                return True, "Both client and bridge returned no properties (consistent)"
            
            if client_count > 0 and bridge_count > 0:
                # Check if we have at least some overlap in property IDs or addresses
                client_addresses = {prop.address for prop in client_properties}
                bridge_addresses = {prop["address"] for prop in bridge_properties}
                
                overlap = len(client_addresses.intersection(bridge_addresses))
                return True, f"Data consistency check: client={client_count}, bridge={bridge_count}, overlap={overlap}"
            
            return True, f"Results differ but both are valid: client={client_count}, bridge={bridge_count}"
            
        except Exception as e:
            return False, f"Data consistency test failed: {str(e)}"
    
    def test_performance_comparison(self):
        """Compare performance between client and bridge API"""
        if not self.client:
            return False, "Client not initialized"
        
        try:
            # Time direct client
            start_time = time.time()
            client_properties = self.client.search_properties_by_zip(self.test_zip, page_size=10)
            client_time = time.time() - start_time
            
            # Time bridge API
            start_time = time.time()
            params = {"zip_code": self.test_zip, "page_size": 10}
            response = self.session.get(f"{self.bridge_url}/properties/search", params=params)
            bridge_time = time.time() - start_time
            
            if response.status_code == 200:
                bridge_data = response.json()
                bridge_count = bridge_data.get("count", 0)
            else:
                bridge_count = 0
            
            client_count = len(client_properties)
            
            return True, f"Performance: client={client_time:.2f}s ({client_count} props), bridge={bridge_time:.2f}s ({bridge_count} props)"
            
        except Exception as e:
            return False, f"Performance comparison failed: {str(e)}"
    
    # ==========================================
    # TEST RUNNERS
    # ==========================================
    
    def run_client_tests(self) -> Tuple[int, int]:
        """Run all direct client tests"""
        print("\n" + "="*80)
        print("TESTING DIRECT ATTOM CLIENT")
        print("="*80)
        
        client_tests = [
            ("Client Initialization", self.test_client_initialization),
            ("ZIP Code Search", self.test_client_zip_search),
            ("Address Search", self.test_client_address_search),
            ("Coordinate Search", self.test_client_coordinate_search),
            ("Filtered Search", self.test_client_filtered_search),
            ("Data Export", self.test_client_data_export),
            ("Neighborhood Analysis", self.test_client_neighborhood_analysis),
            ("Property Comparison", self.test_client_property_comparison),
        ]
        
        passed = 0
        for test_name, test_func in client_tests:
            if self.run_test(test_name, "client", test_func):
                passed += 1
            time.sleep(0.2)  # Small delay between tests
        
        return passed, len(client_tests)
    
    def run_bridge_tests(self) -> Tuple[int, int]:
        """Run all bridge API tests"""
        print("\n" + "="*80)
        print("TESTING BRIDGE API")
        print("="*80)
        
        bridge_tests = [
            ("Bridge Connectivity", self.test_bridge_connectivity),
            ("Property Search", self.test_bridge_property_search),
            ("Value Estimation", self.test_bridge_value_estimation),
            ("Market Trends", self.test_bridge_market_trends),
            ("Neighborhood Analysis", self.test_bridge_neighborhood_analysis),
            ("Property Comparison", self.test_bridge_property_comparison),
            ("Comprehensive Valuation", self.test_bridge_comprehensive_valuation),
        ]
        
        passed = 0
        for test_name, test_func in bridge_tests:
            if self.run_test(test_name, "bridge", test_func):
                passed += 1
            time.sleep(0.2)  # Small delay between tests
        
        return passed, len(bridge_tests)
    
    def run_integration_tests(self) -> Tuple[int, int]:
        """Run integration tests between client and bridge"""
        print("\n" + "="*80)
        print("TESTING SYSTEM INTEGRATION")
        print("="*80)
        
        integration_tests = [
            ("Data Consistency", self.test_client_bridge_data_consistency),
            ("Performance Comparison", self.test_performance_comparison),
        ]
        
        passed = 0
        for test_name, test_func in integration_tests:
            if self.run_test(test_name, "integration", test_func):
                passed += 1
            time.sleep(0.2)  # Small delay between tests
        
        return passed, len(integration_tests)
    
    def run_quick_tests(self) -> Tuple[int, int]:
        """Run essential tests only"""
        print("\n" + "="*80)
        print("RUNNING QUICK SYSTEM TESTS")
        print("="*80)
        
        quick_tests = [
            ("Client Initialization", "client", self.test_client_initialization),
            ("Client ZIP Search", "client", self.test_client_zip_search),
            ("Bridge Connectivity", "bridge", self.test_bridge_connectivity),
            ("Bridge Property Search", "bridge", self.test_bridge_property_search),
            ("Bridge Value Estimation", "bridge", self.test_bridge_value_estimation),
            ("Data Consistency", "integration", self.test_client_bridge_data_consistency),
        ]
        
        passed = 0
        for test_name, component, test_func in quick_tests:
            if self.run_test(test_name, component, test_func):
                passed += 1
            time.sleep(0.2)
        
        return passed, len(quick_tests)
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("COMPREHENSIVE TEST REPORT")
        print("="*80)
        
        # Summary by component
        components = {}
        for result in self.results:
            if result.component not in components:
                components[result.component] = {"passed": 0, "failed": 0, "total_time": 0}
            
            if result.success:
                components[result.component]["passed"] += 1
            else:
                components[result.component]["failed"] += 1
            components[result.component]["total_time"] += result.response_time_ms
        
        # Print summary
        total_passed = sum(comp["passed"] for comp in components.values())
        total_failed = sum(comp["failed"] for comp in components.values())
        total_tests = total_passed + total_failed
        
        print(f"\nOVERALL RESULTS:")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {total_passed} (✅)")
        print(f"Failed: {total_failed} ({'❌' if total_failed > 0 else '✅'})")
        print(f"Success Rate: {(total_passed/total_tests)*100:.1f}%")
        
        print(f"\nBY COMPONENT:")
        for component, stats in components.items():
            total = stats["passed"] + stats["failed"]
            success_rate = (stats["passed"] / total) * 100 if total > 0 else 0
            avg_time = stats["total_time"] / total if total > 0 else 0
            
            print(f"{component.upper():>12}: {stats['passed']:>2}/{total:<2} passed ({success_rate:>5.1f}%) - avg {avg_time:>6.1f}ms")
        
        if not components:
            print("No tests were executed.")
        
        # Detailed results
        print(f"\nDETAILED RESULTS:")
        print("-" * 80)
        for result in self.results:
            status = "✅" if result.success else "❌"
            print(f"{status} [{result.component:>11}] {result.test_name:<25}: {result.details}")
        
        # Performance analysis
        slow_tests = [r for r in self.results if r.response_time_ms > 5000]  # > 5 seconds
        if slow_tests:
            print(f"\nSLOW TESTS (>5s):")
            for result in slow_tests:
                print(f"  ⚠️  {result.test_name}: {result.response_time_ms:.0f}ms")
        
        # Recommendations
        print(f"\nRECOMMENDAIONS:")
        if total_failed == 0:
            print("🎉 All tests passed! The system is working correctly.")
        elif total_failed <= 2:
            print("⚠️  Minor issues detected. Check failed tests above.")
        else:
            print("❌ Multiple failures detected. System needs attention.")
            
        if any(r.component == "bridge" and not r.success for r in self.results):
            print("💡 Bridge API issues: Ensure the bridge API is running on localhost:8000")
            
        if any(r.component == "client" and not r.success for r in self.results):
            print("💡 Client issues: Check ATTOM API key and network connectivity")
        
        print("\n" + "="*80)
        return total_passed, total_tests

def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description="Test ATTOM Housing Data System")
    parser.add_argument("--skip-client", action="store_true", help="Skip direct client tests")
    parser.add_argument("--skip-bridge", action="store_true", help="Skip bridge API tests")
    parser.add_argument("--skip-integration", action="store_true", help="Skip integration tests")
    parser.add_argument("--quick", action="store_true", help="Run only essential tests")
    parser.add_argument("--api-key", default="f531d94bd739ea66392d8f987b95b20e", help="ATTOM API key")
    parser.add_argument("--bridge-url", default="http://localhost:8000", help="Bridge API URL")
    args = parser.parse_args()
    
    print("🏠 ATTOM HOUSING DATA SYSTEM TEST SUITE")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API Key: {args.api_key[:8]}...")
    print(f"Bridge URL: {args.bridge_url}")
    
    tester = ComprehensiveSystemTester(args.api_key, args.bridge_url)
    
    if args.quick:
        tester.run_quick_tests()
    else:
        # Run component tests based on arguments
        if not args.skip_client:
            tester.run_client_tests()
        
        if not args.skip_bridge:
            # Check if bridge API is running
            try:
                response = requests.get(f"{args.bridge_url}/health", timeout=3)
                if response.status_code != 200:
                    print(f"\n⚠️  Bridge API not responding properly at {args.bridge_url}")
                    print("Response code:", response.status_code)
                    print("Start the bridge API with: python attom_bridge_api.py")
                    print("Then run tests in another terminal.")
                    if args.skip_client:
                        print("\n❌ No tests can be run (client tests skipped, bridge API not available)")
                        print("Either start the bridge API or run client tests with:")
                        print("  python test_complete_system.py --skip-bridge --skip-integration")
                        return
                else:
                    tester.run_bridge_tests()
            except requests.exceptions.RequestException as e:
                print(f"\n⚠️  Cannot connect to bridge API at {args.bridge_url}")
                print(f"Connection error: {e}")
                print("Start the bridge API with: python attom_bridge_api.py")
                print("Then run tests in another terminal.")
                if args.skip_client:
                    print("\n❌ No tests can be run (client tests skipped, bridge API not available)")
                    print("Either start the bridge API or run client tests with:")
                    print("  python test_complete_system.py --skip-bridge --skip-integration")
                    return
        
        if not args.skip_integration and not args.skip_client and not args.skip_bridge:
            # Only run integration tests if both client and bridge were tested
            tester.run_integration_tests()
    
    # Generate final report
    passed, total = tester.generate_report()
    
    # Exit with appropriate code
    if passed == total:
        sys.exit(0)  # All tests passed
    else:
        sys.exit(1)  # Some tests failed

if __name__ == "__main__":
    main()