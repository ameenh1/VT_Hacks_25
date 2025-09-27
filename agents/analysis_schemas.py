"""
Analysis Engine Schemas for Structured AI Responses
===================================================

These schemas define the expected JSON output format for AI-powered analysis.
They ensure consistent, structured responses from the Gemini AI models.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union, Any
from enum import Enum
from datetime import datetime

# Valuation Schemas

class ValuationMethod(str, Enum):
    COMPARABLE_SALES = "comparable_sales"
    COST_APPROACH = "cost_approach" 
    INCOME_APPROACH = "income_approach"
    AVM_ESTIMATE = "avm_estimate"

class ARVCalculationSchema(BaseModel):
    """Schema for After Repair Value (ARV) calculation response"""
    arv_estimate: float = Field(..., description="Estimated After Repair Value in USD")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence level 0-1")
    price_per_sqft: float = Field(..., description="Calculated price per square foot")
    
    valuation_methods: Dict[ValuationMethod, float] = Field(..., description="Value from each method")
    method_weights: Dict[ValuationMethod, float] = Field(..., description="Weight given to each method")
    
    comparable_properties: List[Dict] = Field(default=[], description="Key comparable properties used")
    market_adjustments: Dict[str, float] = Field(default={}, description="Market condition adjustments")
    
    key_factors: List[str] = Field(..., description="Primary factors influencing valuation")
    methodology_notes: str = Field(..., description="Explanation of calculation approach")
    
    value_range: Dict[str, float] = Field(
        ..., 
        description="Conservative and optimistic value estimates",
        example={"conservative": 280000, "optimistic": 320000}
    )

class SellValueEstimationSchema(BaseModel):
    """Schema for property sell value estimation with market factors"""
    estimated_sell_value: float = Field(..., description="Current estimated sell value")
    quick_sale_value: float = Field(..., description="Value if sold within 30 days")
    optimal_sale_value: float = Field(..., description="Value with optimal timing/marketing")
    
    time_to_sell_estimate: Dict[str, int] = Field(
        ...,
        description="Days to sell at different price points",
        example={"quick": 30, "market": 90, "premium": 180}
    )
    
    market_factors: Dict[str, Union[float, str]] = Field(..., description="Factors affecting sale")
    seasonal_adjustments: Dict[str, float] = Field(default={}, description="Seasonal price variations")
    
    pricing_recommendations: List[Dict[str, Union[str, float]]] = Field(
        ..., 
        description="Recommended pricing strategies"
    )
    
    confidence_level: float = Field(..., ge=0, le=1, description="Overall confidence in estimate")

# Risk Assessment Schema

class RiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate" 
    HIGH = "high"
    CRITICAL = "critical"

class RiskFactor(BaseModel):
    """Individual risk factor assessment"""
    risk_type: str = Field(..., description="Type of risk (market, financial, property, etc.)")
    level: RiskLevel = Field(..., description="Risk severity level")
    impact_score: float = Field(..., ge=0, le=10, description="Potential impact score 0-10")
    probability: float = Field(..., ge=0, le=1, description="Probability of occurrence 0-1")
    description: str = Field(..., description="Detailed risk description")
    mitigation_strategies: List[str] = Field(default=[], description="Ways to mitigate this risk")

class RiskAssessmentSchema(BaseModel):
    """Schema for comprehensive risk assessment"""
    overall_risk_score: float = Field(..., ge=0, le=10, description="Overall risk score 0-10")
    risk_rating: RiskLevel = Field(..., description="Overall risk classification")
    
    risk_factors: List[RiskFactor] = Field(..., description="Individual risk factors")
    
    risk_categories: Dict[str, Dict] = Field(
        ..., 
        description="Risk breakdown by category",
        example={
            "market_risk": {"score": 6.5, "level": "moderate"},
            "financial_risk": {"score": 4.2, "level": "low"},
            "property_risk": {"score": 7.8, "level": "high"}
        }
    )
    
    key_concerns: List[str] = Field(..., description="Top 3 risk concerns")
    risk_timeline: Dict[str, List[str]] = Field(
        default={},
        description="Risks by timeframe",
        example={
            "immediate": ["Property condition issues"],
            "short_term": ["Interest rate changes"],
            "long_term": ["Neighborhood decline"]
        }
    )

# Market Analysis Schema

class MarketCondition(str, Enum):
    BUYERS_MARKET = "buyers_market"
    SELLERS_MARKET = "sellers_market" 
    BALANCED_MARKET = "balanced_market"

class MarketAnalysisSchema(BaseModel):
    """Schema for market analysis response"""
    market_condition: MarketCondition = Field(..., description="Current market state")
    market_temperature: str = Field(..., description="Hot/Warm/Cool/Cold market description")
    
    price_trends: Dict[str, float] = Field(
        ...,
        description="Price trend percentages",
        example={"3_month": 2.5, "6_month": 5.1, "12_month": 8.3}
    )
    
    inventory_analysis: Dict[str, Union[float, int]] = Field(
        ...,
        description="Inventory metrics",
        example={"months_supply": 2.3, "new_listings": 145, "absorption_rate": 0.65}
    )
    
    competitive_analysis: Dict[str, Any] = Field(..., description="Competitive market factors")
    
    investment_climate: Dict[str, Union[str, float]] = Field(
        ...,
        description="Investment market conditions",
        example={"investor_activity": "high", "cap_rate_avg": 6.8, "rental_demand": "strong"}
    )
    
    market_drivers: List[str] = Field(..., description="Key factors driving market")
    future_outlook: Dict[str, str] = Field(
        ...,
        description="Market predictions",
        example={"6_month": "continued growth", "12_month": "moderate appreciation"}
    )

# Investment Strategy Schema

class InvestmentStrategyType(str, Enum):
    BUY_AND_HOLD = "buy_and_hold"
    FIX_AND_FLIP = "fix_and_flip"
    BRRRR = "brrrr"
    WHOLESALE = "wholesale"
    LIVE_IN_FLIP = "live_in_flip"

class CashFlowProjection(BaseModel):
    """Monthly cash flow projection"""
    gross_rental_income: float = Field(..., description="Monthly gross rent")
    operating_expenses: float = Field(..., description="Monthly operating costs")
    debt_service: float = Field(..., description="Monthly mortgage payment")
    net_cash_flow: float = Field(..., description="Monthly net cash flow")
    
    expense_breakdown: Dict[str, float] = Field(
        ...,
        description="Detailed expense categories",
        example={
            "property_tax": 350,
            "insurance": 125,
            "maintenance": 200,
            "vacancy": 150,
            "management": 180
        }
    )

class InvestmentStrategySchema(BaseModel):
    """Schema for investment strategy recommendation"""
    recommended_strategy: InvestmentStrategyType = Field(..., description="Primary recommended strategy")
    alternative_strategies: List[InvestmentStrategyType] = Field(
        default=[], 
        description="Alternative viable strategies"
    )
    
    financial_projections: Dict[str, Union[float, CashFlowProjection]] = Field(
        ..., description="Financial performance projections"
    )
    
    investment_metrics: Dict[str, float] = Field(
        ...,
        description="Key investment metrics",
        example={
            "cap_rate": 7.2,
            "cash_on_cash_return": 12.5,
            "irr_10_year": 14.8,
            "total_return_annual": 16.3
        }
    )
    
    execution_plan: List[Dict[str, str]] = Field(
        ...,
        description="Step-by-step implementation plan",
        example=[
            {"step": 1, "action": "Secure financing", "timeline": "2-3 weeks"},
            {"step": 2, "action": "Property inspection", "timeline": "1 week"}
        ]
    )
    
    success_factors: List[str] = Field(..., description="Key factors for strategy success")
    potential_challenges: List[str] = Field(..., description="Potential implementation challenges")

# Comprehensive Analysis Schema

class PropertyAnalysisSchema(BaseModel):
    """Complete property analysis result schema"""
    property_address: str = Field(..., description="Property address analyzed")
    analysis_timestamp: datetime = Field(default_factory=datetime.now)
    analysis_type: str = Field(..., description="Type of analysis performed")
    
    # Core Analysis Results
    valuation: ARVCalculationSchema = Field(..., description="Property valuation analysis")
    sell_value_estimate: SellValueEstimationSchema = Field(..., description="Current sell value estimation")
    risk_assessment: RiskAssessmentSchema = Field(..., description="Risk analysis")
    market_analysis: MarketAnalysisSchema = Field(..., description="Market conditions")
    investment_strategy: InvestmentStrategySchema = Field(..., description="Investment recommendations")
    
    # Summary Metrics
    deal_score: float = Field(..., ge=0, le=100, description="Overall deal score 0-100")
    investment_grade: str = Field(..., description="A+, A, B+, B, C+, C, D")
    confidence_score: float = Field(..., ge=0, le=1, description="Analysis confidence 0-1")
    
    # Key Insights
    key_insights: List[str] = Field(..., description="Top insights from analysis")
    red_flags: List[str] = Field(default=[], description="Major concerns identified")
    opportunities: List[str] = Field(default=[], description="Key opportunities identified")
    
    # Executive Summary
    executive_summary: str = Field(..., description="1-2 sentence investment summary")
    recommendation: str = Field(..., description="Buy/Hold/Pass recommendation with rationale")