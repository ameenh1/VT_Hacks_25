"""
Data Models for EquityNest Real Estate Platform
===============================================

Pydantic models for property data, analysis, and user preferences.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from datetime import datetime


class PropertyType(str, Enum):
    """Property type enumeration"""
    SINGLE_FAMILY = "single_family"
    MULTI_FAMILY = "multi_family"
    CONDO = "condo"
    TOWNHOUSE = "townhouse"
    DUPLEX = "duplex"
    APARTMENT_BUILDING = "apartment_building"
    COMMERCIAL = "commercial"
    LAND = "land"
    MOBILE_HOME = "mobile_home"


class InvestmentStrategy(str, Enum):
    """Investment strategy enumeration"""
    BUY_AND_HOLD = "buy_and_hold"
    FIX_AND_FLIP = "fix_and_flip"
    WHOLESALE = "wholesale"
    BRRRR = "brrrr"  # Buy, Rehab, Rent, Refinance, Repeat
    SHORT_TERM_RENTAL = "short_term_rental"
    COMMERCIAL = "commercial"
    LIVE_IN_FLIP = "live_in_flip"


class PropertyAnalysis(BaseModel):
    """Property analysis results"""
    property_id: str = Field(..., description="Unique property identifier")
    address: str = Field(..., description="Property address")
    estimated_value: Optional[float] = Field(None, description="Estimated current value")
    purchase_price: Optional[float] = Field(None, description="Recommended purchase price")
    rental_estimate: Optional[float] = Field(None, description="Monthly rental estimate")
    cap_rate: Optional[float] = Field(None, description="Capitalization rate")
    cash_on_cash_return: Optional[float] = Field(None, description="Cash-on-cash return percentage")
    total_return: Optional[float] = Field(None, description="Total return on investment")
    
    # Property details
    bedrooms: Optional[int] = Field(None, description="Number of bedrooms")
    bathrooms: Optional[float] = Field(None, description="Number of bathrooms")
    square_footage: Optional[int] = Field(None, description="Square footage")
    lot_size: Optional[float] = Field(None, description="Lot size in acres")
    year_built: Optional[int] = Field(None, description="Year built")
    property_type: Optional[PropertyType] = Field(None, description="Type of property")
    
    # Market analysis
    neighborhood_score: Optional[float] = Field(None, description="Neighborhood quality score (1-10)")
    market_trends: Optional[Dict[str, Any]] = Field(None, description="Local market trend data")
    comparable_sales: Optional[List[Dict[str, Any]]] = Field(None, description="Recent comparable sales")
    
    # Investment metrics
    repair_estimates: Optional[float] = Field(None, description="Estimated repair costs")
    holding_costs: Optional[float] = Field(None, description="Monthly holding costs")
    exit_strategy_value: Optional[float] = Field(None, description="Expected exit value")
    
    # Risk factors
    risk_score: Optional[float] = Field(None, description="Investment risk score (1-10)")
    risk_factors: Optional[List[str]] = Field(None, description="Identified risk factors")
    
    analysis_date: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")


class QuickAnalysisResponse(BaseModel):
    """Quick property analysis response"""
    success: bool = Field(..., description="Whether analysis was successful")
    property_found: bool = Field(..., description="Whether property was found in database")
    analysis: Optional[PropertyAnalysis] = Field(None, description="Property analysis results")
    message: Optional[str] = Field(None, description="Response message")
    suggestions: Optional[List[str]] = Field(None, description="Investment suggestions")


class ATTOMSearchCriteria(BaseModel):
    """Search criteria for ATTOM API queries"""
    
    # Location criteria
    city: Optional[str] = Field(None, description="City name")
    state: Optional[str] = Field(None, description="State abbreviation")
    zip_code: Optional[str] = Field(None, description="ZIP code")
    county: Optional[str] = Field(None, description="County name")
    radius: Optional[int] = Field(None, description="Search radius in miles")
    
    # Property criteria
    property_types: Optional[List[PropertyType]] = Field(None, description="Property types to include")
    min_beds: Optional[int] = Field(None, description="Minimum bedrooms")
    max_beds: Optional[int] = Field(None, description="Maximum bedrooms")
    min_baths: Optional[float] = Field(None, description="Minimum bathrooms")
    max_baths: Optional[float] = Field(None, description="Maximum bathrooms")
    min_sqft: Optional[int] = Field(None, description="Minimum square footage")
    max_sqft: Optional[int] = Field(None, description="Maximum square footage")
    min_lot_size: Optional[float] = Field(None, description="Minimum lot size")
    max_lot_size: Optional[float] = Field(None, description="Maximum lot size")
    min_year_built: Optional[int] = Field(None, description="Minimum year built")
    max_year_built: Optional[int] = Field(None, description="Maximum year built")
    
    # Financial criteria
    min_price: Optional[float] = Field(None, description="Minimum price")
    max_price: Optional[float] = Field(None, description="Maximum price")
    min_estimated_value: Optional[float] = Field(None, description="Minimum estimated value")
    max_estimated_value: Optional[float] = Field(None, description="Maximum estimated value")
    
    # Investment criteria
    investment_strategy: Optional[InvestmentStrategy] = Field(None, description="Preferred investment strategy")
    target_cap_rate: Optional[float] = Field(None, description="Target capitalization rate")
    target_cash_return: Optional[float] = Field(None, description="Target cash-on-cash return")
    max_repair_budget: Optional[float] = Field(None, description="Maximum repair budget")
    
    # Search parameters
    max_results: Optional[int] = Field(50, description="Maximum number of results")
    sort_by: Optional[str] = Field("relevance", description="Sort criteria")
    exclude_foreclosures: Optional[bool] = Field(False, description="Exclude foreclosure properties")
    exclude_short_sales: Optional[bool] = Field(False, description="Exclude short sale properties")


class PropertySearchResult(BaseModel):
    """Individual property search result"""
    property_id: str = Field(..., description="Unique property identifier")
    address: str = Field(..., description="Full property address")
    city: str = Field(..., description="City")
    state: str = Field(..., description="State")
    zip_code: str = Field(..., description="ZIP code")
    
    # Basic property info
    property_type: Optional[PropertyType] = Field(None, description="Property type")
    bedrooms: Optional[int] = Field(None, description="Number of bedrooms")
    bathrooms: Optional[float] = Field(None, description="Number of bathrooms")
    square_footage: Optional[int] = Field(None, description="Square footage")
    lot_size: Optional[float] = Field(None, description="Lot size")
    year_built: Optional[int] = Field(None, description="Year built")
    
    # Financial data
    list_price: Optional[float] = Field(None, description="Current list price")
    estimated_value: Optional[float] = Field(None, description="Estimated market value")
    last_sale_price: Optional[float] = Field(None, description="Last sale price")
    last_sale_date: Optional[datetime] = Field(None, description="Last sale date")
    
    # Investment metrics (if calculated)
    potential_rental: Optional[float] = Field(None, description="Estimated monthly rent")
    cap_rate: Optional[float] = Field(None, description="Estimated cap rate")
    cash_return: Optional[float] = Field(None, description="Estimated cash-on-cash return")
    
    # Additional data
    days_on_market: Optional[int] = Field(None, description="Days on market")
    price_per_sqft: Optional[float] = Field(None, description="Price per square foot")
    neighborhood_score: Optional[float] = Field(None, description="Neighborhood quality score")
    
    # Flags
    is_foreclosure: Optional[bool] = Field(False, description="Is foreclosure property")
    is_short_sale: Optional[bool] = Field(False, description="Is short sale")
    needs_repair: Optional[bool] = Field(False, description="Needs significant repair")


class PropertySearchResponse(BaseModel):
    """Property search response with results"""
    success: bool = Field(..., description="Whether search was successful")
    total_found: int = Field(..., description="Total properties found")
    results: List[PropertySearchResult] = Field(..., description="Search results")
    search_criteria: ATTOMSearchCriteria = Field(..., description="Original search criteria")
    message: Optional[str] = Field(None, description="Response message")
    suggestions: Optional[List[str]] = Field(None, description="Search suggestions")


class MarketAnalysis(BaseModel):
    """Market analysis for a specific area"""
    location: str = Field(..., description="Location analyzed")
    analysis_date: datetime = Field(default_factory=datetime.now, description="Analysis date")
    
    # Market metrics
    median_home_value: Optional[float] = Field(None, description="Median home value")
    price_per_sqft: Optional[float] = Field(None, description="Average price per square foot")
    inventory_levels: Optional[int] = Field(None, description="Number of active listings")
    days_on_market: Optional[float] = Field(None, description="Average days on market")
    
    # Trends
    price_trend_1year: Optional[float] = Field(None, description="Price change over 1 year (%)")
    price_trend_5year: Optional[float] = Field(None, description="Price change over 5 years (%)")
    sales_volume_trend: Optional[float] = Field(None, description="Sales volume change (%)")
    
    # Rental market
    median_rent: Optional[float] = Field(None, description="Median monthly rent")
    rent_to_price_ratio: Optional[float] = Field(None, description="Rent-to-price ratio")
    rental_yield: Optional[float] = Field(None, description="Gross rental yield (%)")
    
    # Investment metrics
    cap_rate_range: Optional[Dict[str, float]] = Field(None, description="Cap rate range (min/max)")
    cash_flow_potential: Optional[str] = Field(None, description="Cash flow potential assessment")
    appreciation_potential: Optional[str] = Field(None, description="Appreciation potential assessment")
    
    # Risk factors
    market_risk_score: Optional[float] = Field(None, description="Market risk score (1-10)")
    economic_indicators: Optional[Dict[str, Any]] = Field(None, description="Local economic data")


class UserProfile(BaseModel):
    """User profile and investment preferences"""
    user_id: str = Field(..., description="Unique user identifier")
    
    # Basic info
    name: Optional[str] = Field(None, description="User name")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    
    # Investment profile
    experience_level: Optional[str] = Field(None, description="Investment experience level")
    investment_budget: Optional[Dict[str, float]] = Field(None, description="Investment budget range")
    preferred_strategies: Optional[List[InvestmentStrategy]] = Field(None, description="Preferred investment strategies")
    risk_tolerance: Optional[str] = Field(None, description="Risk tolerance (low/medium/high)")
    
    # Geographic preferences
    target_locations: Optional[List[Dict[str, str]]] = Field(None, description="Target investment locations")
    max_distance: Optional[int] = Field(None, description="Maximum distance from base location")
    
    # Property preferences
    preferred_property_types: Optional[List[PropertyType]] = Field(None, description="Preferred property types")
    min_cap_rate: Optional[float] = Field(None, description="Minimum acceptable cap rate")
    min_cash_return: Optional[float] = Field(None, description="Minimum cash-on-cash return")
    
    # Timeline
    investment_timeline: Optional[str] = Field(None, description="Investment timeline")
    availability: Optional[str] = Field(None, description="Time availability for management")
    
    created_date: datetime = Field(default_factory=datetime.now, description="Profile creation date")
    updated_date: datetime = Field(default_factory=datetime.now, description="Last update date")