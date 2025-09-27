"""
Enhanced Analysis Engine Integration Example
===========================================

This file shows how to integrate the new schemas and data sources 
into the analysis_engine.py for better property analysis.
"""

import json
import asyncio
from typing import Dict, Any, Optional
from agents.analysis_schemas import (
    ARVCalculationSchema, SellValueEstimationSchema, RiskAssessmentSchema,
    MarketAnalysisSchema, InvestmentStrategySchema, PropertyAnalysisSchema
)

class EnhancedAnalysisEngine:
    """
    Enhanced Analysis Engine with structured AI responses and real data integration
    """
    
    def __init__(self, api_key: str, attom_bridge_service, deal_finder_agent):
        self.api_key = api_key
        self.attom_bridge = attom_bridge_service
        self.deal_finder = deal_finder_agent
        # ... existing initialization code
        
        # Load enhanced prompts with schemas
        self.schema_prompts = self._load_schema_based_prompts()
    
    def _load_schema_based_prompts(self) -> Dict[str, str]:
        """Load AI prompts that include schema instructions for structured responses"""
        return {
            "arv_calculation": f"""
            You are an expert real estate appraiser. Analyze the provided property data and calculate the After Repair Value (ARV).

            Use the following methodology:
            1. Analyze comparable sales (weight: 40%)
            2. Consider current listing price (weight: 25%) 
            3. Factor in assessed value (weight: 20%)
            4. Include AVM estimates (weight: 15%)
            5. Apply market condition adjustments
            6. Account for property-specific factors

            IMPORTANT: Respond with valid JSON that matches this exact schema:
            {json.dumps(ARVCalculationSchema.model_json_schema(), indent=2)}
            
            Provide your analysis in the JSON format above. Do not include any text outside the JSON response.
            """,
            
            "sell_value_estimation": f"""
            You are a real estate market analyst specializing in property sell value estimations. 
            Analyze the current market conditions and property data to estimate realistic sell values.

            Consider these factors:
            1. Current market temperature (hot/cold)
            2. Days on market trends in the area
            3. Seasonal pricing patterns
            4. Property condition and appeal
            5. Comparable recent sales
            6. Market inventory levels

            IMPORTANT: Respond with valid JSON that matches this exact schema:
            {json.dumps(SellValueEstimationSchema.model_json_schema(), indent=2)}
            
            Provide your analysis in the JSON format above.
            """,
            
            "risk_assessment": f"""
            You are a real estate investment risk analyst. Evaluate all potential risks for this investment property.
            
            Analyze these risk categories:
            1. Market risks (volatility, supply/demand, economic factors)
            2. Property risks (condition, location, structural issues)  
            3. Financial risks (leverage, cash flow, interest rates)
            4. Regulatory risks (zoning, taxes, rent control)
            5. Management risks (tenant quality, maintenance, vacancy)

            IMPORTANT: Respond with valid JSON that matches this exact schema:
            {json.dumps(RiskAssessmentSchema.model_json_schema(), indent=2)}
            
            Rate each risk factor and provide mitigation strategies.
            """,
            
            "market_analysis": f"""
            You are a real estate market researcher. Provide comprehensive market analysis for the property location.
            
            Analyze:
            1. Current market conditions (buyer's vs seller's market)
            2. Price trends and momentum
            3. Inventory levels and absorption rates
            4. Investment climate and cap rates
            5. Economic drivers and future outlook
            6. Competitive factors

            IMPORTANT: Respond with valid JSON that matches this exact schema:
            {json.dumps(MarketAnalysisSchema.model_json_schema(), indent=2)}
            
            Provide detailed market insights in the JSON format above.
            """,
            
            "investment_strategy": f"""
            You are a real estate investment strategist. Recommend the optimal investment strategy for this property.
            
            Evaluate these strategies:
            1. Buy & Hold (rental income focus)
            2. Fix & Flip (renovation and quick sale)
            3. BRRRR (Buy, Rehab, Rent, Refinance, Repeat)
            4. Wholesale (quick assignment of contract)
            5. Live-in Flip (owner-occupied renovation)

            IMPORTANT: Respond with valid JSON that matches this exact schema:
            {json.dumps(InvestmentStrategySchema.model_json_schema(), indent=2)}
            
            Include financial projections and execution plan.
            """
        }

    async def enhanced_property_analysis(self, address: str) -> Dict[str, Any]:
        """
        Comprehensive property analysis using structured AI responses and real data
        """
        try:
            # Step 1: Get property data from ATTOM bridge
            property_data = await self._get_enhanced_property_data(address)
            
            # Step 2: Get deal finder insights (if property is in monitoring)
            deal_insights = await self._get_deal_finder_insights(address)
            
            # Step 3: Run parallel AI analysis with structured schemas
            arv_task = self._calculate_arv_with_schema(property_data)
            sell_value_task = self._estimate_sell_value_with_schema(property_data)
            risk_task = self._assess_risks_with_schema(property_data)
            market_task = self._analyze_market_with_schema(property_data)
            strategy_task = self._recommend_strategy_with_schema(property_data)
            
            # Execute all analyses in parallel
            arv_result, sell_value, risk_assessment, market_analysis, investment_strategy = await asyncio.gather(
                arv_task, sell_value_task, risk_task, market_task, strategy_task
            )
            
            # Step 4: Calculate overall deal score
            deal_score = self._calculate_enhanced_deal_score(
                arv_result, sell_value, risk_assessment, market_analysis
            )
            
            # Step 5: Generate key insights
            insights = await self._generate_key_insights(
                property_data, arv_result, risk_assessment, market_analysis
            )
            
            # Step 6: Create comprehensive analysis result
            analysis_result = PropertyAnalysisSchema(
                property_address=address,
                analysis_type="comprehensive",
                valuation=arv_result,
                sell_value_estimate=sell_value,
                risk_assessment=risk_assessment,
                market_analysis=market_analysis,
                investment_strategy=investment_strategy,
                deal_score=deal_score,
                investment_grade=self._calculate_investment_grade(deal_score),
                confidence_score=self._calculate_confidence_score(property_data),
                key_insights=insights['key_insights'],
                red_flags=insights['red_flags'],
                opportunities=insights['opportunities'],
                executive_summary=insights['executive_summary'],
                recommendation=insights['recommendation']
            )
            
            return {
                "success": True,
                "analysis": analysis_result.dict(),
                "data_sources": {
                    "attom_api": bool(self.attom_bridge),
                    "deal_finder": bool(deal_insights),
                    "ai_model": "gemini-1.5-pro"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "address": address
            }
    
    async def _get_enhanced_property_data(self, address: str) -> Dict[str, Any]:
        """Get comprehensive property data from ATTOM bridge with fallbacks"""
        if not self.attom_bridge:
            return await self._get_mock_property_data(address)
        
        try:
            # Get basic property details
            property_response = await self.attom_bridge.get_property_details(address)
            
            # Get valuation data with comps
            valuation_request = {
                'address': address,
                'comp_radius_miles': 1.0,
                'max_comps': 5
            }
            valuation_response = await self.attom_bridge.get_property_valuation(valuation_request)
            
            # Get market data for the area
            city = property_response.property_data.get('city', '')
            state = property_response.property_data.get('state', '')
            market_request = {'city': city, 'state': state}
            market_response = await self.attom_bridge.get_market_analysis(market_request)
            
            return {
                'property_details': property_response.property_data,
                'valuation_data': valuation_response,
                'market_data': market_response,
                'data_quality': 'high'
            }
            
        except Exception as e:
            # Fallback to mock data if ATTOM fails
            return await self._get_mock_property_data(address)
    
    async def _get_deal_finder_insights(self, address: str) -> Optional[Dict[str, Any]]:
        """Get insights from Deal Finder agent if property is being monitored"""
        if not self.deal_finder:
            return None
        
        try:
            # Check if property is in Deal Finder's monitored properties
            alerts = await self.deal_finder.get_property_alerts(address)
            
            if alerts:
                return {
                    'alerts': alerts,
                    'monitoring_status': 'active',
                    'deal_finder_score': alerts[0].confidence_score if alerts else None
                }
            
            return None
            
        except Exception as e:
            return None
    
    async def _calculate_arv_with_schema(self, property_data: Dict) -> ARVCalculationSchema:
        """Calculate ARV using AI with structured schema response"""
        
        context = self._build_arv_context(property_data)
        prompt = f"{self.schema_prompts['arv_calculation']}\\n\\nProperty Data:\\n{context}"
        
        try:
            response = await self.model.generate_content_async(prompt)
            result_json = self._extract_json_from_response(response.text)
            
            # Validate response against schema
            arv_result = ARVCalculationSchema.parse_obj(result_json)
            return arv_result
            
        except Exception as e:
            # Fallback calculation
            return await self._fallback_arv_calculation(property_data)
    
    async def _estimate_sell_value_with_schema(self, property_data: Dict) -> SellValueEstimationSchema:
        """Estimate current sell value using AI with structured response"""
        
        context = self._build_market_context(property_data)
        prompt = f"{self.schema_prompts['sell_value_estimation']}\\n\\nMarket Context:\\n{context}"
        
        try:
            response = await self.model.generate_content_async(prompt)
            result_json = self._extract_json_from_response(response.text)
            
            sell_value_result = SellValueEstimationSchema.parse_obj(result_json)
            return sell_value_result
            
        except Exception as e:
            # Fallback estimation
            return await self._fallback_sell_value_estimation(property_data)

    def _calculate_enhanced_deal_score(self, arv_result, sell_value, risk_assessment, market_analysis) -> float:
        """Calculate deal score using multiple analysis components"""
        
        # Weight different factors
        weights = {
            'value_opportunity': 0.30,  # ARV vs current price
            'market_conditions': 0.25,  # Market strength
            'risk_level': 0.25,        # Risk assessment
            'liquidity': 0.20          # How easily can we sell
        }
        
        # Calculate component scores
        value_score = min(100, ((arv_result.arv_estimate / sell_value.estimated_sell_value) - 1) * 100)
        
        market_score = {
            'hot': 85, 'warm': 70, 'cool': 55, 'cold': 40
        }.get(market_analysis.market_temperature.lower(), 50)
        
        risk_score = max(0, 100 - (risk_assessment.overall_risk_score * 10))
        
        liquidity_score = max(0, 100 - (sell_value.time_to_sell_estimate.get('market', 90) - 30))
        
        # Calculate weighted score
        deal_score = (
            value_score * weights['value_opportunity'] +
            market_score * weights['market_conditions'] + 
            risk_score * weights['risk_level'] +
            liquidity_score * weights['liquidity']
        )
        
        return max(0, min(100, deal_score))

    def _calculate_investment_grade(self, deal_score: float) -> str:
        """Convert deal score to letter grade"""
        if deal_score >= 90: return "A+"
        elif deal_score >= 85: return "A"
        elif deal_score >= 80: return "B+"
        elif deal_score >= 75: return "B"
        elif deal_score >= 70: return "C+"
        elif deal_score >= 65: return "C"
        else: return "D"

# Example usage and testing functions would go here...