"""
Pydantic Models for Real Estate Investment Platform
Comprehensive data models for property analysis, agent communication, and API responses
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from enum import Enum


class PropertyType(str, Enum):
    SINGLE_FAMILY = "single_family"
    CONDO = "condo" 
    TOWNHOUSE = "townhouse"
    MULTI_FAMILY = "multi_family"
    COMMERCIAL = "commercial"


class InvestmentStrategy(str, Enum):
    BUY_AND_HOLD = "buy_and_hold"
    FLIP = "flip"
    BRRRR = "brrrr"
    WHOLESALE = "wholesale"


class AgentType(str, Enum):
    CUSTOMER_AGENT = "customer_agent"
    ANALYSIS_ENGINE = "analysis_engine"  
    DEAL_FINDER = "deal_finder"


class AnalysisType(str, Enum):
    QUICK = "quick"
    COMPREHENSIVE = "comprehensive"
    MARKET_ONLY = "market_only"
    RISK_ONLY = "risk_only"


# Core Property Models

class PropertyDetails(BaseModel):
    """Detailed property information"""
    address: str = Field(..., description="Full property address")
    city: str
    state: str  
    zip_code: str
    property_type: PropertyType
    bedrooms: int = Field(..., ge=0, le=20)
    bathrooms: float = Field(..., ge=0, le=20)
    square_feet: int = Field(..., gt=0)
    lot_size: Optional[float] = Field(None, description="Lot size in acres")
    year_built: Optional[int] = Field(None, ge=1800, le=2030)
    listing_price: Optional[float] = Field(None, gt=0)
    zestimate: Optional[float] = Field(None, gt=0)
    rent_estimate: Optional[float] = Field(None, gt=0)
    mls_number: Optional[str] = None
    property_id: Optional[str] = None
    
    @validator('zip_code')
    def validate_zip_code(cls, v):
        if len(v) not in [5, 9] or not v.replace('-', '').isdigit():
            raise ValueError('Invalid zip code format')
        return v


class MarketMetrics(BaseModel):
    """Market conditions and trends"""
    median_home_price: float = Field(..., gt=0)
    price_per_sqft: float = Field(..., gt=0)
    days_on_market: int = Field(..., ge=0)
    inventory_months: float = Field(..., gt=0)
    price_trend_3m: float = Field(..., description="3-month price trend percentage")
    price_trend_6m: float = Field(..., description="6-month price trend percentage") 
    price_trend_1y: float = Field(..., description="1-year price trend percentage")
    rental_yield_avg: float = Field(..., gt=0)
    cap_rate_avg: float = Field(..., gt=0)
    absorption_rate: Optional[float] = Field(None, description="Market absorption rate")
    new_listings: Optional[int] = Field(None, ge=0)
    price_cuts: Optional[float] = Field(None, description="Percentage of listings with price cuts")


class ComparableProperty(BaseModel):
    """Comparable property information"""
    address: str
    distance: float = Field(..., description="Distance in miles")
    price: float = Field(..., gt=0)
    price_per_sqft: float = Field(..., gt=0) 
    bedrooms: int
    bathrooms: float
    square_feet: int
    days_on_market: int
    sale_date: Optional[datetime] = None
    similarity_score: float = Field(..., ge=0, le=1)
    adjustment_factors: Optional[Dict[str, float]] = None


# Analysis Result Models

class CashFlowProjection(BaseModel):
    """Cash flow analysis results"""
    monthly_rent: float
    monthly_expenses: float
    monthly_cash_flow: float
    annual_cash_flow: float
    cash_on_cash_return: float = Field(..., description="Percentage return on cash invested")
    cap_rate: float = Field(..., description="Capitalization rate")
    gross_rent_multiplier: Optional[float] = None
    five_year_projection: Optional[float] = None
    
    @validator('cash_on_cash_return', 'cap_rate')
    def validate_percentages(cls, v):
        if v < -50 or v > 100:
            raise ValueError('Percentage values should be reasonable (-50% to 100%)')
        return v


class RiskCategory(BaseModel):
    """Individual risk category assessment"""
    score: int = Field(..., ge=1, le=10, description="Risk score from 1 (low) to 10 (high)")
    description: str
    mitigation_strategies: List[str] = []
    impact_level: str = Field(..., pattern="^(low|medium|high)$")


class RiskAssessment(BaseModel):
    """Comprehensive risk analysis"""
    overall_risk_score: int = Field(..., ge=1, le=10)
    market_risk: RiskCategory
    property_risk: RiskCategory
    financial_risk: RiskCategory
    regulatory_risk: RiskCategory
    liquidity_risk: Optional[RiskCategory] = None
    red_flags: List[str] = []
    confidence_level: float = Field(..., ge=0, le=1)


class InvestmentReturns(BaseModel):
    """Expected investment returns"""
    annual_cash_flow: float
    total_return_estimate: float = Field(..., description="Expected total return percentage")
    appreciation_estimate: float = Field(..., description="Expected appreciation percentage")
    timeframe: str = Field(..., description="Investment timeframe")
    break_even_months: Optional[int] = None
    irr: Optional[float] = Field(None, description="Internal Rate of Return")
    roi_percentage: Optional[float] = Field(None, description="Return on Investment percentage")


class StrategyRecommendation(BaseModel):
    """Investment strategy recommendation"""
    strategy: InvestmentStrategy
    reasoning: str
    expected_returns: InvestmentReturns
    implementation_steps: List[str]
    success_probability: float = Field(..., ge=0, le=1)
    timeline: Optional[str] = None
    capital_requirements: Optional[Dict[str, float]] = None


# Comprehensive Analysis Result

class PropertyAnalysis(BaseModel):
    """Complete property analysis results"""
    property_details: PropertyDetails
    market_metrics: MarketMetrics
    arv_estimate: float = Field(..., gt=0, description="After Repair Value")
    arv_confidence: float = Field(..., ge=0, le=1)
    deal_score: float = Field(..., ge=0, le=100, description="Overall deal score out of 100")
    investment_potential: str = Field(..., pattern="^(Excellent|Good|Fair|Poor)$")
    recommended_strategy: StrategyRecommendation
    cash_flow_projection: CashFlowProjection
    risk_assessment: RiskAssessment
    comparable_properties: List[ComparableProperty]
    market_analysis: str
    key_insights: List[str]
    analysis_confidence: float = Field(..., ge=0, le=1)
    analysis_timestamp: datetime = Field(default_factory=datetime.now)
    analysis_id: Optional[str] = None


# Agent Communication Models

class AgentRequest(BaseModel):
    """Base model for inter-agent communication"""
    request_id: str
    requesting_agent: AgentType
    target_agent: AgentType
    request_type: str
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)
    priority: int = Field(1, ge=1, le=5, description="Priority level 1-5")


class AgentResponse(BaseModel):
    """Base model for agent responses"""
    request_id: str
    responding_agent: AgentType
    success: bool
    payload: Dict[str, Any]
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    processing_time_ms: Optional[int] = None


class AnalysisRequest(AgentRequest):
    """Specific request for property analysis"""
    analysis_type: AnalysisType
    property_address: str
    user_preferences: Optional[Dict[str, Any]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "request_id": "req_123456",
                "requesting_agent": "customer_agent",
                "target_agent": "analysis_engine",
                "request_type": "property_analysis",
                "analysis_type": "comprehensive",
                "property_address": "123 Main St, Blacksburg, VA 24060",
                "payload": {
                    "listing_price": 350000,
                    "user_budget": 400000,
                    "investment_goals": "buy_and_hold"
                }
            }
        }


class QuickAnalysisRequest(BaseModel):
    """Quick analysis request model"""
    address: str
    listing_price: Optional[float] = None
    user_id: Optional[str] = None
    analysis_depth: str = Field("basic", pattern="^(basic|detailed)$")


class QuickAnalysisResponse(BaseModel):
    """Quick analysis response model"""
    address: str
    deal_score: float = Field(..., ge=0, le=100)
    investment_potential: str
    arv_estimate: float
    recommended_strategy: InvestmentStrategy
    monthly_cash_flow: float
    key_insight: str
    analysis_timestamp: datetime = Field(default_factory=datetime.now)
    confidence_score: float = Field(..., ge=0, le=1)


# API Endpoint Models

class AnalysisAPIRequest(BaseModel):
    """API request for property analysis"""
    property_address: str
    analysis_type: AnalysisType = AnalysisType.COMPREHENSIVE
    listing_price: Optional[float] = None
    user_preferences: Optional[Dict[str, Any]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "property_address": "123 Investment Ave, Blacksburg, VA 24060",
                "analysis_type": "comprehensive",
                "listing_price": 275000,
                "user_preferences": {
                    "max_budget": 300000,
                    "strategy_preference": "buy_and_hold",
                    "risk_tolerance": "moderate"
                }
            }
        }


class AnalysisAPIResponse(BaseModel):
    """API response for property analysis"""
    status: str = Field(..., pattern="^(success|error|processing)$")
    analysis_id: str
    property_analysis: Optional[PropertyAnalysis] = None
    error_message: Optional[str] = None
    processing_time_seconds: Optional[float] = None
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "analysis_id": "analysis_789012",
                "processing_time_seconds": 12.5,
                "property_analysis": {
                    "deal_score": 78.5,
                    "investment_potential": "Good",
                    "arv_estimate": 285000
                }
            }
        }


# ATTOM API Integration Models

class ATTOMPropertyData(BaseModel):
    """ATTOM Data API property response model"""
    property_id: str
    address: str
    city: str
    state: str
    zip_code: str
    county: str
    fips_code: Optional[str] = None
    apn: Optional[str] = None
    property_type: str
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    square_feet: Optional[int] = None
    lot_size_sqft: Optional[int] = None
    year_built: Optional[int] = None
    estimated_value: Optional[float] = None
    last_sale_price: Optional[float] = None
    last_sale_date: Optional[datetime] = None
    tax_assessed_value: Optional[float] = None
    tax_year: Optional[int] = None
    owner_occupied: Optional[bool] = None


class ATTOMMarketData(BaseModel):
    """ATTOM market analytics response model"""
    county_fips: str
    county_name: str
    state: str
    median_sale_price: float
    median_price_per_sqft: float
    median_days_on_market: int
    months_of_supply: float
    price_change_3m: float
    price_change_6m: float
    price_change_12m: float
    sales_volume: int
    new_listings: int
    foreclosure_rate: Optional[float] = None
    rental_yield: Optional[float] = None


class ATTOMSearchCriteria(BaseModel):
    """Search criteria for ATTOM property search"""
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    county: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_bedrooms: Optional[int] = None
    max_bedrooms: Optional[int] = None
    min_bathrooms: Optional[float] = None
    max_bathrooms: Optional[float] = None
    min_sqft: Optional[int] = None
    max_sqft: Optional[int] = None
    property_types: Optional[List[str]] = None
    radius_miles: Optional[float] = None
    max_results: int = Field(50, ge=1, le=1000)


# Error Models

class ValidationError(BaseModel):
    """Validation error details"""
    field: str
    message: str
    invalid_value: Any


class APIError(BaseModel):
    """API error response"""
    error_code: str
    error_message: str
    details: Optional[List[ValidationError]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: Optional[str] = None


# Health Check Models

class AgentHealthStatus(BaseModel):
    """Individual agent health status"""
    agent_type: AgentType
    status: str = Field(..., pattern="^(healthy|degraded|unhealthy)$") 
    last_check: datetime
    response_time_ms: Optional[int] = None
    error_rate: Optional[float] = None
    active_requests: Optional[int] = None


class SystemHealthStatus(BaseModel):
    """Overall system health status"""
    overall_status: str = Field(..., pattern="^(healthy|degraded|unhealthy)$")
    agents: List[AgentHealthStatus]
    attom_api_status: str = Field(..., pattern="^(connected|disconnected|error)$")
    gemini_api_status: str = Field(..., pattern="^(connected|disconnected|error)$")
    database_status: Optional[str] = None
    uptime_seconds: int
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.now)