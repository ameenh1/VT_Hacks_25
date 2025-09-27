"""
ATTOM Housing Data Bridge API
============================

This FastAPI service acts as a bridge between your assistant and the ATTOM Data API,
providing clean, structured endpoints for property data retrieval and sell value estimation.

Features:
- RESTful API endpoints for property search and valuation
- Structured responses optimized for AI assistants
- Built-in error handling and rate limiting
- Swagger UI documentation
- Health monitoring endpoints

Author: VT Hacks 25 Team
"""

from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import logging
import uvicorn
from enum import Enum

# Import our ATTOM client
from attom_housing_data import AttomDataClient, PropertyData, PropertyDataExporter, HousingDataAnalyzer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ATTOM Housing Data Bridge API",
    description="Bridge API for accessing ATTOM property data and generating sell value estimates",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for web applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global client instance (you can move this to dependency injection later)
ATTOM_API_KEY = "f531d94bd739ea66392d8f987b95b20e"
attom_client = AttomDataClient(ATTOM_API_KEY)
analyzer = HousingDataAnalyzer(attom_client)

# Pydantic models for requests and responses
class PropertyTypeEnum(str, Enum):
    SFR = "sfr"
    CONDO = "condo" 
    APARTMENT = "apartment"
    TOWNHOUSE = "townhouse"
    MFR = "mfr"

class PropertySearchRequest(BaseModel):
    zip_code: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius: Optional[float] = Field(default=1.0, ge=0.1, le=20.0)
    property_type: Optional[PropertyTypeEnum] = None
    min_beds: Optional[int] = Field(default=None, ge=0)
    max_beds: Optional[int] = Field(default=None, ge=0)
    min_baths: Optional[float] = Field(default=None, ge=0)
    max_baths: Optional[float] = Field(default=None, ge=0)
    min_price: Optional[float] = Field(default=None, ge=0)
    max_price: Optional[float] = Field(default=None, ge=0)
    min_year: Optional[int] = Field(default=None, ge=1800)
    max_year: Optional[int] = Field(default=None, le=2030)
    page_size: Optional[int] = Field(default=10, ge=1, le=100)

class PropertyResponse(BaseModel):
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
    property_type: Optional[str]
    square_footage: Optional[int]
    lot_size: Optional[float]
    listing_price: Optional[float]
    last_sale_price: Optional[float]
    last_sale_date: Optional[str]
    assessed_value: Optional[float]
    avm_value: Optional[float]

class PropertySearchResponse(BaseModel):
    success: bool
    count: int
    properties: List[PropertyResponse]
    query_time: str

class ValuationData(BaseModel):
    property_id: str
    address: str
    current_avm_value: Optional[float]
    assessed_value: Optional[float]
    last_sale_price: Optional[float]
    last_sale_date: Optional[str]
    price_per_sqft: Optional[float]
    estimated_sell_value: Optional[float]
    confidence_score: Optional[float]
    market_factors: Dict[str, Any]

class ValuationResponse(BaseModel):
    success: bool
    property_found: bool
    valuation_data: Optional[ValuationData]
    comparable_properties: List[PropertyResponse]
    market_summary: Dict[str, Any]

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    api_connection: bool

# Convert PropertyData to PropertyResponse
def property_data_to_response(prop: PropertyData) -> PropertyResponse:
    return PropertyResponse(
        property_id=prop.property_id,
        address=prop.address,
        city=prop.city,
        state=prop.state,
        zip_code=prop.zip_code,
        latitude=prop.latitude,
        longitude=prop.longitude,
        bedrooms=prop.bedrooms,
        bathrooms=prop.bathrooms,
        build_year=prop.build_year,
        property_type=prop.property_type,
        square_footage=prop.square_footage,
        lot_size=prop.lot_size,
        listing_price=prop.listing_price,
        last_sale_price=prop.last_sale_price,
        last_sale_date=prop.last_sale_date,
        assessed_value=prop.assessed_value,
        avm_value=prop.avm_value
    )

# API Endpoints

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information"""
    return {
        "service": "ATTOM Housing Data Bridge API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint to verify API connectivity"""
    try:
        # Test ATTOM API connection by making a simple request
        test_props = attom_client.search_properties_by_zip("10001", page_size=1)
        api_connection = True
    except Exception as e:
        logger.error(f"ATTOM API connection test failed: {e}")
        api_connection = False
    
    return HealthResponse(
        status="healthy" if api_connection else "degraded",
        timestamp=datetime.now().isoformat(),
        api_connection=api_connection
    )

@app.get("/properties/search", response_model=PropertySearchResponse)
async def search_properties(
    zip_code: Optional[str] = Query(None, description="ZIP code to search"),
    address: Optional[str] = Query(None, description="Street address"),
    city: Optional[str] = Query(None, description="City name"),
    state: Optional[str] = Query(None, description="State abbreviation"),
    latitude: Optional[float] = Query(None, description="Latitude for coordinate search"),
    longitude: Optional[float] = Query(None, description="Longitude for coordinate search"),
    radius: float = Query(1.0, ge=0.1, le=20.0, description="Search radius in miles"),
    property_type: Optional[PropertyTypeEnum] = Query(None, description="Property type filter"),
    min_beds: Optional[int] = Query(None, ge=0, description="Minimum bedrooms"),
    max_beds: Optional[int] = Query(None, ge=0, description="Maximum bedrooms"),
    min_baths: Optional[float] = Query(None, ge=0, description="Minimum bathrooms"),
    max_baths: Optional[float] = Query(None, ge=0, description="Maximum bathrooms"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    min_year: Optional[int] = Query(None, ge=1800, description="Minimum build year"),
    max_year: Optional[int] = Query(None, le=2030, description="Maximum build year"),
    page_size: int = Query(10, ge=1, le=100, description="Number of results")
):
    """
    Search for properties using various criteria.
    
    You can search by:
    - ZIP code only
    - Full address (address + city + state)
    - Coordinates (latitude + longitude + radius)
    - With additional filters for bedrooms, bathrooms, price, etc.
    """
    start_time = datetime.now()
    
    try:
        properties = []
        
        # Coordinate-based search
        if latitude is not None and longitude is not None:
            logger.info(f"Searching by coordinates: {latitude}, {longitude}")
            properties = attom_client.search_properties_by_coordinates(
                latitude=latitude,
                longitude=longitude,
                radius=radius,
                page_size=page_size
            )
        
        # Address-based search
        elif address and city and state:
            logger.info(f"Searching by address: {address}, {city}, {state}")
            prop = attom_client.search_property_by_address(address, city, state, zip_code)
            if prop:
                properties = [prop]
        
        # ZIP code search with optional filters
        elif zip_code:
            logger.info(f"Searching by ZIP code: {zip_code}")
            if any([min_beds, max_beds, min_baths, max_baths, min_price, max_price, min_year, max_year, property_type]):
                # Use filtered search
                properties = attom_client.search_properties_with_filters(
                    zip_code=zip_code,
                    min_beds=min_beds,
                    max_beds=max_beds,
                    min_baths=min_baths,
                    max_baths=max_baths,
                    min_price=min_price,
                    max_price=max_price,
                    min_year=min_year,
                    max_year=max_year,
                    property_type=property_type.value if property_type else None,
                    page_size=page_size
                )
            else:
                # Basic ZIP search
                properties = attom_client.search_properties_by_zip(
                    zip_code=zip_code,
                    page_size=page_size,
                    property_type=property_type.value if property_type else None
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="Must provide either zip_code, full address (address+city+state), or coordinates (latitude+longitude)"
            )
        
        # Convert to response format
        property_responses = [property_data_to_response(prop) for prop in properties]
        
        return PropertySearchResponse(
            success=True,
            count=len(property_responses),
            properties=property_responses,
            query_time=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error searching properties: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/properties/{property_id}/details", response_model=Dict[str, Any])
async def get_property_details(
    property_id: str = Path(..., description="ATTOM property ID")
):
    """Get detailed information for a specific property including sales history and assessments"""
    try:
        # Get basic property data first - we'll need to search for it
        # Note: In a production system, you might want to store property IDs for direct lookup
        
        # Get sales history
        sales_history = attom_client.get_property_sales_history(property_id)
        
        # Get assessment data
        assessment_data = attom_client.get_property_assessment_data(property_id)
        
        # Get AVM data
        avm_data = attom_client.get_property_avm_value(property_id)
        
        return {
            "success": True,
            "property_id": property_id,
            "sales_history": sales_history,
            "assessment_data": assessment_data,
            "avm_data": avm_data,
            "retrieved_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting property details for {property_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get property details: {str(e)}")

@app.post("/properties/valuation", response_model=ValuationResponse)
async def get_property_valuation(request: PropertySearchRequest):
    """
    Get comprehensive valuation data for a property including estimated sell value.
    
    This endpoint is optimized for sell value estimation by providing:
    - Current property values (AVM, assessed, last sale)
    - Comparable properties in the area
    - Market analysis and trends
    - Estimated sell value with confidence score
    """
    try:
        # First, find the target property
        target_property = None
        
        if request.address and request.city and request.state:
            target_property = attom_client.search_property_by_address(
                request.address, request.city, request.state, request.zip_code
            )
        elif request.zip_code:
            # If only ZIP provided, get one property as example
            properties = attom_client.search_properties_by_zip(request.zip_code, page_size=1)
            if properties:
                target_property = properties[0]
        
        if not target_property:
            return ValuationResponse(
                success=True,
                property_found=False,
                valuation_data=None,
                comparable_properties=[],
                market_summary={}
            )
        
        # Find comparable properties
        comparable_properties = []
        if target_property.latitude and target_property.longitude:
            comparable_properties = analyzer.find_similar_properties(
                target_property, search_radius=2.0
            )
        
        # Calculate price per square foot
        price_per_sqft = None
        if target_property.square_footage and target_property.last_sale_price:
            price_per_sqft = target_property.last_sale_price / target_property.square_footage
        
        # Estimate sell value (simple algorithm - you can enhance this)
        estimated_sell_value = None
        confidence_score = None
        
        values = []
        if target_property.avm_value:
            values.append(target_property.avm_value)
        if target_property.assessed_value:
            values.append(target_property.assessed_value)
        if target_property.last_sale_price:
            values.append(target_property.last_sale_price)
        
        if values:
            estimated_sell_value = sum(values) / len(values)
            confidence_score = min(len(values) * 0.3, 1.0)  # Simple confidence based on data availability
        
        # Market factors analysis
        market_factors = {
            "comparable_count": len(comparable_properties),
            "avg_price_per_sqft": None,
            "price_range": {"min": None, "max": None},
            "avg_build_year": None
        }
        
        if comparable_properties:
            prices = [p.last_sale_price for p in comparable_properties if p.last_sale_price]
            sqft_prices = [p.last_sale_price / p.square_footage 
                          for p in comparable_properties 
                          if p.last_sale_price and p.square_footage]
            years = [p.build_year for p in comparable_properties if p.build_year]
            
            if prices:
                market_factors["price_range"] = {"min": min(prices), "max": max(prices)}
            if sqft_prices:
                market_factors["avg_price_per_sqft"] = sum(sqft_prices) / len(sqft_prices)
            if years:
                market_factors["avg_build_year"] = sum(years) / len(years)
        
        # Market summary for the area
        if request.zip_code:
            market_analysis = analyzer.analyze_neighborhood(request.zip_code)
            market_summary = market_analysis.get('summary', {})
        else:
            market_summary = {}
        
        valuation_data = ValuationData(
            property_id=target_property.property_id,
            address=target_property.address,
            current_avm_value=target_property.avm_value,
            assessed_value=target_property.assessed_value,
            last_sale_price=target_property.last_sale_price,
            last_sale_date=target_property.last_sale_date,
            price_per_sqft=price_per_sqft,
            estimated_sell_value=estimated_sell_value,
            confidence_score=confidence_score,
            market_factors=market_factors
        )
        
        comparable_responses = [property_data_to_response(prop) for prop in comparable_properties]
        
        return ValuationResponse(
            success=True,
            property_found=True,
            valuation_data=valuation_data,
            comparable_properties=comparable_responses,
            market_summary=market_summary
        )
        
    except Exception as e:
        logger.error(f"Error getting property valuation: {e}")
        raise HTTPException(status_code=500, detail=f"Valuation failed: {str(e)}")

@app.get("/neighborhoods/{zip_code}/analysis", response_model=Dict[str, Any])
async def analyze_neighborhood(
    zip_code: str = Path(..., description="ZIP code to analyze"),
    include_properties: bool = Query(False, description="Include full property list in response")
):
    """
    Get comprehensive neighborhood analysis for a ZIP code.
    
    Provides market trends, property statistics, and overview data
    useful for understanding the local housing market.
    """
    try:
        analysis = analyzer.analyze_neighborhood(zip_code)
        
        response = {
            "success": True,
            "zip_code": zip_code,
            "summary": analysis.get('summary', {}),
            "analysis_timestamp": analysis.get('analysis_timestamp'),
            "property_count": len(analysis.get('properties', []))
        }
        
        if include_properties:
            properties = analysis.get('properties', [])
            response["properties"] = [property_data_to_response(prop) for prop in properties]
        
        return response
        
    except Exception as e:
        logger.error(f"Error analyzing neighborhood {zip_code}: {e}")
        raise HTTPException(status_code=500, detail=f"Neighborhood analysis failed: {str(e)}")

@app.post("/properties/compare", response_model=Dict[str, Any])
async def compare_properties(addresses: List[Dict[str, str]]):
    """
    Compare multiple properties side by side.
    
    Request body should contain a list of address objects:
    [
        {"address": "123 Main St", "city": "Arlington", "state": "VA", "zip_code": "22030"},
        {"address": "456 Oak Ave", "city": "Arlington", "state": "VA", "zip_code": "22030"}
    ]
    """
    try:
        if len(addresses) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 properties can be compared at once")
        
        comparison = analyzer.compare_properties(addresses)
        
        # Convert properties to response format
        properties_response = []
        for prop in comparison.get('properties', []):
            properties_response.append(property_data_to_response(prop))
        
        return {
            "success": True,
            "comparison_timestamp": comparison.get('comparison_timestamp'),
            "properties_found": comparison.get('properties_found', 0),
            "properties_requested": comparison.get('properties_requested', 0),
            "properties": properties_response,
            "comparison_table": comparison.get('comparison_table', [])
        }
        
    except Exception as e:
        logger.error(f"Error comparing properties: {e}")
        raise HTTPException(status_code=500, detail=f"Property comparison failed: {str(e)}")

@app.get("/market/trends/{zip_code}", response_model=Dict[str, Any])
async def get_market_trends(
    zip_code: str = Path(..., description="ZIP code for market trends"),
    property_type: Optional[PropertyTypeEnum] = Query(None, description="Filter by property type")
):
    """
    Get market trends and statistics for a specific ZIP code.
    
    Provides insights into pricing trends, property characteristics,
    and market conditions useful for sell value estimation.
    """
    try:
        # Get properties in the area
        properties = attom_client.search_properties_by_zip(
            zip_code=zip_code,
            page_size=100,
            property_type=property_type.value if property_type else None
        )
        
        if not properties:
            return {
                "success": True,
                "zip_code": zip_code,
                "property_type": property_type.value if property_type else "all",
                "trends": {},
                "message": "No properties found for trend analysis"
            }
        
        # Generate summary statistics
        summary = PropertyDataExporter.generate_summary_report(properties)
        
        # Calculate additional trend metrics
        current_year = datetime.now().year
        recent_sales = [p for p in properties if p.last_sale_date and 
                       p.last_sale_date.startswith(str(current_year - 1)) or 
                       p.last_sale_date.startswith(str(current_year))]
        
        price_per_sqft_data = []
        for prop in properties:
            if prop.square_footage and prop.last_sale_price:
                price_per_sqft_data.append(prop.last_sale_price / prop.square_footage)
        
        trends = {
            "total_properties": len(properties),
            "recent_sales_count": len(recent_sales),
            "property_types": summary.get('property_types', {}),
            "price_statistics": summary.get('prices', {}),
            "size_statistics": summary.get('square_footage', {}),
            "age_statistics": summary.get('build_years', {}),
            "bedroom_distribution": summary.get('bedrooms', {}),
            "bathroom_distribution": summary.get('bathrooms', {}),
            "price_per_sqft": {
                "min": min(price_per_sqft_data) if price_per_sqft_data else None,
                "max": max(price_per_sqft_data) if price_per_sqft_data else None,
                "avg": sum(price_per_sqft_data) / len(price_per_sqft_data) if price_per_sqft_data else None
            }
        }
        
        return {
            "success": True,
            "zip_code": zip_code,
            "property_type": property_type.value if property_type else "all",
            "analysis_date": datetime.now().isoformat(),
            "trends": trends
        }
        
    except Exception as e:
        logger.error(f"Error getting market trends for {zip_code}: {e}")
        raise HTTPException(status_code=500, detail=f"Market trends analysis failed: {str(e)}")

@app.get("/properties/estimate-value", response_model=Dict[str, Any])
async def estimate_property_value(
    address: str = Query(..., description="Property address"),
    city: str = Query(..., description="City name"),
    state: str = Query(..., description="State abbreviation"),
    zip_code: Optional[str] = Query(None, description="ZIP code"),
    bedrooms: Optional[int] = Query(None, description="Number of bedrooms (for better estimation)"),
    bathrooms: Optional[float] = Query(None, description="Number of bathrooms (for better estimation)"),
    square_footage: Optional[int] = Query(None, description="Square footage (for better estimation)"),
    build_year: Optional[int] = Query(None, description="Build year (for better estimation)")
):
    """
    Quick property value estimation endpoint.
    
    This endpoint provides a fast sell value estimate for a property
    using available data and comparable properties.
    """
    try:
        # Find the property
        property_data = attom_client.search_property_by_address(address, city, state, zip_code)
        
        if not property_data:
            # If property not found in ATTOM, create a basic estimate using provided data
            if not (bedrooms and bathrooms and square_footage and zip_code):
                raise HTTPException(
                    status_code=404, 
                    detail="Property not found in ATTOM database. Please provide bedrooms, bathrooms, square_footage, and zip_code for estimation."
                )
            
            # Get market data for the ZIP code
            market_props = attom_client.search_properties_by_zip(zip_code, page_size=50)
            if not market_props:
                raise HTTPException(status_code=404, detail="No market data available for this area")
            
            # Calculate estimated value based on comparable properties
            comparable_prices = []
            for prop in market_props:
                if (prop.bedrooms and abs(prop.bedrooms - bedrooms) <= 1 and
                    prop.bathrooms and abs(prop.bathrooms - bathrooms) <= 1 and
                    prop.square_footage and prop.last_sale_price):
                    
                    price_per_sqft = prop.last_sale_price / prop.square_footage
                    estimated_value = price_per_sqft * square_footage
                    comparable_prices.append(estimated_value)
            
            if comparable_prices:
                estimated_value = sum(comparable_prices) / len(comparable_prices)
                confidence = min(len(comparable_prices) * 0.1, 0.7)  # Lower confidence for estimated properties
            else:
                # Fallback to average market price per sqft
                all_prices_per_sqft = []
                for prop in market_props:
                    if prop.square_footage and prop.last_sale_price:
                        all_prices_per_sqft.append(prop.last_sale_price / prop.square_footage)
                
                if all_prices_per_sqft:
                    avg_price_per_sqft = sum(all_prices_per_sqft) / len(all_prices_per_sqft)
                    estimated_value = avg_price_per_sqft * square_footage
                    confidence = 0.3  # Low confidence for general market estimate
                else:
                    raise HTTPException(status_code=404, detail="Insufficient market data for estimation")
            
            return {
                "success": True,
                "property_found_in_attom": False,
                "address": f"{address}, {city}, {state}",
                "estimated_value": round(estimated_value, 2),
                "confidence_score": round(confidence, 2),
                "estimation_method": "comparable_properties_analysis",
                "comparables_used": len(comparable_prices) if comparable_prices else len(all_prices_per_sqft),
                "estimated_at": datetime.now().isoformat()
            }
        
        else:
            # Property found in ATTOM - use comprehensive data
            values = []
            value_sources = []
            
            if property_data.avm_value:
                values.append(property_data.avm_value)
                value_sources.append("AVM")
            
            if property_data.assessed_value:
                values.append(property_data.assessed_value)
                value_sources.append("Assessed")
            
            if property_data.last_sale_price:
                values.append(property_data.last_sale_price)
                value_sources.append("Last Sale")
            
            if values:
                estimated_value = sum(values) / len(values)
                confidence = min(len(values) * 0.25, 0.9)  # Higher confidence with ATTOM data
            else:
                raise HTTPException(status_code=404, detail="No valuation data available for this property")
            
            return {
                "success": True,
                "property_found_in_attom": True,
                "property_id": property_data.property_id,
                "address": property_data.address,
                "estimated_value": round(estimated_value, 2),
                "confidence_score": round(confidence, 2),
                "value_sources": value_sources,
                "individual_values": {
                    "avm_value": property_data.avm_value,
                    "assessed_value": property_data.assessed_value,
                    "last_sale_price": property_data.last_sale_price
                },
                "property_details": {
                    "bedrooms": property_data.bedrooms,
                    "bathrooms": property_data.bathrooms,
                    "square_footage": property_data.square_footage,
                    "build_year": property_data.build_year,
                    "last_sale_date": property_data.last_sale_date
                },
                "estimated_at": datetime.now().isoformat()
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error estimating property value: {e}")
        raise HTTPException(status_code=500, detail=f"Value estimation failed: {str(e)}")

# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "attom_bridge_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )