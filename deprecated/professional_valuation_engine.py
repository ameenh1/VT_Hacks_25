"""
Professional Real Estate Valuation Engine
==========================================

Implements industry-standard real estate appraisal methodology using three approaches:
1. Sales Comparison Approach (Market Data)
2. Income Approach (Capitalization & GRM)  
3. Cost Approach (Replacement Cost Less Depreciation)

Integrates with Deal Finder for data sourcing and provides professional-grade analysis.
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
    
    
class ProfessionalValuationSchema(BaseModel):
    """Complete professional valuation analysis schema"""
    
    # Property identification
    property_address: str = Field(..., description="Subject property address")
    analysis_date: datetime = Field(..., description="Date of analysis")
    valuation_date: datetime = Field(..., description="Effective date of valuation")
    
    # Sales Comparison Approach
    comparable_sales: List[Dict] = Field(..., description="Comparable sales analyzed")
    sales_approach_indicators: Dict[str, Any] = Field(..., description="Sales approach calculations")
    sales_approach_value: float = Field(..., description="Value indication from sales comparison")
    sales_approach_confidence: ConfidenceLevel = Field(..., description="Confidence in sales approach")
    
    # Income Approach  
    income_analysis: Dict[str, Any] = Field(..., description="Income approach calculations")
    income_approach_value: float = Field(..., description="Value indication from income approach")
    income_approach_confidence: ConfidenceLevel = Field(..., description="Confidence in income approach")
    
    # Cost Approach
    cost_analysis: Dict[str, Any] = Field(..., description="Cost approach calculations")
    cost_approach_value: float = Field(..., description="Value indication from cost approach")
    cost_approach_confidence: ConfidenceLevel = Field(..., description="Confidence in cost approach")
    
    # Final Reconciliation
    approach_weights: Dict[ValuationApproach, float] = Field(..., description="Weight given to each approach")
    final_value_estimate: float = Field(..., description="Final reconciled value")
    value_range: Dict[str, float] = Field(..., description="Conservative to optimistic range")
    overall_confidence: ConfidenceLevel = Field(..., description="Overall confidence level")
    
    # Professional Analysis
    market_conditions: Dict[str, Any] = Field(..., description="Current market condition analysis")
    key_value_drivers: List[str] = Field(..., description="Primary factors affecting value")
    risk_factors: List[str] = Field(..., description="Identified risk factors")
    assumptions_and_limitations: List[str] = Field(..., description="Key assumptions made")
    
    # Investment Analysis
    deal_score: float = Field(..., ge=0, le=100, description="Investment deal score")
    investment_strategy: str = Field(..., description="Recommended investment strategy")
    expected_returns: Dict[str, float] = Field(..., description="Projected investment returns")
    

class ProfessionalValuationEngine:
    """
    Professional-grade real estate valuation engine implementing industry standards
    """
    
    def __init__(self, gemini_api_key: str, deal_finder=None):
        """Initialize the professional valuation engine"""
        self.api_key = gemini_api_key
        self.deal_finder = deal_finder
        genai.configure(api_key=gemini_api_key)
        
        # Use Gemini 1.5 Pro for complex analysis
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Default adjustment rates (will be dynamically updated)
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
        
    async def analyze_property_batch(self, properties: List[PropertyFeatures], 
                                   user_criteria: Dict = None) -> List[ProfessionalValuationSchema]:
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
                                             user_criteria: Dict = None) -> ProfessionalValuationSchema:
        """
        Complete professional valuation analysis using all three approaches
        """
        
        # Phase 1.2: Request comparable sales through Deal Finder
        comparable_sales = await self._request_comparable_sales(property_data)
        
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
    
    async def _request_comparable_sales(self, property_data: PropertyFeatures) -> List[ComparableSale]:
        """
        Phase 1.2: Request comparable sales through Deal Finder
        """
        if not self.deal_finder:
            # Return mock data for testing
            return self._generate_mock_comparables(property_data)
        
        # Request comps from Deal Finder with specific criteria
        comp_criteria = {
            'center_address': property_data.address,
            'radius_miles': 1.0,
            'max_months_back': 6,
            'property_type': property_data.property_type,
            'gla_range': (int(property_data.gla * 0.75), int(property_data.gla * 1.25)),
            'max_results': 10
        }
        
        # This would call Deal Finder's comparable search
        # comparable_data = await self.deal_finder.search_comparable_sales(comp_criteria)
        
        # For now, return mock data
        return self._generate_mock_comparables(property_data)
    
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
        # This would request data from Deal Finder
        # For now, return typical cap rates by property type
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
        # This would request data from Deal Finder
        # For now, return typical GRM values
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
        # This would request data from Deal Finder
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
        # This would request data from Deal Finder for land sales
        # Default land values per square foot
        default_land_values = 15.0  # $15/sq ft
        
        return property_data.lot_size * default_land_values
    
    async def _ai_enhanced_reconciliation(self, property_data: PropertyFeatures,
                                        sales_analysis: Dict, income_analysis: Dict,
                                        cost_analysis: Dict, user_criteria: Dict = None) -> ProfessionalValuationSchema:
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
        
        # Phase 4.4: Investment analysis for Deal Finder
        investment_metrics = await self._calculate_investment_metrics(
            property_data, final_value, user_criteria
        )
        
        # Phase 4.2: AI-powered market analysis
        market_analysis = await self._ai_market_analysis(property_data, final_value)
        
        # Create comprehensive analysis schema
        analysis = ProfessionalValuationSchema(
            property_address=property_data.address,
            analysis_date=datetime.now(),
            valuation_date=datetime.now(),
            
            # Sales Comparison Results
            comparable_sales=sales_analysis['comparable_sales'],
            sales_approach_indicators=sales_analysis,
            sales_approach_value=sales_analysis['weighted_value'],
            sales_approach_confidence=sales_analysis['confidence'],
            
            # Income Approach Results
            income_analysis=income_analysis,
            income_approach_value=income_analysis['value'],
            income_approach_confidence=income_analysis['confidence'],
            
            # Cost Approach Results
            cost_analysis=cost_analysis,
            cost_approach_value=cost_analysis['value'],
            cost_approach_confidence=cost_analysis['confidence'],
            
            # Final Reconciliation
            approach_weights=approach_weights,
            final_value_estimate=final_value,
            value_range={
                'conservative': final_value * 0.92,
                'optimistic': final_value * 1.08
            },
            overall_confidence=self._determine_overall_confidence(sales_analysis, income_analysis, cost_analysis),
            
            # Professional Analysis
            market_conditions=market_analysis,
            key_value_drivers=self._identify_value_drivers(property_data, sales_analysis),
            risk_factors=self._identify_risk_factors(property_data, market_analysis),
            assumptions_and_limitations=self._generate_assumptions(),
            
            # Investment Analysis
            deal_score=investment_metrics['deal_score'],
            investment_strategy=investment_metrics['strategy'],
            expected_returns=investment_metrics['returns']
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
            ValuationApproach.SALES_COMPARISON: 0.75,
            ValuationApproach.INCOME_APPROACH: 0.15,
            ValuationApproach.COST_APPROACH: 0.10
        }
        
        # Adjust based on data quality and applicability
        if sales_analysis['confidence'] == ConfidenceLevel.LOW:
            weights[ValuationApproach.SALES_COMPARISON] = 0.50
            weights[ValuationApproach.INCOME_APPROACH] = 0.30
            weights[ValuationApproach.COST_APPROACH] = 0.20
        
        if income_analysis['applicable'] and property_data.monthly_rent:
            weights[ValuationApproach.INCOME_APPROACH] = 0.25
            weights[ValuationApproach.SALES_COMPARISON] = 0.65
            weights[ValuationApproach.COST_APPROACH] = 0.10
        
        # For new construction, give more weight to cost approach
        if property_data.age < 5:
            weights[ValuationApproach.COST_APPROACH] = 0.20
            weights[ValuationApproach.SALES_COMPARISON] = 0.65
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
        elif property_data.condition in ['fair', 'poor']:
            strategy = "Fix and Flip - Value Add Opportunity"
        else:
            strategy = "Buy and Hold - Appreciation Focus"
        
        # Calculate returns
        if property_data.monthly_rent:
            annual_rent = property_data.monthly_rent * 12
            gross_yield = annual_rent / estimated_value
            net_yield = gross_yield * 0.65  # After expenses
        else:
            gross_yield = 0.0
            net_yield = 0.0
        
        return {
            'deal_score': deal_score,
            'strategy': strategy,
            'returns': {
                'gross_yield': gross_yield,
                'net_yield': net_yield,
                'value_ratio': property_data.listing_price and estimated_value / property_data.listing_price or 1.0
            }
        }
    
    async def _ai_market_analysis(self, property_data: PropertyFeatures, estimated_value: float) -> Dict[str, Any]:
        """
        Phase 4.2: AI-Powered Market Analysis
        """
        
        prompt = f"""
        As a professional real estate analyst, analyze the current market conditions for this property:
        
        Property: {property_data.address}
        Property Type: {property_data.property_type}
        Estimated Value: ${estimated_value:,.0f}
        
        Provide analysis on:
        1. Current market conditions (buyer's vs seller's market)
        2. Price trends in the area
        3. Days on market expectations
        4. Seasonal factors
        5. Market outlook (next 6-12 months)
        
        Format as JSON with keys: market_type, trends, dom_estimate, seasonal_factors, outlook
        """
        
        try:
            response = await self.model.generate_content_async(prompt)
            market_analysis = json.loads(response.text)
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
    
    def _identify_risk_factors(self, property_data: PropertyFeatures, market_analysis: Dict) -> List[str]:
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
        
        # Market risks
        if market_analysis.get('market_type') == 'buyer_market':
            risks.append("Buyer's market conditions may limit appreciation")
        
        return risks
    
    def _generate_assumptions(self) -> List[str]:
        """
        Generate key assumptions and limitations
        """
        return [
            "Analysis assumes continued market stability",
            "Property condition assessment based on available data",
            "Rental estimates based on market averages",
            "Analysis current as of valuation date only",
            "Subject to verification of all property data"
        ]
    
    def _determine_overall_confidence(self, sales_analysis: Dict, income_analysis: Dict, 
                                    cost_analysis: Dict) -> ConfidenceLevel:
        """
        Determine overall confidence level
        """
        confidence_scores = {
            ConfidenceLevel.LOW: 1,
            ConfidenceLevel.MODERATE: 2,
            ConfidenceLevel.HIGH: 3,
            ConfidenceLevel.VERY_HIGH: 4
        }
        
        scores = [
            confidence_scores[sales_analysis['confidence']],
            confidence_scores[income_analysis['confidence']],
            confidence_scores[cost_analysis['confidence']]
        ]
        
        avg_score = statistics.mean(scores)
        
        if avg_score >= 3.5:
            return ConfidenceLevel.VERY_HIGH
        elif avg_score >= 2.5:
            return ConfidenceLevel.HIGH
        elif avg_score >= 1.5:
            return ConfidenceLevel.MODERATE
        else:
            return ConfidenceLevel.LOW
    
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
            'adjustments': getattr(comp, 'adjustments', {})
        }
    
    def _generate_mock_comparables(self, property_data: PropertyFeatures) -> List[ComparableSale]:
        """Generate mock comparable sales for testing"""
        base_price = 300000
        comps = []
        
        for i in range(5):
            comp = ComparableSale(
                address=f"{1000 + i * 100} Main St",
                sale_price=base_price + (i - 2) * 20000,
                sale_date=datetime.now() - timedelta(days=30 + i * 20),
                gla=property_data.gla + (i - 2) * 100,
                bedrooms=property_data.bedrooms + (1 if i > 2 else 0),
                bathrooms=property_data.bathrooms,
                garage_spaces=property_data.garage_spaces,
                lot_size=property_data.lot_size + (i - 2) * 1000,
                distance=0.3 + i * 0.1,
                condition='good',
                age=property_data.age + (i - 2) * 2
            )
            comps.append(comp)
        
        return comps