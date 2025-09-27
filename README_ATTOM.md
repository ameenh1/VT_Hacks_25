# ATTOM Housing Data API Client

A comprehensive Python client for accessing house data from the ATTOM Data API. This script provides easy-to-use methods for pulling detailed property information including location, specifications, bedrooms, bathrooms, build year, and listing prices.

## Features

- **Property Search**: Search by ZIP code, address, or geographic coordinates
- **Detailed Data**: Extract comprehensive property information including:
  - Location (address, city, state, ZIP, coordinates)
  - Property specifications (bedrooms, bathrooms, square footage)
  - Build year and property type
  - Listing prices and sale history
  - Assessment and AVM values
- **Advanced Filtering**: Filter properties by bedrooms, bathrooms, build year, price range
- **Data Export**: Export results to CSV and JSON formats
- **Analysis Tools**: Compare properties and generate summary reports
- **Robust Error Handling**: Built-in logging and error management

## Prerequisites

1. **ATTOM Data API Key**: Sign up at [ATTOM Developer Platform](https://api.developer.attomdata.com/signup)
2. **Python 3.7+** with the following packages:
   ```bash
   pip install requests
   ```

## Quick Start

```python
from attom_housing_data import AttomDataClient, HousingDataAnalyzer

# Initialize client with your API key
API_KEY = "your_api_key_here"
client = AttomDataClient(API_KEY)

# Search properties by ZIP code
properties = client.search_properties_by_zip("22030", page_size=10)
for prop in properties:
    print(f"{prop.address}: {prop.bedrooms} beds, {prop.bathrooms} baths, built {prop.build_year}")
```

## API Classes

### AttomDataClient

Main client class for interacting with the ATTOM Data API.

#### Methods:

- `search_properties_by_zip(zip_code, page_size=50, property_type=None)` - Search properties in a ZIP code
- `search_property_by_address(address, city, state, zip_code=None)` - Find specific property by address
- `search_properties_by_coordinates(latitude, longitude, radius=1.0, page_size=50)` - Search within radius
- `search_properties_with_filters(...)` - Advanced filtered search
- `get_property_sales_history(property_id)` - Get sales history for a property
- `get_property_assessment_data(property_id)` - Get assessment information
- `get_property_avm_value(property_id)` - Get automated valuation model data

### PropertyData

Data class that stores structured property information:

```python
@dataclass
class PropertyData:
    property_id: str
    address: str
    city: str
    state: str
    zip_code: str
    latitude: Optional[float]
    longitude: Optional[float]
    bedrooms: Optional[int]
    bathrooms: Optional[float]
    build_year: Optional[int]
    listing_price: Optional[float]
    property_type: Optional[str]
    square_footage: Optional[int]
    lot_size: Optional[float]
    last_sale_price: Optional[float]
    last_sale_date: Optional[str]
    assessed_value: Optional[float]
    avm_value: Optional[float]
```

### PropertyDataExporter

Utility class for exporting property data:

- `export_to_csv(properties, filename)` - Export to CSV format
- `export_to_json(properties, filename)` - Export to JSON format
- `generate_summary_report(properties)` - Generate statistics summary

### HousingDataAnalyzer

Advanced analysis tools:

- `analyze_neighborhood(zip_code)` - Complete neighborhood analysis
- `compare_properties(property_addresses)` - Side-by-side property comparison
- `find_similar_properties(reference_property)` - Find similar properties

## Usage Examples

### 1. Basic Property Search

```python
# Search by ZIP code
properties = client.search_properties_by_zip("10001", page_size=20)
print(f"Found {len(properties)} properties")

# Search specific address
property = client.search_property_by_address(
    address="123 Main Street",
    city="New York",
    state="NY",
    zip_code="10001"
)
if property:
    print(f"Property: {property.address}")
    print(f"Bedrooms: {property.bedrooms}, Bathrooms: {property.bathrooms}")
    print(f"Built: {property.build_year}, Price: ${property.last_sale_price}")
```

### 2. Geographic Search

```python
# Search near coordinates (Manhattan)
properties = client.search_properties_by_coordinates(
    latitude=40.7589, 
    longitude=-73.9851, 
    radius=0.5,  # 0.5 miles
    page_size=25
)
```

### 3. Advanced Filtering

```python
# Find luxury properties
luxury_properties = client.search_properties_with_filters(
    zip_code="90210",
    min_beds=4,
    min_baths=3,
    min_price=1000000,
    min_year=2010,
    property_type="sfr",  # Single Family Residence
    page_size=50
)
```

### 4. Data Export

```python
from attom_housing_data import PropertyDataExporter

# Get properties
properties = client.search_properties_by_zip("22030", page_size=100)

# Export to CSV
PropertyDataExporter.export_to_csv(properties, "properties.csv")

# Export to JSON
PropertyDataExporter.export_to_json(properties, "properties.json")

# Generate summary report
summary = PropertyDataExporter.generate_summary_report(properties)
print(f"Average bedrooms: {summary['bedrooms']['avg']}")
print(f"Price range: ${summary['prices']['min']} - ${summary['prices']['max']}")
```

### 5. Neighborhood Analysis

```python
from attom_housing_data import HousingDataAnalyzer

analyzer = HousingDataAnalyzer(client)

# Analyze entire neighborhood
results = analyzer.analyze_neighborhood("22030", export_csv=True, export_json=True)
print(f"Analyzed {results['summary']['total_properties']} properties")
print(f"Property types: {results['summary']['property_types']}")
```

### 6. Property Comparison

```python
# Compare multiple properties
addresses = [
    {"address": "123 Oak Street", "city": "Arlington", "state": "VA", "zip_code": "22030"},
    {"address": "456 Pine Avenue", "city": "Arlington", "state": "VA", "zip_code": "22030"},
    {"address": "789 Elm Drive", "city": "Arlington", "state": "VA", "zip_code": "22030"}
]

comparison = analyzer.compare_properties(addresses)
print(f"Compared {comparison['properties_found']} properties")
for i, prop in enumerate(comparison['comparison_table'], 1):
    print(f"Property {i}: {prop['bedrooms']} beds, ${prop['last_sale_price']}")
```

### 7. Find Similar Properties

```python
# Find properties similar to a reference property
reference = client.search_property_by_address("123 Main St", "Arlington", "VA")
if reference:
    similar = analyzer.find_similar_properties(reference, search_radius=2.0)
    print(f"Found {len(similar)} similar properties")
```

## Property Types

Common property type codes for filtering:
- `sfr` - Single Family Residence
- `condo` - Condominium
- `apartment` - Apartment
- `townhouse` - Townhouse
- `mfr` - Multi-Family Residence

## API Rate Limits

The ATTOM Data API has rate limits and monthly quotas. The script includes:
- Error handling for rate limit responses
- Logging for API usage monitoring
- Configurable page sizes (max 100 per request)

## Error Handling

The script includes comprehensive error handling:
- Network connection errors
- API authentication errors
- Data parsing errors
- Invalid parameter validation

All errors are logged using Python's logging module.

## File Structure

```
attom_housing_data.py          # Main script with all classes
README.md                      # This documentation
properties_ZIPCODE_TIMESTAMP.csv   # Example CSV export
properties_ZIPCODE_TIMESTAMP.json  # Example JSON export
```

## Running the Demo

The script includes a demonstration function:

```bash
python attom_housing_data.py
```

This will run examples of all major features and create sample export files.

## License

This project is for educational and development purposes. Please review ATTOM Data's terms of service for commercial usage.

## Support

For API documentation and support:
- [ATTOM Developer Documentation](https://api.developer.attomdata.com/docs)
- [ATTOM Data Contact](mailto:datacustomercare@attomdata.com)

## Contributing

Feel free to submit issues and enhancement requests!