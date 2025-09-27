"""
Agent 2: Analysis Engine for Real Estate Investment Platform
Handles complex property valuations, market analysis, and risk assessments using Gemini 1.5 Pro
"""

import google.generativeai as genai
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import math
import statistics

logger = logging.getLogger(__name__)

class PropertyType(Enum):
    SINGLE_FAMILY = "single_family"
    CONDO = "condo"
    TOWNHOUSE = "townhouse"
    MULTI_FAMILY = "multi_family"
    COMMERCIAL = "commercial"

class InvestmentStrategy(Enum):
    BUY_AND_HOLD = "buy_and_hold"
    FLIP = "flip"
    BRRRR = "brrrr"  # Buy, Rehab, Rent, Refinance, Repeat
    WHOLESALE = "wholesale"

@dataclass
class PropertyData:
    """Core property information structure"""
    address: str
    city: str
    state: str
    zip_code: str
    property_type: PropertyType
    bedrooms: int
    bathrooms: float
    square_feet: int
    lot_size: Optional[float] = None
    year_built: Optional[int] = None
    listing_price: Optional[float] = None
    zestimate: Optional[float] = None
    rent_estimate: Optional[float] = None
    
@dataclass 
class MarketData:
    """Market conditions and trends"""
    median_home_price: float
    price_per_sqft: float
    days_on_market: int
    inventory_months: float
    price_trend_3m: float  # percentage change
    price_trend_6m: float
    price_trend_1y: float
    rental_yield_avg: float
    cap_rate_avg: float

@dataclass
class AnalysisResult:
    """Comprehensive analysis output"""
    property_data: PropertyData
    arv_estimate: float
    deal_score: float  # 0-100 scale
    investment_potential: str  # "Excellent", "Good", "Fair", "Poor"
    recommended_strategy: InvestmentStrategy
    cash_flow_projection: Dict[str, float]
    risk_assessment: Dict[str, Any]
    comparable_properties: List[Dict[str, Any]]
    market_analysis: str
    key_insights: List[str]
    confidence_score: float  # 0-1 scale

class AnalysisEngine:
    """
    Agent 2: Advanced Real Estate Analysis Engine
    Uses Gemini 1.5 Pro for sophisticated property analysis and market evaluation
    """
    
    def __init__(self, api_key: str):
        """Initialize the Analysis Engine with Gemini Pro model"""
        self.api_key = api_key
        genai.configure(api_key=api_key)
        
        # Use Gemini 2.5 Pro for complex analysis tasks
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        
        # Analysis parameters
        self.analysis_prompts = self._load_analysis_prompts()
        self.market_weights = {
            'location_score': 0.25,
            'property_condition': 0.20,
            'market_trends': 0.20,
            'cash_flow_potential': 0.15,
            'appreciation_potential': 0.10,
            'risk_factors': 0.10
        }

        logger.info("Analysis Engine initialized with Gemini 2.5 Pro")

    def _load_analysis_prompts(self) -> Dict[str, str]:
        """Load specialized prompts for different analysis tasks"""
        return {
            "arv_calculation": """
            You are a expert real estate appraiser and investment analyst. Analyze this property data and calculate the After Repair Value (ARV).

            Consider these factors:
            1. Comparable sales in the area (within 0.5 mile radius, sold within 6 months)
            2. Property condition and required repairs
            3. Market trends and neighborhood appreciation
            4. Property-specific factors (lot size, layout, unique features)
            5. Local market conditions and inventory levels

            Provide a detailed ARV calculation with reasoning and confidence level.
            """,
            
            "market_analysis": """
            You are a real estate market analyst. Provide a comprehensive market analysis for this property location.

            Analyze:
            1. Local market trends (price movements, inventory, absorption rates)
            2. Neighborhood dynamics (gentrification, development, demographics)
            3. Economic factors (employment, population growth, infrastructure)
            4. Investment climate (cap rates, rental yields, investor activity)
            5. Future outlook and potential risks/opportunities

            Provide actionable insights for real estate investors.
            """,
            
            "risk_assessment": """
            You are a real estate risk analyst. Evaluate potential risks for this investment property.

            Assess:
            1. Market risks (volatility, oversupply, demand shifts)
            2. Property-specific risks (condition, location, tenant issues)
            3. Financial risks (interest rates, financing challenges, cash flow)
            4. Regulatory risks (zoning changes, rent control, taxes)
            5. Economic risks (recession, job market, demographics)

            Rate each risk category and provide mitigation strategies.
            """,
            
            "investment_strategy": """
            You are a real estate investment strategist. Recommend the optimal investment strategy for this property.

            Consider:
            1. Property characteristics and condition
            2. Local market dynamics
            3. Cash flow vs appreciation potential
            4. Investor profile and goals
            5. Market timing and cycles

            Recommend from: Buy & Hold, Fix & Flip, BRRRR, Wholesale
            Provide detailed reasoning and implementation steps.
            """
        }
    
    async def analyze_property(self, property_data: PropertyData, market_data: MarketData) -> AnalysisResult:
        """
        Comprehensive property analysis using multiple AI-powered evaluations
        """
        logger.info(f"Starting comprehensive analysis for {property_data.address}")
        
        try:
            # Run parallel analysis tasks
            arv_result = await self._calculate_arv(property_data, market_data)
            market_analysis = await self._analyze_market(property_data, market_data)
            risk_assessment = await self._assess_risks(property_data, market_data)
            strategy_recommendation = await self._recommend_strategy(property_data, market_data)
            
            # Calculate deal score
            deal_score = self._calculate_deal_score(property_data, market_data, arv_result)
            
            # Generate cash flow projections
            cash_flow = self._project_cash_flow(property_data, market_data, arv_result)
            
            # Find comparable properties (placeholder for ATTOM integration)
            comparables = await self._find_comparable_properties(property_data)
            
            # Determine investment potential
            investment_potential = self._determine_investment_potential(deal_score)
            
            # Generate key insights
            insights = await self._generate_insights(property_data, market_data, deal_score)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(property_data, market_data)
            
            return AnalysisResult(
                property_data=property_data,
                arv_estimate=arv_result['arv'],
                deal_score=deal_score,
                investment_potential=investment_potential,
                recommended_strategy=InvestmentStrategy(strategy_recommendation['strategy']),
                cash_flow_projection=cash_flow,
                risk_assessment=risk_assessment,
                comparable_properties=comparables,
                market_analysis=market_analysis['analysis'],
                key_insights=insights,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error(f"Analysis failed for {property_data.address}: {e}")
            raise
    
    async def _calculate_arv(self, property_data: PropertyData, market_data: MarketData) -> Dict[str, Any]:
        """Calculate After Repair Value using AI analysis"""
        
        # Prepare data for AI analysis
        analysis_data = {
            "property": {
                "address": property_data.address,
                "type": property_data.property_type.value,
                "bedrooms": property_data.bedrooms,
                "bathrooms": property_data.bathrooms,
                "square_feet": property_data.square_feet,
                "year_built": property_data.year_built,
                "lot_size": property_data.lot_size
            },
            "market": {
                "median_price": market_data.median_home_price,
                "price_per_sqft": market_data.price_per_sqft,
                "days_on_market": market_data.days_on_market,
                "price_trends": {
                    "3_month": market_data.price_trend_3m,
                    "6_month": market_data.price_trend_6m,
                    "1_year": market_data.price_trend_1y
                }
            }
        }
        
        prompt = f"""
        {self.analysis_prompts['arv_calculation']}
        
        Property Data:
        {json.dumps(analysis_data, indent=2)}
        
        Calculate the ARV and provide your analysis in this JSON format:
        {{
            "arv": <estimated_value>,
            "price_per_sqft": <calculated_psf>,
            "analysis_factors": [<list_of_key_factors>],
            "confidence_level": <0.0-1.0>,
            "methodology": "<explanation_of_calculation>",
            "comparable_basis": "<description_of_comps_used>"
        }}
        """
        
        try:
            response = await self.model.generate_content_async(prompt)
            result = self._extract_json_from_response(response.text)
            
            # Fallback calculation if AI fails
            if not result or 'arv' not in result:
                result = self._fallback_arv_calculation(property_data, market_data)
            
            return result
            
        except Exception as e:
            logger.warning(f"AI ARV calculation failed, using fallback: {e}")
            return self._fallback_arv_calculation(property_data, market_data)
    
    async def _analyze_market(self, property_data: PropertyData, market_data: MarketData) -> Dict[str, Any]:
        """Comprehensive market analysis"""
        
        market_context = {
            "location": f"{property_data.city}, {property_data.state}",
            "market_metrics": {
                "median_price": market_data.median_home_price,
                "inventory_months": market_data.inventory_months,
                "days_on_market": market_data.days_on_market,
                "rental_yield": market_data.rental_yield_avg,
                "cap_rate": market_data.cap_rate_avg
            },
            "trends": {
                "3_month_trend": market_data.price_trend_3m,
                "6_month_trend": market_data.price_trend_6m,
                "1_year_trend": market_data.price_trend_1y
            }
        }
        
        prompt = f"""
        {self.analysis_prompts['market_analysis']}
        
        Market Data:
        {json.dumps(market_context, indent=2)}
        
        Provide analysis in JSON format:
        {{
            "analysis": "<comprehensive_market_analysis>",
            "market_score": <1-10_rating>,
            "trend_direction": "<bullish|bearish|neutral>",
            "investment_timing": "<excellent|good|fair|poor>",
            "key_opportunities": [<list_of_opportunities>],
            "market_risks": [<list_of_risks>]
        }}
        """
        
        try:
            response = await self.model.generate_content_async(prompt)
            return self._extract_json_from_response(response.text)
        except Exception as e:
            logger.warning(f"Market analysis failed: {e}")
            return self._fallback_market_analysis(market_data)
    
    async def _assess_risks(self, property_data: PropertyData, market_data: MarketData) -> Dict[str, Any]:
        """Comprehensive risk assessment"""
        
        risk_context = {
            "property": {
                "type": property_data.property_type.value,
                "age": 2024 - (property_data.year_built or 2000),
                "location": f"{property_data.city}, {property_data.state}"
            },
            "market": {
                "volatility_indicator": abs(market_data.price_trend_3m),
                "liquidity_indicator": market_data.days_on_market,
                "supply_indicator": market_data.inventory_months
            }
        }
        
        prompt = f"""
        {self.analysis_prompts['risk_assessment']}
        
        Context:
        {json.dumps(risk_context, indent=2)}
        
        Provide risk assessment in JSON format:
        {{
            "overall_risk_score": <1-10>,
            "risk_categories": {{
                "market_risk": {{"score": <1-10>, "description": "<explanation>"}},
                "property_risk": {{"score": <1-10>, "description": "<explanation>"}},
                "financial_risk": {{"score": <1-10>, "description": "<explanation>"}},
                "regulatory_risk": {{"score": <1-10>, "description": "<explanation>"}}
            }},
            "mitigation_strategies": [<list_of_strategies>],
            "red_flags": [<list_of_concerns>]
        }}
        """
        
        try:
            response = await self.model.generate_content_async(prompt)
            return self._extract_json_from_response(response.text)
        except Exception as e:
            logger.warning(f"Risk assessment failed: {e}")
            return self._fallback_risk_assessment()
    
    async def _recommend_strategy(self, property_data: PropertyData, market_data: MarketData) -> Dict[str, Any]:
        """AI-powered investment strategy recommendation"""
        
        strategy_context = {
            "property_metrics": {
                "price_to_rent_ratio": (property_data.listing_price or market_data.median_home_price) / (property_data.rent_estimate or 2000),
                "cash_flow_potential": property_data.rent_estimate or 2000,
                "appreciation_potential": market_data.price_trend_1y
            },
            "market_conditions": {
                "inventory_level": market_data.inventory_months,
                "market_velocity": market_data.days_on_market,
                "investor_activity": market_data.cap_rate_avg
            }
        }
        
        prompt = f"""
        {self.analysis_prompts['investment_strategy']}
        
        Context:
        {json.dumps(strategy_context, indent=2)}
        
        Recommend strategy in JSON format:
        {{
            "strategy": "<buy_and_hold|flip|brrrr|wholesale>",
            "reasoning": "<detailed_explanation>",
            "expected_returns": {{
                "annual_cash_flow": <amount>,
                "total_return_estimate": <percentage>,
                "timeframe": "<holding_period>"
            }},
            "implementation_steps": [<list_of_steps>],
            "success_probability": <0.0-1.0>
        }}
        """
        
        try:
            response = await self.model.generate_content_async(prompt)
            return self._extract_json_from_response(response.text)
        except Exception as e:
            logger.warning(f"Strategy recommendation failed: {e}")
            return self._fallback_strategy_recommendation(property_data, market_data)
    
    def _calculate_deal_score(self, property_data: PropertyData, market_data: MarketData, arv_result: Dict) -> float:
        """Calculate overall deal score (0-100)"""
        
        # Price-to-ARV ratio (lower is better)
        current_price = property_data.listing_price or market_data.median_home_price
        arv = arv_result.get('arv', current_price)
        price_ratio_score = min(100, max(0, (1 - current_price / arv) * 100))
        
        # Market conditions score
        market_score = self._calculate_market_score(market_data)
        
        # Cash flow score
        cash_flow_score = self._calculate_cash_flow_score(property_data, market_data)
        
        # Location score (simplified)
        location_score = 75  # Placeholder - would integrate with actual location data
        
        # Weighted average
        deal_score = (
            price_ratio_score * 0.3 +
            market_score * 0.25 +
            cash_flow_score * 0.25 +
            location_score * 0.2
        )
        
        return round(deal_score, 1)
    
    def _calculate_market_score(self, market_data: MarketData) -> float:
        """Calculate market conditions score"""
        
        # Positive trend indicators
        trend_score = (market_data.price_trend_1y + 5) / 10 * 50  # -5% to +5% mapped to 0-50
        
        # Inventory levels (3-6 months is ideal)
        inventory_score = 100 - abs(market_data.inventory_months - 4.5) * 10
        
        # Days on market (lower is better, 30 days is ideal)
        dom_score = max(0, 100 - (market_data.days_on_market - 30) * 2)
        
        return max(0, min(100, (trend_score + inventory_score + dom_score) / 3))
    
    def _calculate_cash_flow_score(self, property_data: PropertyData, market_data: MarketData) -> float:
        """Calculate cash flow potential score"""
        
        if not property_data.rent_estimate:
            return 50  # Neutral score if no rent data
        
        estimated_expenses = property_data.rent_estimate * 0.5  # 50% rule
        net_cash_flow = property_data.rent_estimate - estimated_expenses
        
        # Score based on cash flow as percentage of property value
        property_value = property_data.listing_price or market_data.median_home_price
        cash_flow_yield = (net_cash_flow * 12) / property_value * 100
        
        # 1% rule: 1% of property value in monthly rent = 100 score
        return min(100, cash_flow_yield * 100)
    
    def _project_cash_flow(self, property_data: PropertyData, market_data: MarketData, arv_result: Dict) -> Dict[str, float]:
        """Project cash flow over different time periods"""
        
        monthly_rent = property_data.rent_estimate or market_data.median_home_price * 0.01
        
        # Estimate expenses (using 50% rule as starting point)
        monthly_expenses = monthly_rent * 0.5
        monthly_cash_flow = monthly_rent - monthly_expenses
        
        return {
            "monthly_cash_flow": round(monthly_cash_flow, 2),
            "annual_cash_flow": round(monthly_cash_flow * 12, 2),
            "5_year_projection": round(monthly_cash_flow * 12 * 5 * (1 + market_data.price_trend_1y/100), 2),
            "cash_on_cash_return": round((monthly_cash_flow * 12) / (property_data.listing_price or market_data.median_home_price * 0.2) * 100, 2)
        }
    
    async def _find_comparable_properties(self, property_data: PropertyData) -> List[Dict[str, Any]]:
        """Find comparable properties (placeholder for ATTOM integration)"""
        
        # This will be replaced with actual ATTOM API calls
        return [
            {
                "address": "Similar Property 1",
                "distance": 0.3,
                "price": property_data.listing_price or 300000 * 0.95,
                "price_per_sqft": 150,
                "days_on_market": 25,
                "similarity_score": 0.85
            },
            {
                "address": "Similar Property 2", 
                "distance": 0.5,
                "price": property_data.listing_price or 300000 * 1.05,
                "price_per_sqft": 165,
                "days_on_market": 35,
                "similarity_score": 0.78
            }
        ]
    
    def _determine_investment_potential(self, deal_score: float) -> str:
        """Determine investment potential based on deal score"""
        
        if deal_score >= 80:
            return "Excellent"
        elif deal_score >= 65:
            return "Good"
        elif deal_score >= 45:
            return "Fair"
        else:
            return "Poor"
    
    async def _generate_insights(self, property_data: PropertyData, market_data: MarketData, deal_score: float) -> List[str]:
        """Generate key insights using AI"""
        
        insights_prompt = f"""
        Based on this real estate analysis, provide 3-5 key actionable insights for an investor:
        
        Property: {property_data.address}
        Deal Score: {deal_score}/100
        Market Trend: {market_data.price_trend_1y}% (1-year)
        Days on Market: {market_data.days_on_market}
        
        Format as a JSON array of strings: ["insight 1", "insight 2", ...]
        """
        
        try:
            response = await self.model.generate_content_async(insights_prompt)
            insights = self._extract_json_from_response(response.text)
            return insights if isinstance(insights, list) else []
        except Exception as e:
            logger.warning(f"Insights generation failed: {e}")
            return self._fallback_insights(deal_score)
    
    def _calculate_confidence_score(self, property_data: PropertyData, market_data: MarketData) -> float:
        """Calculate confidence in the analysis"""
        
        # Data completeness score
        data_fields = [
            property_data.listing_price,
            property_data.rent_estimate,
            property_data.year_built,
            property_data.lot_size
        ]
        data_completeness = sum(1 for field in data_fields if field is not None) / len(data_fields)
        
        # Market data reliability (based on days on market and inventory)
        market_reliability = min(1.0, (60 - market_data.days_on_market) / 60 + 0.5)
        
        return round((data_completeness * 0.6 + market_reliability * 0.4), 2)
    
    # Fallback methods for when AI analysis fails
    
    def _fallback_arv_calculation(self, property_data: PropertyData, market_data: MarketData) -> Dict[str, Any]:
        """Fallback ARV calculation using basic formulas"""
        
        base_value = property_data.square_feet * market_data.price_per_sqft
        
        # Adjust for property age
        age_factor = 1.0
        if property_data.year_built:
            age = 2024 - property_data.year_built
            age_factor = max(0.8, 1.0 - (age / 100))
        
        arv = base_value * age_factor
        
        return {
            "arv": round(arv, 0),
            "price_per_sqft": round(arv / property_data.square_feet, 0),
            "analysis_factors": ["Square footage", "Market price per sqft", "Property age"],
            "confidence_level": 0.7,
            "methodology": "Basic calculation using square footage and market price per sqft",
            "comparable_basis": "Local market price per square foot averages"
        }
    
    def _fallback_market_analysis(self, market_data: MarketData) -> Dict[str, Any]:
        """Fallback market analysis"""
        
        trend_direction = "neutral"
        if market_data.price_trend_1y > 2:
            trend_direction = "bullish"
        elif market_data.price_trend_1y < -2:
            trend_direction = "bearish"
        
        return {
            "analysis": f"Market showing {trend_direction} trends with {market_data.inventory_months} months of inventory.",
            "market_score": 6,
            "trend_direction": trend_direction,
            "investment_timing": "fair",
            "key_opportunities": ["Stable market conditions"],
            "market_risks": ["Market volatility"]
        }
    
    def _fallback_risk_assessment(self) -> Dict[str, Any]:
        """Fallback risk assessment"""
        
        return {
            "overall_risk_score": 5,
            "risk_categories": {
                "market_risk": {"score": 5, "description": "Moderate market risk"},
                "property_risk": {"score": 5, "description": "Average property risk"},
                "financial_risk": {"score": 5, "description": "Standard financing risks"},
                "regulatory_risk": {"score": 4, "description": "Low regulatory risk"}
            },
            "mitigation_strategies": ["Diversify investments", "Maintain cash reserves"],
            "red_flags": []
        }
    
    def _fallback_strategy_recommendation(self, property_data: PropertyData, market_data: MarketData) -> Dict[str, Any]:
        """Fallback strategy recommendation"""
        
        # Simple logic based on rent-to-price ratio
        if property_data.rent_estimate and property_data.listing_price:
            monthly_yield = (property_data.rent_estimate / property_data.listing_price) * 100
            strategy = "buy_and_hold" if monthly_yield > 1.0 else "flip"
        else:
            strategy = "buy_and_hold"
        
        return {
            "strategy": strategy,
            "reasoning": "Based on basic rent-to-price analysis",
            "expected_returns": {
                "annual_cash_flow": property_data.rent_estimate * 6 if property_data.rent_estimate else 12000,
                "total_return_estimate": 8.0,
                "timeframe": "5-10 years"
            },
            "implementation_steps": ["Analyze financing options", "Conduct property inspection"],
            "success_probability": 0.7
        }
    
    def _fallback_insights(self, deal_score: float) -> List[str]:
        """Generate fallback insights"""
        
        insights = []
        
        if deal_score >= 70:
            insights.append("This property shows strong investment potential")
        elif deal_score >= 50:
            insights.append("Property requires careful analysis but shows moderate potential")
        else:
            insights.append("Consider alternative properties with better metrics")
        
        insights.extend([
            "Verify all property data through on-site inspection",
            "Research local market trends and upcoming developments",
            "Consider multiple financing options to optimize returns"
        ])
        
        return insights
    
    def _extract_json_from_response(self, response_text: str) -> Any:
        """Extract JSON from AI response text"""
        
        try:
            # Look for JSON blocks in the response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                return None
                
        except (json.JSONDecodeError, AttributeError) as e:
            logger.warning(f"Failed to extract JSON from response: {e}")
            return None

    async def quick_analysis(self, address: str, listing_price: float = None) -> Dict[str, Any]:
        """Quick analysis endpoint for basic property evaluation"""
        
        # This would typically fetch data from ATTOM API
        # For now, using placeholder data
        property_data = PropertyData(
            address=address,
            city="Sample City",
            state="VA",
            zip_code="24060",
            property_type=PropertyType.SINGLE_FAMILY,
            bedrooms=3,
            bathrooms=2.0,
            square_feet=1500,
            listing_price=listing_price
        )
        
        market_data = MarketData(
            median_home_price=350000,
            price_per_sqft=200,
            days_on_market=45,
            inventory_months=3.2,
            price_trend_3m=1.5,
            price_trend_6m=3.2,
            price_trend_1y=5.8,
            rental_yield_avg=6.5,
            cap_rate_avg=5.2
        )
        
        full_analysis = await self.analyze_property(property_data, market_data)
        
        # Return simplified results for quick analysis
        return {
            "address": address,
            "deal_score": full_analysis.deal_score,
            "investment_potential": full_analysis.investment_potential,
            "arv_estimate": full_analysis.arv_estimate,
            "recommended_strategy": full_analysis.recommended_strategy.value,
            "monthly_cash_flow": full_analysis.cash_flow_projection["monthly_cash_flow"],
            "key_insight": full_analysis.key_insights[0] if full_analysis.key_insights else "Analysis completed"
        }