"""
ATTOM Housing Data API Client
============================

This script provides a comprehensive interface to the ATTOM Data API for pulling
detailed house data including location, specifications, bedrooms, bathrooms,
build year, and listing prices.

Author: VT Hacks 25 Team
API Documentation: https://api.developer.attomdata.com/docs
"""

import requests
import json
import csv
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PropertyData:
    """Data class to store structured property information"""
    property_id: str
    address: str
    city: str
    state: str
    zip_code: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    build_year: Optional[int] = None
    listing_price: Optional[float] = None
    property_type: Optional[str] = None
    square_footage: Optional[int] = None
    lot_size: Optional[float] = None
    last_sale_price: Optional[float] = None
    last_sale_date: Optional[str] = None
    assessed_value: Optional[float] = None
    avm_value: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert PropertyData to dictionary"""
        return {
            'property_id': self.property_id,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'build_year': self.build_year,
            'listing_price': self.listing_price,
            'property_type': self.property_type,
            'square_footage': self.square_footage,
            'lot_size': self.lot_size,
            'last_sale_price': self.last_sale_price,
            'last_sale_date': self.last_sale_date,
            'assessed_value': self.assessed_value,
            'avm_value': self.avm_value
        }

class AttomDataClient:
    """
    Client class for interacting with the ATTOM Data API
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the ATTOM Data client
        
        Args:
            api_key (str): Your ATTOM Data API key
        """
        self.api_key = api_key
        self.base_url = "https://api.gateway.attomdata.com"
        self.headers = {
            'Accept': 'application/json',
            'APIKey': self.api_key
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Optional[Dict]:
        """
        Make a request to the ATTOM API
        
        Args:
            endpoint (str): API endpoint
            params (dict): Query parameters
            
        Returns:
            dict: JSON response data or None if error
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Check API status
            if 'status' in data and data['status']['code'] != 0:
                logger.error(f"API Error: {data['status']['msg']}")
                return None
                
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return None
            
    def _extract_property_data(self, property_item: Dict) -> PropertyData:
        """
        Extract property data from API response item
        
        Args:
            property_item (dict): Property data from API response
            
        Returns:
            PropertyData: Structured property information
        """
        # Basic property identification
        prop_id = property_item.get('identifier', {}).get('attomId', '')
        if not prop_id:
            prop_id = property_item.get('identifier', {}).get('Id', '')
            
        # Address information
        address_info = property_item.get('address', {})
        address = address_info.get('line1', '')
        city = address_info.get('locality', '')
        state = address_info.get('countrySubd', '')
        zip_code = address_info.get('postal1', '')
        
        # Geographic coordinates
        location = property_item.get('location', {})
        latitude = location.get('latitude')
        longitude = location.get('longitude')
        
        # Building details
        building = property_item.get('building', {})
        size = building.get('size', {})
        rooms = building.get('rooms', {})
        
        bedrooms = rooms.get('beds')
        bathrooms = rooms.get('bathsTotal')
        square_footage = size.get('universalSize')
        build_year = building.get('summary', {}).get('yearBuilt')
        property_type = building.get('summary', {}).get('propType')
        
        # Lot information
        lot = property_item.get('lot', {})
        lot_size = lot.get('lotSize1')  # in acres
        
        # Sale information
        sale = property_item.get('sale', {})
        last_sale_price = sale.get('amount', {}).get('saleAmt')
        last_sale_date = sale.get('salesSearchDate')
        
        # Assessment and valuation
        assessment = property_item.get('assessment', {})
        assessed_value = assessment.get('assessed', {}).get('assdTtlValue')
        
        avm = property_item.get('avm', {})
        avm_value = avm.get('amount', {}).get('value')
        
        # Current listing price (if available)
        listing_price = property_item.get('listing', {}).get('listPrice')
        
        return PropertyData(
            property_id=prop_id,
            address=address,
            city=city,
            state=state,
            zip_code=zip_code,
            latitude=latitude,
            longitude=longitude,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            build_year=build_year,
            listing_price=listing_price,
            property_type=property_type,
            square_footage=square_footage,
            lot_size=lot_size,
            last_sale_price=last_sale_price,
            last_sale_date=last_sale_date,
            assessed_value=assessed_value,
            avm_value=avm_value
        )
    
    def search_properties_by_zip(self, zip_code: str, page_size: int = 50, property_type: str = None) -> List[PropertyData]:
        """
        Search for properties by zip code
        
        Args:
            zip_code (str): ZIP code to search
            page_size (int): Number of properties to return (max 100)
            property_type (str): Property type filter (e.g., 'sfr', 'apartment', 'condo')
            
        Returns:
            List[PropertyData]: List of property data objects
        """
        endpoint = "/propertyapi/v1.0.0/property/detail"
        params = {
            'postalcode': zip_code,
            'pageSize': min(page_size, 100)
        }
        
        if property_type:
            params['propertytype'] = property_type
            
        logger.info(f"Searching properties in ZIP code: {zip_code}")
        
        response = self._make_request(endpoint, params)
        if not response:
            return []
            
        properties = []
        if 'property' in response:
            property_list = response['property']
            if isinstance(property_list, dict):
                property_list = [property_list]
                
            for prop in property_list:
                try:
                    property_data = self._extract_property_data(prop)
                    properties.append(property_data)
                except Exception as e:
                    logger.warning(f"Error extracting property data: {e}")
                    
        logger.info(f"Found {len(properties)} properties in ZIP {zip_code}")
        return properties
    
    def search_property_by_address(self, address: str, city: str, state: str, zip_code: str = None) -> Optional[PropertyData]:
        """
        Search for a specific property by address
        
        Args:
            address (str): Street address
            city (str): City name
            state (str): State abbreviation
            zip_code (str): ZIP code (optional)
            
        Returns:
            PropertyData: Property data object or None if not found
        """
        endpoint = "/propertyapi/v1.0.0/property/detail"
        
        # Format address for API
        if zip_code:
            full_address = f"{address}, {city}, {state} {zip_code}"
        else:
            full_address = f"{address}, {city}, {state}"
            
        params = {
            'address': full_address
        }
        
        logger.info(f"Searching property at: {full_address}")
        
        response = self._make_request(endpoint, params)
        if not response:
            return None
            
        if 'property' in response:
            property_list = response['property']
            if isinstance(property_list, list) and len(property_list) > 0:
                property_item = property_list[0]  # Take first match
            elif isinstance(property_list, dict):
                property_item = property_list
            else:
                logger.warning("No property found at the given address")
                return None
                
            try:
                return self._extract_property_data(property_item)
            except Exception as e:
                logger.error(f"Error extracting property data: {e}")
                return None
                
        return None
    
    def search_properties_by_coordinates(self, latitude: float, longitude: float, radius: float = 1.0, page_size: int = 50) -> List[PropertyData]:
        """
        Search for properties within a radius of given coordinates
        
        Args:
            latitude (float): Latitude
            longitude (float): Longitude 
            radius (float): Search radius in miles (default 1.0, max 20.0)
            page_size (int): Number of properties to return (max 100)
            
        Returns:
            List[PropertyData]: List of property data objects
        """
        endpoint = "/propertyapi/v1.0.0/property/detail"
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'radius': min(radius, 20.0),
            'pageSize': min(page_size, 100)
        }
        
        logger.info(f"Searching properties near coordinates: {latitude}, {longitude} (radius: {radius} miles)")
        
        response = self._make_request(endpoint, params)
        if not response:
            return []
            
        properties = []
        if 'property' in response:
            property_list = response['property']
            if isinstance(property_list, dict):
                property_list = [property_list]
                
            for prop in property_list:
                try:
                    property_data = self._extract_property_data(prop)
                    properties.append(property_data)
                except Exception as e:
                    logger.warning(f"Error extracting property data: {e}")
                    
        logger.info(f"Found {len(properties)} properties near coordinates")
        return properties
    
    def search_properties_with_filters(self, zip_code: str, min_beds: int = None, max_beds: int = None, 
                                     min_baths: float = None, max_baths: float = None,
                                     min_price: float = None, max_price: float = None,
                                     min_year: int = None, max_year: int = None,
                                     property_type: str = None, page_size: int = 50) -> List[PropertyData]:
        """
        Search for properties with specific filters
        
        Args:
            zip_code (str): ZIP code to search
            min_beds (int): Minimum bedrooms
            max_beds (int): Maximum bedrooms
            min_baths (float): Minimum bathrooms
            max_baths (float): Maximum bathrooms
            min_price (float): Minimum sale/listing price
            max_price (float): Maximum sale/listing price
            min_year (int): Minimum build year
            max_year (int): Maximum build year
            property_type (str): Property type filter
            page_size (int): Number of properties to return
            
        Returns:
            List[PropertyData]: List of property data objects
        """
        endpoint = "/propertyapi/v1.0.0/property/detail"
        params = {
            'postalcode': zip_code,
            'pageSize': min(page_size, 100)
        }
        
        # Add filters
        if min_beds:
            params['minBeds'] = min_beds
        if max_beds:
            params['maxBeds'] = max_beds
        if min_baths:
            params['minBathsTotal'] = min_baths
        if max_baths:
            params['maxBathsTotal'] = max_baths
        if min_price:
            params['minSaleAmt'] = min_price
        if max_price:
            params['maxSaleAmt'] = max_price
        if min_year:
            params['minYearBuilt'] = min_year
        if max_year:
            params['maxYearBuilt'] = max_year
        if property_type:
            params['propertytype'] = property_type
            
        logger.info(f"Searching properties in ZIP {zip_code} with filters")
        
        response = self._make_request(endpoint, params)
        if not response:
            return []
            
        properties = []
        if 'property' in response:
            property_list = response['property']
            if isinstance(property_list, dict):
                property_list = [property_list]
                
            for prop in property_list:
                try:
                    property_data = self._extract_property_data(prop)
                    properties.append(property_data)
                except Exception as e:
                    logger.warning(f"Error extracting property data: {e}")
                    
        logger.info(f"Found {len(properties)} filtered properties")
        return properties
    
    def get_property_sales_history(self, property_id: str) -> Dict[str, Any]:
        """
        Get sales history for a specific property
        
        Args:
            property_id (str): ATTOM property ID
            
        Returns:
            Dict: Sales history data
        """
        endpoint = "/propertyapi/v1.0.0/saleshistory/detail"
        params = {'id': property_id}
        
        logger.info(f"Getting sales history for property ID: {property_id}")
        
        response = self._make_request(endpoint, params)
        if not response:
            return {}
            
        return response
    
    def get_property_assessment_data(self, property_id: str) -> Dict[str, Any]:
        """
        Get assessment data for a specific property
        
        Args:
            property_id (str): ATTOM property ID
            
        Returns:
            Dict: Assessment data
        """
        endpoint = "/propertyapi/v1.0.0/assessment/detail"
        params = {'id': property_id}
        
        logger.info(f"Getting assessment data for property ID: {property_id}")
        
        response = self._make_request(endpoint, params)
        if not response:
            return {}
            
        return response
    
    def get_property_avm_value(self, property_id: str) -> Dict[str, Any]:
        """
        Get AVM (Automated Valuation Model) data for a specific property
        
        Args:
            property_id (str): ATTOM property ID
            
        Returns:
            Dict: AVM data
        """
        endpoint = "/propertyapi/v1.0.0/attomavm/detail"
        params = {'id': property_id}
        
        logger.info(f"Getting AVM value for property ID: {property_id}")
        
        response = self._make_request(endpoint, params)
        if not response:
            return {}
            
        return response

if __name__ == "__main__":
    # Example API key placeholder
    API_KEY = "f531d94bd739ea66392d8f987b95b20e"
    
    # Initialize client
    client = AttomDataClient(API_KEY)
    print("ATTOM Housing Data Client initialized successfully!")
    print(f"Base URL: {client.base_url}")
    print(f"Headers configured with API key")

class PropertyDataExporter:
    """
    Utility class for exporting property data to various formats
    """
    
    @staticmethod
    def export_to_csv(properties: List[PropertyData], filename: str) -> bool:
        """
        Export property data to CSV file
        
        Args:
            properties (List[PropertyData]): List of property data objects
            filename (str): Output filename
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not properties:
            logger.warning("No properties to export")
            return False
            
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'property_id', 'address', 'city', 'state', 'zip_code',
                    'latitude', 'longitude', 'bedrooms', 'bathrooms', 'build_year',
                    'listing_price', 'property_type', 'square_footage', 'lot_size',
                    'last_sale_price', 'last_sale_date', 'assessed_value', 'avm_value'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for prop in properties:
                    writer.writerow(prop.to_dict())
                    
            logger.info(f"Successfully exported {len(properties)} properties to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return False
    
    @staticmethod
    def export_to_json(properties: List[PropertyData], filename: str, indent: int = 2) -> bool:
        """
        Export property data to JSON file
        
        Args:
            properties (List[PropertyData]): List of property data objects
            filename (str): Output filename
            indent (int): JSON indentation level
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not properties:
            logger.warning("No properties to export")
            return False
            
        try:
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'property_count': len(properties),
                'properties': [prop.to_dict() for prop in properties]
            }
            
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(export_data, jsonfile, indent=indent, default=str)
                
            logger.info(f"Successfully exported {len(properties)} properties to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            return False
    
    @staticmethod
    def generate_summary_report(properties: List[PropertyData]) -> Dict[str, Any]:
        """
        Generate a summary report of property data
        
        Args:
            properties (List[PropertyData]): List of property data objects
            
        Returns:
            Dict: Summary statistics
        """
        if not properties:
            return {}
            
        summary = {
            'total_properties': len(properties),
            'property_types': {},
            'bedrooms': {'min': None, 'max': None, 'avg': None},
            'bathrooms': {'min': None, 'max': None, 'avg': None},
            'build_years': {'min': None, 'max': None, 'avg': None},
            'prices': {'min': None, 'max': None, 'avg': None},
            'square_footage': {'min': None, 'max': None, 'avg': None}
        }
        
        # Property types count
        for prop in properties:
            if prop.property_type:
                prop_type = prop.property_type
                summary['property_types'][prop_type] = summary['property_types'].get(prop_type, 0) + 1
        
        # Numerical stats
        bedrooms = [p.bedrooms for p in properties if p.bedrooms is not None]
        bathrooms = [p.bathrooms for p in properties if p.bathrooms is not None]
        build_years = [p.build_year for p in properties if p.build_year is not None]
        prices = [p.last_sale_price or p.listing_price or p.assessed_value or p.avm_value 
                 for p in properties if any([p.last_sale_price, p.listing_price, p.assessed_value, p.avm_value])]
        square_feet = [p.square_footage for p in properties if p.square_footage is not None]
        
        for data_list, key in [(bedrooms, 'bedrooms'), (bathrooms, 'bathrooms'), 
                              (build_years, 'build_years'), (prices, 'prices'),
                              (square_feet, 'square_footage')]:
            if data_list:
                summary[key] = {
                    'min': min(data_list),
                    'max': max(data_list),
                    'avg': round(sum(data_list) / len(data_list), 2)
                }
        
        return summary

class HousingDataAnalyzer:
    """
    Utility class for analyzing housing data
    """
    
    def __init__(self, api_client: AttomDataClient):
        self.client = api_client
        self.exporter = PropertyDataExporter()
    
    def analyze_neighborhood(self, zip_code: str, export_csv: bool = False, export_json: bool = False) -> Dict[str, Any]:
        """
        Analyze all properties in a neighborhood (ZIP code)
        
        Args:
            zip_code (str): ZIP code to analyze
            export_csv (bool): Whether to export results to CSV
            export_json (bool): Whether to export results to JSON
            
        Returns:
            Dict: Analysis results including summary and properties
        """
        logger.info(f"Starting neighborhood analysis for ZIP code: {zip_code}")
        
        # Search for all properties in the ZIP code
        properties = self.client.search_properties_by_zip(zip_code, page_size=100)
        
        if not properties:
            logger.warning(f"No properties found in ZIP code {zip_code}")
            return {'properties': [], 'summary': {}}
        
        # Generate summary
        summary = self.exporter.generate_summary_report(properties)
        
        # Export if requested
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if export_csv:
            csv_filename = f"properties_{zip_code}_{timestamp}.csv"
            self.exporter.export_to_csv(properties, csv_filename)
            
        if export_json:
            json_filename = f"properties_{zip_code}_{timestamp}.json"
            self.exporter.export_to_json(properties, json_filename)
        
        result = {
            'zip_code': zip_code,
            'analysis_timestamp': datetime.now().isoformat(),
            'properties': properties,
            'summary': summary
        }
        
        logger.info(f"Completed neighborhood analysis for ZIP {zip_code}: {len(properties)} properties found")
        return result
    
    def compare_properties(self, property_addresses: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Compare multiple properties side by side
        
        Args:
            property_addresses (List[Dict]): List of address dictionaries with keys: address, city, state, zip_code
            
        Returns:
            Dict: Comparison results
        """
        logger.info(f"Comparing {len(property_addresses)} properties")
        
        properties = []
        for addr in property_addresses:
            prop = self.client.search_property_by_address(
                address=addr['address'],
                city=addr['city'],
                state=addr['state'],
                zip_code=addr.get('zip_code')
            )
            if prop:
                properties.append(prop)
            else:
                logger.warning(f"Property not found: {addr}")
        
        comparison = {
            'comparison_timestamp': datetime.now().isoformat(),
            'properties_found': len(properties),
            'properties_requested': len(property_addresses),
            'properties': properties,
            'comparison_table': []
        }
        
        # Create comparison table
        if properties:
            fields = ['address', 'bedrooms', 'bathrooms', 'build_year', 'square_footage', 
                     'last_sale_price', 'assessed_value', 'avm_value']
            
            for prop in properties:
                row = {}
                for field in fields:
                    row[field] = getattr(prop, field, None)
                comparison['comparison_table'].append(row)
        
        return comparison
    
    def find_similar_properties(self, reference_property: PropertyData, search_radius: float = 5.0) -> List[PropertyData]:
        """
        Find properties similar to a reference property
        
        Args:
            reference_property (PropertyData): Property to use as reference
            search_radius (float): Search radius in miles
            
        Returns:
            List[PropertyData]: List of similar properties
        """
        if not reference_property.latitude or not reference_property.longitude:
            logger.error("Reference property must have coordinates for similarity search")
            return []
        
        # Search in the area
        nearby_properties = self.client.search_properties_by_coordinates(
            latitude=reference_property.latitude,
            longitude=reference_property.longitude,
            radius=search_radius,
            page_size=100
        )
        
        # Filter for similar properties
        similar_properties = []
        for prop in nearby_properties:
            if prop.property_id == reference_property.property_id:
                continue  # Skip the reference property itself
                
            # Check similarity criteria
            similar = True
            
            # Property type should match
            if reference_property.property_type and prop.property_type:
                if reference_property.property_type != prop.property_type:
                    similar = False
            
            # Bedrooms within 1 of reference
            if reference_property.bedrooms and prop.bedrooms:
                if abs(reference_property.bedrooms - prop.bedrooms) > 1:
                    similar = False
            
            # Bathrooms within 1 of reference
            if reference_property.bathrooms and prop.bathrooms:
                if abs(reference_property.bathrooms - prop.bathrooms) > 1:
                    similar = False
            
            # Build year within 10 years
            if reference_property.build_year and prop.build_year:
                if abs(reference_property.build_year - prop.build_year) > 10:
                    similar = False
            
            if similar:
                similar_properties.append(prop)
        
        logger.info(f"Found {len(similar_properties)} similar properties")
        return similar_properties


# Example usage and demonstration
def main():
    """
    Demonstration of the ATTOM Housing Data Client
    """
    print("="*60)
    print("ATTOM Housing Data API Client - Demo")
    print("="*60)
    
    # Initialize the client
    API_KEY = "f531d94bd739ea66392d8f987b95b20e"
    client = AttomDataClient(API_KEY)
    analyzer = HousingDataAnalyzer(client)
    exporter = PropertyDataExporter()
    
    # Example 1: Search properties by ZIP code
    print("\n1. Searching properties by ZIP code (22030)...")
    properties = client.search_properties_by_zip("22030", page_size=10)
    if properties:
        print(f"Found {len(properties)} properties")
        for i, prop in enumerate(properties[:3], 1):  # Show first 3
            print(f"  {i}. {prop.address}, {prop.city}, {prop.state} - {prop.bedrooms} beds, {prop.bathrooms} baths")
    else:
        print("No properties found")
    
    # Example 2: Search specific property by address
    print("\n2. Searching for a specific property...")
    property = client.search_property_by_address(
        address="1600 Pennsylvania Avenue NW",
        city="Washington",
        state="DC",
        zip_code="20500"
    )
    if property:
        print(f"Found: {property.address}")
        print(f"Built: {property.build_year}")
        print(f"Bedrooms: {property.bedrooms}, Bathrooms: {property.bathrooms}")
    else:
        print("Property not found")
    
    # Example 3: Search by coordinates
    print("\n3. Searching properties by coordinates (DC area)...")
    coord_properties = client.search_properties_by_coordinates(
        latitude=38.9072, longitude=-77.0369, radius=2.0, page_size=5
    )
    if coord_properties:
        print(f"Found {len(coord_properties)} properties within 2 miles")
    else:
        print("No properties found")
    
    # Example 4: Filtered search
    print("\n4. Filtered search (3+ bedrooms, built after 2000)...")
    filtered_properties = client.search_properties_with_filters(
        zip_code="22030",
        min_beds=3,
        min_year=2000,
        property_type="sfr",
        page_size=5
    )
    if filtered_properties:
        print(f"Found {len(filtered_properties)} filtered properties")
        for prop in filtered_properties[:2]:
            print(f"  - {prop.address}: {prop.bedrooms} beds, built {prop.build_year}")
    else:
        print("No filtered properties found")
    
    # Example 5: Export to CSV and JSON
    if properties:
        print("\n5. Exporting data...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"sample_properties_{timestamp}.csv"
        json_filename = f"sample_properties_{timestamp}.json"
        
        exporter.export_to_csv(properties, csv_filename)
        exporter.export_to_json(properties, json_filename)
        
        # Generate summary report
        summary = exporter.generate_summary_report(properties)
        print(f"Summary: {summary.get('total_properties', 0)} properties")
        if summary.get('bedrooms'):
            print(f"Bedrooms: {summary['bedrooms']['min']}-{summary['bedrooms']['max']} (avg: {summary['bedrooms']['avg']})")
        if summary.get('build_years'):
            print(f"Build years: {summary['build_years']['min']}-{summary['build_years']['max']}")
    
    print("\nDemo completed!")


if __name__ == "__main__":
    main()