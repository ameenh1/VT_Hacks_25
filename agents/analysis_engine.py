"""
Professional Real Estate Analysis Engine
========================================

Implements industry-standard real estate appraisal methodology using three approaches:
1. Sales Comparison Approach (Market Data)
2. Income Approach (Capitalization & GRM)  
3. Cost Approach (Replacement Cost Less Depreciation)

Standalone analysis engine with professional-grade valuation capabilities.
"""

import google.generativeai as genai
import json
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import math
import statistics
import asyncio
from pydantic import BaseModel, Field

# Import analysis schemas for professional valuation
from agents.analysis_schemas import (
    ARVCalculationSchema, SellValueEstimationSchema, RiskAssessmentSchema,
    MarketAnalysisSchema, InvestmentStrategySchema, PropertyAnalysisSchema,
    ValuationMethod, RiskLevel, MarketCondition, InvestmentStrategyType,
    RiskFactor, CashFlowProjection
)

logger = logging.getLogger(__name__)


class ValuationApproach(str, Enum):
    SALES_COMPARISON = "sales_comparison"
    INCOME_APPROACH = "income_approach"
    COST_APPROACH = "cost_approach"


class ConfidenceLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class ComparableSale:
    """Individual comparable sale data"""
    address: str
    sale_price: float
    sale_date: datetime
    gla: int  # Gross Living Area
    bedrooms: int
    bathrooms: float
    garage_spaces: int
    lot_size: float
    distance: float  # Distance from subject in miles
    condition: str
    age: int
    
    # Calculated fields
    price_per_sqft: Optional[float] = None
    time_adjusted_price: Optional[float] = None
    total_adjustments: Optional[float] = None
    adjusted_price: Optional[float] = None
    weight: Optional[float] = None
    adjustments: Optional[Dict[str, float]] = None
    
    def __post_init__(self):
        if self.price_per_sqft is None:
            self.price_per_sqft = self.sale_price / self.gla if self.gla > 0 else 0


@dataclass
class PropertyFeatures:
    """Subject property features for analysis"""
    address: str
    gla: int
    bedrooms: int
    bathrooms: float
    garage_spaces: int
    lot_size: float
    age: int
    condition: str
    property_type: str
    
    # Market data
    listing_price: Optional[float] = None
    monthly_rent: Optional[float] = None


class AnalysisEngine:
    """
    Professional Real Estate Analysis Engine
    Implements industry-standard 3-approach valuation methodology:
    1. Sales Comparison Approach
    2. Income Approach 
    3. Cost Approach
    
    Uses Gemini 2.5 Pro for AI-enhanced analysis and structured responses
    """
    
    def __init__(self, api_key: str, deal_finder=None):
        """Initialize the Professional Analysis Engine"""
        self.api_key = api_key
        genai.configure(api_key=api_key)
        
        # Use Gemini 2.5 Pro for complex analysis tasks
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        
        # Deal Finder integration for data sourcing
        self.deal_finder = deal_finder
        
        # Professional adjustment rates (dynamically updated)
        self.adjustment_rates = {
            'gla_per_sqft': 50.0,  # $/sq ft adjustment for GLA differences
            'bathroom_value': 3000.0,  # Value per bathroom
            'garage_value': 5000.0,  # Value per garage space
            'lot_per_sqft': 2.0,  # $/sq ft for lot size differences
            'annual_appreciation': 0.05,  # 5% annual market appreciation
            'condition_multipliers': {
                'excellent': 1.1,
                'good': 1.0, 
                'average': 0.95,
                'fair': 0.9,
                'poor': 0.8
            }
        }
        
        # Analysis parameters for professional valuation
        self.analysis_prompts = self._load_professional_analysis_prompts()
        
        logger.info("Professional Analysis Engine initialized with Gemini 2.5 Pro")
    
    def _load_professional_analysis_prompts(self) -> Dict[str, str]:
        """Load professional appraisal prompts for AI analysis"""
        return {
            "sales_comparison": """
            You are a certified real estate appraiser using the Sales Comparison Approach.
            
            Analyze the subject property and comparable sales data provided.
            Apply appropriate adjustments for differences in:
            - Time of sale (market conditions changes)
            - Location and neighborhood factors
            - Physical characteristics (size, bedrooms, bathrooms, etc.)
            - Condition and quality
            - Site characteristics (lot size, topography, etc.)
            
            Provide a professional analysis with weighted reconciliation of adjusted comparable sales.
            
            Respond in structured JSON format matching the ARVCalculationSchema.
            """,
            
            "income_approach": """
            You are analyzing this property using the Income Approach to value.
            
            Calculate:
            1. Net Operating Income (NOI) - rental income less operating expenses
            2. Capitalization Rate - from market sales of similar rental properties
            3. Gross Rent Multiplier (GRM) - from rental property sales
            4. Value indications from both methods
            
            Consider local vacancy rates, operating expense ratios, and market cap rates.
            
            Provide analysis in structured JSON format.
            """,
            
            "cost_approach": """
            You are applying the Cost Approach to value this property.
            
            Calculate:
            1. Current replacement cost of improvements
            2. Depreciation (physical, functional, external obsolescence)
            3. Land value (separate valuation)
            4. Final value indication: Land Value + (Replacement Cost - Depreciation)
            
            Consider property age, condition, and local construction costs.
            
            Provide analysis in structured JSON format.
            """,
            
            "market_analysis": """
            You are analyzing current real estate market conditions for investment decisions.
            
            Evaluate:
            1. Market temperature (buyer's vs seller's market)
            2. Price trends and momentum
            3. Inventory levels and days on market
            4. Economic factors affecting real estate
            5. Investment climate and opportunities
            
            Provide actionable market insights for real estate investors.
            
            Respond in structured JSON format matching the MarketAnalysisSchema.
            """,
            
            "risk_assessment": """
            You are conducting a comprehensive investment risk assessment.
            
            Analyze risks in these categories:
            1. Market risk (volatility, demand/supply, cycles)
            2. Property risk (condition, location, tenant factors)
            3. Financial risk (leverage, cash flow, interest rates)
            4. Regulatory risk (zoning, taxes, rent control)
            5. Management risk (vacancy, maintenance, tenant quality)
            
            Rate each risk factor and provide mitigation strategies.
            
            Respond in structured JSON format matching the RiskAssessmentSchema.
            """,
            
            "investment_strategy": """
            You are recommending optimal investment strategy for this property.
            
            Consider these strategies:
            1. Buy & Hold - long-term rental income and appreciation
            2. Fix & Flip - renovation and quick resale
            3. BRRRR - Buy, Rehab, Rent, Refinance, Repeat
            4. Wholesale - contract assignment for quick profit
            5. Live-in Flip - owner-occupied renovation
            
            Recommend strategy based on property characteristics, market conditions, and financial analysis.
            
            Respond in structured JSON format matching the InvestmentStrategySchema.
            """
        }
    
    async def analyze_property_batch(self, properties: List[PropertyFeatures], 
                                   user_criteria: Dict = None) -> List[PropertyAnalysisSchema]:
        """
        Phase 1.1: Process batch of properties from Deal Finder
        """
        analyses = []
        
        for property_data in properties:
            try:
                analysis = await self.comprehensive_valuation_analysis(
                    property_data, user_criteria
                )
                analyses.append(analysis)
            except Exception as e:
                logger.error(f"Failed to analyze {property_data.address}: {str(e)}")
                continue
                
        return analyses
    
    async def comprehensive_valuation_analysis(self, property_data: PropertyFeatures,
                                             user_criteria: Dict = None) -> PropertyAnalysisSchema:
        """
        Complete professional valuation analysis using all three approaches
        """
        
        try:
            # Phase 1.2: Get comparable sales data (mock data for standalone operation)
            comparable_sales = await self._get_comparable_sales_data(property_data)
            
            # Phase 1: Sales Comparison Approach
            sales_analysis = await self._sales_comparison_analysis(property_data, comparable_sales)
            
            # Phase 2: Income Approach
            income_analysis = await self._income_approach_analysis(property_data)
            
            # Phase 3: Cost Approach  
            cost_analysis = await self._cost_approach_analysis(property_data)
            
            # Phase 4: AI-Enhanced Analysis & Reconciliation
            final_analysis = await self._ai_enhanced_reconciliation(
                property_data, sales_analysis, income_analysis, cost_analysis, user_criteria
            )
            
            return final_analysis
        
        except Exception as e:
            logger.error(f"Comprehensive valuation failed for {property_data.address}: {str(e)}")
            return await self._create_fallback_analysis(property_data)
    
    async def _get_comparable_sales_data(self, property_data: PropertyFeatures) -> List[ComparableSale]:
        """
        Phase 1.2: Get comparable sales data
        For standalone operation, generates realistic mock comparables
        """
        
        # Generate mock comparable sales for demonstration
        base_price = property_data.listing_price or 300000
        comps = []
        
        for i in range(5):
            # Create realistic variations
            price_variation = 1 + (i - 2) * 0.05  # ±10% price variation
            size_variation = 1 + (i - 2) * 0.08   # ±16% size variation
            age_variation = (i - 2) * 3           # ±6 years age variation
            
            comp = ComparableSale(
                address=f"{1000 + i * 100} Comparable St",
                sale_price=int(base_price * price_variation),
                sale_date=datetime.now() - timedelta(days=30 + i * 20),
                gla=int(property_data.gla * size_variation),
                bedrooms=property_data.bedrooms + (1 if i > 3 else -1 if i < 1 else 0),
                bathrooms=property_data.bathrooms,
                garage_spaces=property_data.garage_spaces,
                lot_size=property_data.lot_size + (i - 2) * 1000,
                distance=0.2 + i * 0.1,
                condition=['excellent', 'good', 'good', 'average', 'fair'][i],
                age=property_data.age + age_variation
            )
            comps.append(comp)
        
        return comps
    
    async def _sales_comparison_analysis(self, property_data: PropertyFeatures, 
                                       comparables: List[ComparableSale]) -> Dict[str, Any]:
        """
        Phase 1: Complete Sales Comparison Approach Implementation
        """
        
        # Phase 1.3: Time adjustments
        time_adjusted_comps = []
        for comp in comparables:
            adjusted_price = self._calculate_time_adjustment(
                comp.sale_price, comp.sale_date, datetime.now()
            )
            comp.time_adjusted_price = adjusted_price
            time_adjusted_comps.append(comp)
        
        # Phase 1.4: Feature adjustments
        feature_adjusted_comps = []
        for comp in time_adjusted_comps:
            adjustments = self._calculate_feature_adjustments(property_data, comp)
            comp.total_adjustments = sum(adjustments.values())
            comp.adjusted_price = comp.time_adjusted_price + comp.total_adjustments
            comp.adjustments = adjustments
            feature_adjusted_comps.append(comp)
        
        # Phase 1.5: Weighted reconciliation
        weighted_value = self._calculate_weighted_reconciliation(feature_adjusted_comps)
        
        # Calculate confidence based on adjustment sizes and data quality
        confidence = self._calculate_sales_confidence(feature_adjusted_comps)
        
        return {
            'comparable_sales': [self._comp_to_dict(comp) for comp in feature_adjusted_comps],
            'weighted_value': weighted_value,
            'confidence': confidence,
            'value_range': {
                'low': weighted_value * 0.92,
                'high': weighted_value * 1.08
            },
            'methodology': 'Sales comparison with time and feature adjustments'
        }
    
    def _calculate_time_adjustment(self, sale_price: float, sale_date: datetime, 
                                 valuation_date: datetime) -> float:
        """
        Phase 1.3: Time Adjustment Engine
        Formula: P_time = P_sale × (1 + r)^(Δt_years)
        """
        years_diff = (valuation_date - sale_date).days / 365.25
        annual_rate = self.adjustment_rates['annual_appreciation']
        
        time_adjusted_price = sale_price * ((1 + annual_rate) ** years_diff)
        return time_adjusted_price
    
    def _calculate_feature_adjustments(self, subject: PropertyFeatures, 
                                     comp: ComparableSale) -> Dict[str, float]:
        """
        Phase 1.4: Feature Adjustment Calculator
        Calculate dollar-based adjustments for property differences
        """
        adjustments = {}
        
        # GLA (Gross Living Area) adjustment
        gla_diff = subject.gla - comp.gla
        adjustments['gla_adjustment'] = gla_diff * self.adjustment_rates['gla_per_sqft']
        
        # Bedroom/bathroom adjustments
        bath_diff = subject.bathrooms - comp.bathrooms  
        adjustments['bathroom_adjustment'] = bath_diff * self.adjustment_rates['bathroom_value']
        
        # Garage adjustment
        garage_diff = subject.garage_spaces - comp.garage_spaces
        adjustments['garage_adjustment'] = garage_diff * self.adjustment_rates['garage_value']
        
        # Lot size adjustment
        lot_diff = subject.lot_size - comp.lot_size
        adjustments['lot_adjustment'] = lot_diff * self.adjustment_rates['lot_per_sqft']
        
        # Condition adjustment
        condition_multiplier = self.adjustment_rates['condition_multipliers'].get(subject.condition, 1.0)
        comp_multiplier = self.adjustment_rates['condition_multipliers'].get(comp.condition, 1.0)
        condition_adjustment = comp.time_adjusted_price * (condition_multiplier - comp_multiplier)
        adjustments['condition_adjustment'] = condition_adjustment
        
        return adjustments
    
    def _calculate_weighted_reconciliation(self, adjusted_comps: List[ComparableSale]) -> float:
        """
        Phase 1.5: Weighted Reconciliation System
        Weight comparables based on adjustment size, recency, distance, and similarity
        """
        total_weighted_value = 0
        total_weight = 0
        
        for comp in adjusted_comps:
            # Base weight factors
            k = 0.1  # Base constant
            
            # Weight by adjustment size (larger adjustments = lower weight)
            adjustment_factor = abs(comp.total_adjustments) / comp.time_adjusted_price
            adjustment_weight = 1 / (k + adjustment_factor)
            
            # Weight by recency (older sales = lower weight)
            months_old = (datetime.now() - comp.sale_date).days / 30.0
            recency_weight = 1 / (1 + months_old * 0.1)
            
            # Weight by distance (farther = lower weight)
            distance_weight = 1 / (1 + comp.distance * 0.5)
            
            # Combined weight
            comp.weight = adjustment_weight * recency_weight * distance_weight
            
            total_weighted_value += comp.adjusted_price * comp.weight
            total_weight += comp.weight
        
        return total_weighted_value / total_weight if total_weight > 0 else 0
    
    def _calculate_sales_confidence(self, adjusted_comps: List[ComparableSale]) -> ConfidenceLevel:
        """
        Calculate confidence level based on data quality and adjustments
        """
        if not adjusted_comps:
            return ConfidenceLevel.LOW
        
        # Calculate average adjustment percentage
        avg_adjustment_pct = statistics.mean([
            abs(comp.total_adjustments) / comp.time_adjusted_price 
            for comp in adjusted_comps
        ])
        
        # Calculate data recency score
        avg_age_months = statistics.mean([
            (datetime.now() - comp.sale_date).days / 30.0 
            for comp in adjusted_comps
        ])
        
        # Determine confidence level
        if avg_adjustment_pct < 0.05 and avg_age_months < 3:
            return ConfidenceLevel.VERY_HIGH
        elif avg_adjustment_pct < 0.10 and avg_age_months < 6:
            return ConfidenceLevel.HIGH
        elif avg_adjustment_pct < 0.20 and avg_age_months < 12:
            return ConfidenceLevel.MODERATE
        else:
            return ConfidenceLevel.LOW
    
    async def _income_approach_analysis(self, property_data: PropertyFeatures) -> Dict[str, Any]:
        """
        Phase 2: Income Approach Implementation
        """
        if not property_data.monthly_rent:
            return {
                'applicable': False,
                'reason': 'No rental data available',
                'value': 0,
                'confidence': ConfidenceLevel.LOW
            }
        
        # Phase 2.1: NOI Calculation
        annual_rent = property_data.monthly_rent * 12
        vacancy_rate = 0.08  # 8% default vacancy rate
        effective_income = annual_rent * (1 - vacancy_rate)
        
        # Operating expenses estimation (% of effective income)
        operating_expenses = effective_income * 0.35  # 35% of effective income
        noi = effective_income - operating_expenses
        
        # Phase 2.2: Cap Rate Analysis
        market_cap_rate = await self._get_market_cap_rate(property_data)
        cap_rate_value = noi / market_cap_rate if market_cap_rate > 0 else 0
        
        # Phase 2.3: GRM Method
        market_grm = await self._get_market_grm(property_data)
        grm_value = property_data.monthly_rent * market_grm if market_grm > 0 else 0
        
        # Reconcile income approach values
        income_values = [cap_rate_value, grm_value]
        income_values = [v for v in income_values if v > 0]
        
        if income_values:
            income_value = statistics.mean(income_values)
            confidence = ConfidenceLevel.MODERATE
        else:
            income_value = 0
            confidence = ConfidenceLevel.LOW
        
        return {
            'applicable': True,
            'noi': noi,
            'cap_rate': market_cap_rate,
            'cap_rate_value': cap_rate_value,
            'grm': market_grm,
            'grm_value': grm_value,
            'value': income_value,
            'confidence': confidence
        }
    
    async def _get_market_cap_rate(self, property_data: PropertyFeatures) -> float:
        """
        Get market cap rate for the area and property type
        """
        # Default cap rates by property type
        default_cap_rates = {
            'SFR': 0.065,  # 6.5% for single family
            'CON': 0.070,  # 7.0% for condos
            'TWH': 0.068,  # 6.8% for townhomes
        }
        
        return default_cap_rates.get(property_data.property_type, 0.065)
    
    async def _get_market_grm(self, property_data: PropertyFeatures) -> float:
        """
        Get market Gross Rent Multiplier for the area
        """
        # Default GRM values
        default_grm = {
            'SFR': 140,  # 140 months for single family
            'CON': 130,  # 130 months for condos  
            'TWH': 135,  # 135 months for townhomes
        }
        
        return default_grm.get(property_data.property_type, 140)
    
    async def _cost_approach_analysis(self, property_data: PropertyFeatures) -> Dict[str, Any]:
        """
        Phase 3: Cost Approach Implementation
        """
        
        # Phase 3.1: Replacement cost estimation
        cost_per_sqft = await self._get_construction_costs(property_data)
        replacement_cost = property_data.gla * cost_per_sqft
        
        # Add soft costs (15% of construction)
        soft_costs = replacement_cost * 0.15
        total_replacement_cost = replacement_cost + soft_costs
        
        # Phase 3.2: Depreciation analysis
        depreciation_rate = self._calculate_depreciation(property_data)
        depreciated_cost = total_replacement_cost * (1 - depreciation_rate)
        
        # Phase 3.3: Land value assessment
        land_value = await self._get_land_value(property_data)
        
        # Total cost approach value
        cost_value = land_value + depreciated_cost
        
        # Confidence based on property age and data availability
        if property_data.age < 10:
            confidence = ConfidenceLevel.HIGH
        elif property_data.age < 20:
            confidence = ConfidenceLevel.MODERATE  
        else:
            confidence = ConfidenceLevel.LOW
        
        return {
            'replacement_cost': total_replacement_cost,
            'depreciation_rate': depreciation_rate,
            'depreciated_cost': depreciated_cost,
            'land_value': land_value,
            'value': cost_value,
            'confidence': confidence
        }
    
    async def _get_construction_costs(self, property_data: PropertyFeatures) -> float:
        """
        Get local construction costs per square foot
        """
        # Default construction costs by property type
        default_costs = {
            'SFR': 120.0,  # $120/sq ft
            'CON': 110.0,  # $110/sq ft
            'TWH': 115.0,  # $115/sq ft
        }
        
        return default_costs.get(property_data.property_type, 120.0)
    
    def _calculate_depreciation(self, property_data: PropertyFeatures) -> float:
        """
        Calculate depreciation based on age and condition
        """
        # Effective age based on condition
        condition_factors = {
            'excellent': 0.8,
            'good': 1.0,
            'average': 1.2,
            'fair': 1.5,
            'poor': 2.0
        }
        
        condition_factor = condition_factors.get(property_data.condition, 1.0)
        effective_age = property_data.age * condition_factor
        
        # Economic life by property type
        economic_life = {
            'SFR': 60,  # 60 years
            'CON': 50,  # 50 years
            'TWH': 55,  # 55 years
        }.get(property_data.property_type, 60)
        
        # Physical depreciation
        physical_depreciation = min(1.0, effective_age / economic_life)
        
        return physical_depreciation
    
    async def _get_land_value(self, property_data: PropertyFeatures) -> float:
        """
        Estimate land value
        """
        # Default land values per square foot
        default_land_values = 15.0  # $15/sq ft
        
        return property_data.lot_size * default_land_values
    
    async def _ai_enhanced_reconciliation(self, property_data: PropertyFeatures,
                                        sales_analysis: Dict, income_analysis: Dict,
                                        cost_analysis: Dict, user_criteria: Dict = None) -> PropertyAnalysisSchema:
        """
        Phase 4: AI-Enhanced Professional Analysis and Final Reconciliation
        """
        
        # Phase 4.3: Determine approach weights based on property type and data quality
        approach_weights = self._determine_approach_weights(
            property_data, sales_analysis, income_analysis, cost_analysis
        )
        
        # Calculate final reconciled value
        final_value = (
            sales_analysis['weighted_value'] * approach_weights[ValuationApproach.SALES_COMPARISON] +
            income_analysis['value'] * approach_weights[ValuationApproach.INCOME_APPROACH] +
            cost_analysis['value'] * approach_weights[ValuationApproach.COST_APPROACH]
        )
        
        # Phase 4.4: Investment analysis
        investment_metrics = await self._calculate_investment_metrics(
            property_data, final_value, user_criteria
        )
        
        # Phase 4.2: AI-powered market analysis
        market_analysis = await self._ai_market_analysis(property_data, final_value)
        
        # Create comprehensive ARV calculation schema
        arv_schema = ARVCalculationSchema(
            arv_estimate=final_value,
            confidence_score=0.8,  # Will calculate based on approach confidence
            price_per_sqft=final_value / property_data.gla if property_data.gla > 0 else 0,
            valuation_methods={
                ValuationMethod.COMPARABLE_SALES: sales_analysis['weighted_value'],
                ValuationMethod.INCOME_APPROACH: income_analysis['value'],
                ValuationMethod.COST_APPROACH: cost_analysis['value']
            },
            method_weights={
                ValuationMethod.COMPARABLE_SALES: approach_weights[ValuationApproach.SALES_COMPARISON],
                ValuationMethod.INCOME_APPROACH: approach_weights[ValuationApproach.INCOME_APPROACH],
                ValuationMethod.COST_APPROACH: approach_weights[ValuationApproach.COST_APPROACH]
            },
            comparable_properties=sales_analysis['comparable_sales'][:3],
            key_factors=self._identify_value_drivers(property_data, sales_analysis),
            methodology_notes="Professional 3-approach appraisal methodology with AI enhancement",
            value_range={
                'conservative': final_value * 0.92,
                'optimistic': final_value * 1.08
            }
        )
        
        # Create sell value estimation
        sell_value_schema = SellValueEstimationSchema(
            estimated_sell_value=final_value,
            quick_sale_value=final_value * 0.92,
            optimal_sale_value=final_value * 1.05,
            time_to_sell_estimate={
                'quick': 30,
                'market': 75,
                'premium': 120
            },
            market_factors=market_analysis,
            pricing_recommendations=[{
                'strategy': 'Market pricing',
                'price': final_value,
                'timeline': '60-90 days'
            }],
            confidence_level=0.8
        )
        
        # Create comprehensive analysis
        analysis = PropertyAnalysisSchema(
            property_address=property_data.address,
            analysis_type="comprehensive_professional_valuation",
            valuation=arv_schema,
            sell_value_estimate=sell_value_schema,
            risk_assessment=await self._create_risk_assessment_schema(property_data),
            market_analysis=await self._create_market_analysis_schema(property_data),
            investment_strategy=await self._create_investment_strategy_schema(property_data, final_value),
            deal_score=investment_metrics['deal_score'],
            investment_grade=self._calculate_investment_grade(investment_metrics['deal_score']),
            confidence_score=0.8,
            key_insights=await self._generate_key_insights(property_data, final_value),
            red_flags=self._identify_risk_factors(property_data),
            opportunities=self._identify_opportunities(property_data, final_value),
            executive_summary=f"Property valued at ${final_value:,.0f} with {investment_metrics['deal_score']:.0f}% deal score",
            recommendation=investment_metrics['recommendation']
        )
        
        return analysis
    
    def _determine_approach_weights(self, property_data: PropertyFeatures,
                                  sales_analysis: Dict, income_analysis: Dict,
                                  cost_analysis: Dict) -> Dict[ValuationApproach, float]:
        """
        Determine appropriate weights for each valuation approach
        """
        # Default weights for residential properties
        weights = {
            ValuationApproach.SALES_COMPARISON: 0.70,
            ValuationApproach.INCOME_APPROACH: 0.20,
            ValuationApproach.COST_APPROACH: 0.10
        }
        
        # Adjust based on data quality and applicability
        if sales_analysis['confidence'] == ConfidenceLevel.LOW:
            weights[ValuationApproach.SALES_COMPARISON] = 0.50
            weights[ValuationApproach.INCOME_APPROACH] = 0.30
            weights[ValuationApproach.COST_APPROACH] = 0.20
        
        if income_analysis['applicable'] and property_data.monthly_rent:
            weights[ValuationApproach.INCOME_APPROACH] = 0.30
            weights[ValuationApproach.SALES_COMPARISON] = 0.60
            weights[ValuationApproach.COST_APPROACH] = 0.10
        
        # For new construction, give more weight to cost approach
        if property_data.age < 5:
            weights[ValuationApproach.COST_APPROACH] = 0.25
            weights[ValuationApproach.SALES_COMPARISON] = 0.60
            weights[ValuationApproach.INCOME_APPROACH] = 0.15
        
        return weights
    
    async def _calculate_investment_metrics(self, property_data: PropertyFeatures,
                                          estimated_value: float, user_criteria: Dict = None) -> Dict[str, Any]:
        """
        Phase 4.4: Calculate investment metrics and deal score
        """
        
        # Deal score based on value vs listing price
        if property_data.listing_price:
            value_ratio = estimated_value / property_data.listing_price
            if value_ratio > 1.20:
                deal_score = 95
            elif value_ratio > 1.15:
                deal_score = 85
            elif value_ratio > 1.10:
                deal_score = 75
            elif value_ratio > 1.05:
                deal_score = 65
            else:
                deal_score = 50
        else:
            deal_score = 70  # Default score
        
        # Investment strategy recommendation
        if property_data.monthly_rent and property_data.monthly_rent * 12 / estimated_value > 0.08:
            strategy = "Buy and Hold - Strong Cash Flow"
            recommendation = "BUY - Excellent cash flow potential"
        elif property_data.condition in ['fair', 'poor']:
            strategy = "Fix and Flip - Value Add Opportunity"
            recommendation = "BUY - Good renovation opportunity"
        else:
            strategy = "Buy and Hold - Appreciation Focus"
            recommendation = "CONSIDER - Moderate investment potential"
        
        return {
            'deal_score': deal_score,
            'strategy': strategy,
            'recommendation': recommendation
        }
    
    async def _ai_market_analysis(self, property_data: PropertyFeatures, estimated_value: float) -> Dict[str, Any]:
        """
        Phase 4.2: AI-Powered Market Analysis
        """
        
        prompt = f"""
        As a professional real estate market analyst, analyze the current market conditions for this property:
        
        Property: {property_data.address}
        Property Type: {property_data.property_type}
        Estimated Value: ${estimated_value:,.0f}
        
        Provide analysis on:
        1. Current market conditions (buyer's vs seller's market)
        2. Price trends in the area
        3. Days on market expectations
        4. Seasonal factors
        5. Market outlook (next 6-12 months)
        
        Respond ONLY with valid JSON in this exact format:
        {{
            "market_type": "buyer_market|seller_market|balanced",
            "trends": "rising|declining|stable",
            "dom_estimate": 60,
            "seasonal_factors": "favorable|normal|challenging",
            "outlook": "positive|stable|cautious"
        }}
        """
        
        try:
            response = await self.model.generate_content_async(prompt)
            response_text = response.text.strip()
            
            # Try to extract JSON if it's wrapped in markdown
            if '```json' in response_text:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    response_text = response_text[json_start:json_end]
            
            market_analysis = json.loads(response_text)
        except Exception as e:
            logger.error(f"AI market analysis failed: {str(e)}")
            market_analysis = {
                'market_type': 'balanced',
                'trends': 'stable',
                'dom_estimate': 60,
                'seasonal_factors': 'normal',
                'outlook': 'stable'
            }
        
        return market_analysis
    
    def _calculate_investment_grade(self, deal_score: float) -> str:
        """Convert deal score to letter grade"""
        if deal_score >= 90: return "A+"
        elif deal_score >= 85: return "A"
        elif deal_score >= 80: return "B+"
        elif deal_score >= 75: return "B"
        elif deal_score >= 70: return "C+"
        elif deal_score >= 65: return "C"
        else: return "D"
    
    def _identify_value_drivers(self, property_data: PropertyFeatures, sales_analysis: Dict) -> List[str]:
        """
        Identify key factors driving property value
        """
        drivers = []
        
        # Size factors
        if property_data.gla > 2000:
            drivers.append("Above-average living space")
        
        # Location factors
        drivers.append("Location in established neighborhood")
        
        # Condition factors
        if property_data.condition in ['excellent', 'good']:
            drivers.append("Well-maintained property condition")
        
        # Market factors
        if sales_analysis['confidence'] in [ConfidenceLevel.HIGH, ConfidenceLevel.VERY_HIGH]:
            drivers.append("Strong comparable sales data")
        
        return drivers
    
    def _identify_risk_factors(self, property_data: PropertyFeatures) -> List[str]:
        """
        Identify potential risk factors
        """
        risks = []
        
        # Property age risks
        if property_data.age > 30:
            risks.append("Older property may require significant maintenance")
        
        # Condition risks
        if property_data.condition in ['fair', 'poor']:
            risks.append("Property condition may require substantial investment")
        
        return risks
    
    def _identify_opportunities(self, property_data: PropertyFeatures, estimated_value: float) -> List[str]:
        """
        Identify investment opportunities
        """
        opportunities = []
        
        if property_data.listing_price and estimated_value > property_data.listing_price * 1.1:
            opportunities.append("Property appears undervalued based on analysis")
        
        if property_data.condition in ['fair', 'poor']:
            opportunities.append("Value-add opportunity through renovations")
        
        if property_data.monthly_rent:
            opportunities.append("Strong rental income potential")
        
        return opportunities
    
    async def _generate_key_insights(self, property_data: PropertyFeatures, estimated_value: float) -> List[str]:
        """
        Generate key investment insights
        """
        insights = []
        
        if property_data.listing_price:
            value_ratio = estimated_value / property_data.listing_price
            if value_ratio > 1.15:
                insights.append(f"Property appears undervalued by {(value_ratio - 1) * 100:.0f}%")
            elif value_ratio < 0.95:
                insights.append(f"Property may be overpriced by {(1 - value_ratio) * 100:.0f}%")
        
        insights.append("Professional 3-approach valuation completed")
        insights.append("Consider detailed property inspection before purchase")
        
        return insights
    
    async def _create_risk_assessment_schema(self, property_data: PropertyFeatures) -> RiskAssessmentSchema:
        """Create risk assessment schema"""
        
        risk_factors = [
            RiskFactor(
                risk_type="property_age",
                level=RiskLevel.MODERATE if property_data.age > 20 else RiskLevel.LOW,
                impact_score=5.0 if property_data.age > 20 else 2.0,
                probability=0.6 if property_data.age > 20 else 0.3,
                description=f"Property is {property_data.age} years old",
                mitigation_strategies=["Regular maintenance", "Property inspection"]
            )
        ]
        
        return RiskAssessmentSchema(
            overall_risk_score=4.0,
            risk_rating=RiskLevel.MODERATE,
            risk_factors=risk_factors,
            risk_categories={
                "market_risk": {"score": 4.0, "level": "moderate"},
                "property_risk": {"score": 3.0, "level": "low"}
            },
            key_concerns=["Property age considerations"]
        )
    
    async def _create_market_analysis_schema(self, property_data: PropertyFeatures) -> MarketAnalysisSchema:
        """Create market analysis schema"""
        
        return MarketAnalysisSchema(
            market_condition=MarketCondition.BALANCED_MARKET,
            market_temperature="Warm",
            price_trends={
                "3_month": 2.0,
                "6_month": 4.5,
                "12_month": 7.2
            },
            inventory_analysis={
                "months_supply": 3.5,
                "new_listings": 125,
                "absorption_rate": 0.6
            },
            competitive_analysis={"competition_level": "moderate"},
            investment_climate={
                "investor_activity": "moderate",
                "cap_rate_avg": 6.5,
                "rental_demand": "strong"
            },
            market_drivers=["Economic growth", "Population increase"],
            future_outlook={
                "6_month": "continued growth",
                "12_month": "stable appreciation"
            }
        )
    
    async def _create_investment_strategy_schema(self, property_data: PropertyFeatures, estimated_value: float) -> InvestmentStrategySchema:
        """Create investment strategy schema"""
        
        # Determine strategy based on property characteristics
        if property_data.monthly_rent and property_data.monthly_rent * 12 / estimated_value > 0.08:
            strategy = InvestmentStrategyType.BUY_AND_HOLD
        elif property_data.condition in ['fair', 'poor']:
            strategy = InvestmentStrategyType.FIX_AND_FLIP
        else:
            strategy = InvestmentStrategyType.BUY_AND_HOLD
        
        cash_flow_proj = CashFlowProjection(
            gross_rental_income=property_data.monthly_rent or estimated_value * 0.01,
            operating_expenses=(property_data.monthly_rent or estimated_value * 0.01) * 0.4,
            debt_service=(property_data.monthly_rent or estimated_value * 0.01) * 0.5,
            net_cash_flow=(property_data.monthly_rent or estimated_value * 0.01) * 0.1,
            expense_breakdown={
                "property_tax": 200,
                "insurance": 100,
                "maintenance": 150,
                "vacancy": 100,
                "management": 100
            }
        )
        
        return InvestmentStrategySchema(
            recommended_strategy=strategy,
            alternative_strategies=[InvestmentStrategyType.BRRRR],
            financial_projections={"cash_flow": cash_flow_proj},
            investment_metrics={
                "cap_rate": 6.5,
                "cash_on_cash_return": 12.0,
                "total_return_annual": 15.0
            },
            execution_plan=[
                {"step": "1", "action": "Secure financing", "timeline": "2-3 weeks"},
                {"step": "2", "action": "Property inspection", "timeline": "1 week"}
            ],
            success_factors=["Market knowledge", "Property management"],
            potential_challenges=["Market volatility", "Maintenance costs"]
        )
    
    async def _create_fallback_analysis(self, property_data: PropertyFeatures) -> PropertyAnalysisSchema:
        """Create fallback analysis when main analysis fails"""
        
        estimated_value = property_data.listing_price or 300000
        
        # Create minimal but valid schemas
        arv_schema = ARVCalculationSchema(
            arv_estimate=estimated_value,
            confidence_score=0.5,
            price_per_sqft=estimated_value / property_data.gla if property_data.gla > 0 else 150,
            valuation_methods={ValuationMethod.COMPARABLE_SALES: estimated_value},
            method_weights={ValuationMethod.COMPARABLE_SALES: 1.0},
            comparable_properties=[],
            key_factors=["Limited data analysis"],
            methodology_notes="Fallback analysis due to data limitations",
            value_range={"conservative": estimated_value * 0.9, "optimistic": estimated_value * 1.1}
        )
        
        return PropertyAnalysisSchema(
            property_address=property_data.address,
            analysis_type="fallback_analysis",
            valuation=arv_schema,
            sell_value_estimate=SellValueEstimationSchema(
                estimated_sell_value=estimated_value,
                quick_sale_value=estimated_value * 0.9,
                optimal_sale_value=estimated_value * 1.1,
                time_to_sell_estimate={"market": 90},
                market_factors={"analysis": "limited"},
                pricing_recommendations=[],
                confidence_level=0.5
            ),
            risk_assessment=await self._create_risk_assessment_schema(property_data),
            market_analysis=await self._create_market_analysis_schema(property_data),
            investment_strategy=await self._create_investment_strategy_schema(property_data, estimated_value),
            deal_score=50.0,
            investment_grade="C",
            confidence_score=0.5,
            key_insights=["Limited analysis due to data constraints"],
            executive_summary="Basic property analysis completed",
            recommendation="Requires additional data for comprehensive analysis"
        )
    
    def _comp_to_dict(self, comp: ComparableSale) -> Dict:
        """Convert comparable sale to dictionary format"""
        return {
            'address': comp.address,
            'sale_price': comp.sale_price,
            'sale_date': comp.sale_date.isoformat(),
            'gla': comp.gla,
            'bedrooms': comp.bedrooms,
            'bathrooms': comp.bathrooms,
            'distance': comp.distance,
            'time_adjusted_price': comp.time_adjusted_price,
            'total_adjustments': comp.total_adjustments,
            'adjusted_price': comp.adjusted_price,
            'weight': comp.weight,
            'adjustments': comp.adjustments or {}
        }
    
    # Legacy method for backward compatibility
    async def quick_analysis(self, address: str, listing_price: float = None) -> Dict[str, Any]:
        """Quick property analysis for backward compatibility"""
        
        # Create basic property features
        property_features = PropertyFeatures(
            address=address,
            gla=1500,  # Default size
            bedrooms=3,
            bathrooms=2.0,
            garage_spaces=2,
            lot_size=7500,
            age=15,
            condition='good',
            property_type='SFR',
            listing_price=listing_price,
            monthly_rent=listing_price * 0.01 if listing_price else 2000
        )
        
        try:
            # Run comprehensive analysis
            analysis = await self.comprehensive_valuation_analysis(property_features)
            
            # Return simplified results for quick analysis
            return {
                "success": True,
                "address": address,
                "deal_score": analysis.deal_score,
                "investment_potential": analysis.investment_grade,
                "arv_estimate": analysis.valuation.arv_estimate,
                "recommended_strategy": analysis.investment_strategy.recommended_strategy.value,
                "monthly_cash_flow": analysis.investment_strategy.financial_projections.get("cash_flow", {}).net_cash_flow if hasattr(analysis.investment_strategy.financial_projections.get("cash_flow", {}), 'net_cash_flow') else 200,
                "key_insight": analysis.key_insights[0] if analysis.key_insights else "Professional valuation completed",
                "confidence_score": analysis.confidence_score
            }
            
        except Exception as e:
            logger.error(f"Quick analysis failed for {address}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "address": address
            }