# ATTOM Housing Data Bridge API

A FastAPI-based bridge service that provides clean, structured endpoints for accessing ATTOM property data and generating sell value estimates. Perfect for integration with AI assistants and other systems.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Bridge API
```bash
python attom_bridge_api.py
```

The API will be available at: `http://localhost:8000`

### 3. Test the API
```bash
# Run comprehensive tests
python test_attom_bridge_api.py

# Run quick tests only
python test_attom_bridge_api.py --quick
```

### 4. View API Documentation
Open your browser and go to: `http://localhost:8000/docs`

## 📋 API Endpoints

### Core Endpoints

- **`GET /`** - API information and status
- **`GET /health`** - Health check and ATTOM API connectivity status
- **`GET /docs`** - Interactive Swagger UI documentation

### Property Search

- **`GET /properties/search`** - Search properties by ZIP, address, or coordinates
- **`GET /properties/{property_id}/details`** - Get detailed property information
- **`POST /properties/compare`** - Compare multiple properties side-by-side

### Valuation & Estimation (Key for Sell Value Estimates)

- **`POST /properties/valuation`** - Comprehensive property valuation with comparables
- **`GET /properties/estimate-value`** - Quick property value estimation
- **`GET /market/trends/{zip_code}`** - Market trends and statistics

### Market Analysis

- **`GET /neighborhoods/{zip_code}/analysis`** - Neighborhood analysis and statistics

## 🏠 Usage Examples for AI Assistants

### Quick Property Value Estimate
```python
import requests

# Estimate property value
response = requests.get("http://localhost:8000/properties/estimate-value", params={
    "address": "123 Main Street",
    "city": "Arlington", 
    "state": "VA",
    "zip_code": "22030"
})

data = response.json()
if data["success"]:
    print(f"Estimated Value: ${data['estimated_value']:,.2f}")
    print(f"Confidence: {data['confidence_score']:.2f}")
```

### Search Properties for Comparison
```python
# Search properties in an area
response = requests.get("http://localhost:8000/properties/search", params={
    "zip_code": "22030",
    "min_beds": 3,
    "property_type": "sfr",
    "page_size": 10
})

properties = response.json()["properties"]
for prop in properties:
    print(f"{prop['address']}: ${prop['last_sale_price']:,.2f}")
```

### Get Market Trends for Context
```python
# Get market trends for valuation context
response = requests.get("http://localhost:8000/market/trends/22030")
trends = response.json()["trends"]

print(f"Average price: ${trends['price_statistics']['avg']:,.2f}")
print(f"Price per sqft: ${trends['price_per_sqft']['avg']:.2f}")
```

## 🤖 AI Assistant Integration

This bridge API is designed for seamless integration with AI assistants. Here's how to use it:

### 1. Property Valuation Assistant

```python
def get_property_value_estimate(address, city, state, zip_code=None):
    """Get property value estimate for AI assistant"""
    
    # Quick estimate endpoint
    response = requests.get("http://localhost:8000/properties/estimate-value", params={
        "address": address,
        "city": city,
        "state": state,
        "zip_code": zip_code
    })
    
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            return {
                "estimated_value": data["estimated_value"],
                "confidence": data["confidence_score"],
                "data_sources": data.get("value_sources", []),
                "property_details": data.get("property_details", {})
            }
    
    return {"error": "Could not estimate value"}

# Usage in AI assistant
estimate = get_property_value_estimate("123 Oak St", "Arlington", "VA")
print(f"The estimated sell value is ${estimate['estimated_value']:,.2f} with {estimate['confidence']:.0%} confidence")
```

### 2. Market Analysis Assistant

```python
def analyze_market_for_selling(zip_code):
    """Analyze market conditions for selling decisions"""
    
    # Get market trends
    trends_response = requests.get(f"http://localhost:8000/market/trends/{zip_code}")
    
    # Get neighborhood analysis  
    neighborhood_response = requests.get(f"http://localhost:8000/neighborhoods/{zip_code}/analysis")
    
    if trends_response.status_code == 200 and neighborhood_response.status_code == 200:
        trends = trends_response.json()["trends"]
        neighborhood = neighborhood_response.json()
        
        return {
            "market_summary": {
                "total_properties": trends["total_properties"],
                "avg_price": trends["price_statistics"]["avg"],
                "price_range": f"${trends['price_statistics']['min']:,.0f} - ${trends['price_statistics']['max']:,.0f}",
                "avg_price_per_sqft": trends["price_per_sqft"]["avg"]
            },
            "selling_insights": {
                "property_types": trends["property_types"],
                "recent_sales": trends["recent_sales_count"]
            }
        }
    
    return {"error": "Could not analyze market"}

# Usage in AI assistant  
market_info = analyze_market_for_selling("22030")
print(f"Market has {market_info['market_summary']['total_properties']} properties")
print(f"Average price: {market_info['market_summary']['avg_price']}")
```

## 🔧 Configuration

### Environment Variables

You can configure the API using environment variables:

```bash
# Set ATTOM API key
export ATTOM_API_KEY="your_actual_api_key_here"

# Set API host and port
export API_HOST="0.0.0.0"
export API_PORT="8000"
```

### Custom Configuration

Edit `attom_bridge_api.py` to customize:

```python
# Change API key
ATTOM_API_KEY = "your_api_key_here"

# Modify CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Restrict origins
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## 📊 Response Formats

All endpoints return consistent JSON responses:

### Success Response
```json
{
    "success": true,
    "data": { ... },
    "timestamp": "2025-09-26T10:30:00"
}
```

### Error Response
```json
{
    "detail": "Error description",
    "status_code": 400
}
```

### Property Data Structure
```json
{
    "property_id": "123456789",
    "address": "123 Main Street",
    "city": "Arlington",
    "state": "VA",
    "zip_code": "22030",
    "latitude": 38.8816,
    "longitude": -77.0910,
    "bedrooms": 3,
    "bathrooms": 2.5,
    "build_year": 2010,
    "property_type": "sfr",
    "square_footage": 2500,
    "lot_size": 0.25,
    "listing_price": null,
    "last_sale_price": 650000,
    "last_sale_date": "2023-05-15",
    "assessed_value": 625000,
    "avm_value": 675000
}
```

## 🧪 Testing

The test script validates all endpoints and provides detailed results:

```bash
# Full test suite
python test_attom_bridge_api.py

# Quick essential tests
python test_attom_bridge_api.py --quick

# Test against different URL
python test_attom_bridge_api.py --url http://your-server:8000
```

## 🚨 Error Handling

The API includes comprehensive error handling:

- **400**: Bad Request (invalid parameters)
- **404**: Not Found (property not found)
- **422**: Validation Error (invalid input format)
- **500**: Internal Server Error (ATTOM API issues)

All errors include descriptive messages for debugging.

## 📈 Performance

- Response times typically under 2 seconds
- Built-in request/response logging
- Efficient data caching opportunities
- Rate limiting respect for ATTOM API

## 🔒 Security Considerations

- API key is server-side only
- CORS configured for security
- Input validation on all endpoints
- No sensitive data in responses

## 📞 Support

For issues with:
- **Bridge API**: Check logs and test script results
- **ATTOM API**: Review ATTOM Data documentation
- **Property Data**: Verify ATTOM API key and quotas

## 🛠 Development

To extend the bridge API:

1. Add new endpoints in `attom_bridge_api.py`
2. Update test script in `test_attom_bridge_api.py`
3. Add tests for new functionality
4. Update this documentation

The bridge API is designed to be easily extensible for additional property data features and AI assistant integrations.