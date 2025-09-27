"""
Agent 1: Customer-Facing Agent for Real Estate Investment Platform
Handles user interactions, explains analysis in simple terms, provides conversational responses using Gemini Flash
"""

import google.generativeai as genai
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from models.data_models import PropertyAnalysis, QuickAnalysisResponse

logger = logging.getLogger(__name__)


class CustomerAgent:
    """
    Agent 1: Customer-Facing Agent
    Uses Gemini 2.5 Flash for fast, conversational responses
    Explains complex real estate analysis in simple, understandable terms
    """
    
    def __init__(self, api_key: str):
        """Initialize the Customer Agent with Gemini Flash model"""
        self.api_key = api_key
        genai.configure(api_key=api_key)
        
        # Use Gemini Flash for fast conversational responses
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Customer-friendly prompts and templates
        self.explanation_templates = self._load_explanation_templates()
        
        logger.info("Customer Agent initialized with Gemini 2.5 Flash")
    
    def _load_explanation_templates(self) -> Dict[str, str]:
        """Load templates for explaining analysis results to customers"""
        return {
            "deal_score_explanation": """
            You are a friendly real estate investment advisor. Explain this deal score to a potential investor in simple terms.
            
            Deal Score: {score}/100
            Rating: {rating}
            
            Explain what this score means, why it's good or bad, and what the investor should consider.
            Keep it conversational and easy to understand.
            """,
            
            "investment_strategy_explanation": """
            You are helping an investor understand the best strategy for a property investment.
            
            Recommended Strategy: {strategy}
            Property: {address}
            Key Metrics: {metrics}
            
            Explain this investment strategy in simple terms, including:
            1. What this strategy means
            2. Why it's recommended for this property
            3. What steps the investor should take
            4. Potential benefits and considerations
            
            Be encouraging but realistic.
            """,
            
            "risk_explanation": """
            You are explaining investment risks to a real estate investor in a clear, helpful way.
            
            Risk Assessment: {risks}
            
            Explain these risks in simple terms and provide practical advice on how to mitigate them.
            Don't scare the investor, but be honest about potential challenges.
            """,
            
            "market_explanation": """
            You are explaining local real estate market conditions to an investor.
            
            Market Data: {market_data}
            Location: {location}
            
            Explain what these market conditions mean for someone looking to invest in this area.
            Include both opportunities and challenges in easy-to-understand language.
            """
        }
    
    async def handle_general_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Handle general real estate investment questions"""
        
        system_prompt = """
        You are a knowledgeable and friendly real estate investment assistant. 
        Help users understand real estate investing concepts, answer their questions, 
        and provide practical guidance. Keep your responses conversational, encouraging, 
        and easy to understand. Use examples when helpful.
        """
        
        # Add context if provided
        context_text = ""
        if context:
            context_text = f"\nContext: {json.dumps(context, indent=2)}"
        
        full_prompt = f"{system_prompt}\n\nUser Question: {query}{context_text}"
        
        try:
            response = await self.model.generate_content_async(full_prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error handling general query: {e}")
            return "I'm sorry, I'm having trouble processing your question right now. Could you please try rephrasing it?"
    
    async def explain_analysis_results(self, analysis_result: Dict[str, Any]) -> str:
        """Explain property analysis results in customer-friendly terms"""
        
        deal_score = analysis_result.get("deal_score", 0)
        investment_potential = analysis_result.get("investment_potential", "Unknown")
        address = analysis_result.get("address", "the property")
        
        prompt = f"""
        You are a real estate investment advisor explaining analysis results to a client.
        
        Property Analysis Results:
        - Address: {address}
        - Deal Score: {deal_score}/100
        - Investment Rating: {investment_potential}
        - ARV Estimate: ${analysis_result.get('arv_estimate', 'N/A'):,}
        - Recommended Strategy: {analysis_result.get('recommended_strategy', 'N/A')}
        - Monthly Cash Flow: ${analysis_result.get('monthly_cash_flow', 0):,.2f}
        - Key Insight: {analysis_result.get('key_insight', 'Analysis completed')}
        
        Explain these results in simple, encouraging terms. Help the client understand:
        1. Whether this is a good investment opportunity
        2. What the numbers mean in practical terms
        3. What their next steps should be
        4. Any important considerations
        
        Be conversational and supportive while being realistic about the investment.
        """
        
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error explaining analysis results: {e}")
            return self._fallback_explanation(analysis_result)
    
    async def explain_deal_score(self, score: float, rating: str) -> str:
        """Explain what a deal score means"""
        
        template = self.explanation_templates["deal_score_explanation"]
        prompt = template.format(score=score, rating=rating)
        
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error explaining deal score: {e}")
            return self._fallback_deal_score_explanation(score, rating)
    
    async def explain_investment_strategy(self, strategy: str, address: str, metrics: Dict[str, Any]) -> str:
        """Explain why a particular investment strategy is recommended"""
        
        template = self.explanation_templates["investment_strategy_explanation"]
        prompt = template.format(
            strategy=strategy,
            address=address,
            metrics=json.dumps(metrics, indent=2)
        )
        
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error explaining investment strategy: {e}")
            return self._fallback_strategy_explanation(strategy)
    
    async def explain_risks(self, risk_assessment: Dict[str, Any]) -> str:
        """Explain investment risks in customer-friendly terms"""
        
        template = self.explanation_templates["risk_explanation"]
        prompt = template.format(risks=json.dumps(risk_assessment, indent=2))
        
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error explaining risks: {e}")
            return "There are some risks to consider with this investment. I'd recommend reviewing the detailed risk assessment and consulting with a real estate professional."
    
    async def explain_market_conditions(self, market_data: Dict[str, Any], location: str) -> str:
        """Explain local market conditions"""
        
        template = self.explanation_templates["market_explanation"]
        prompt = template.format(
            market_data=json.dumps(market_data, indent=2),
            location=location
        )
        
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error explaining market conditions: {e}")
            return f"The market conditions in {location} show mixed signals. I'd recommend getting a more detailed market analysis."
    
    async def provide_next_steps(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Suggest next steps based on analysis results"""
        
        deal_score = analysis_result.get("deal_score", 0)
        investment_potential = analysis_result.get("investment_potential", "Unknown")
        
        prompt = f"""
        Based on this property analysis, suggest 3-5 specific next steps for the investor:
        
        Deal Score: {deal_score}/100
        Investment Rating: {investment_potential}
        Recommended Strategy: {analysis_result.get('recommended_strategy', 'N/A')}
        
        Provide actionable, specific steps they should take next.
        Format as a JSON array of strings: ["step 1", "step 2", ...]
        """
        
        try:
            response = await self.model.generate_content_async(prompt)
            # Extract JSON from response
            import re
            json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
            if json_match:
                steps = json.loads(json_match.group())
                return steps if isinstance(steps, list) else []
        except Exception as e:
            logger.error(f"Error generating next steps: {e}")
        
        # Fallback steps based on deal score
        return self._fallback_next_steps(deal_score, investment_potential)
    
    async def answer_followup_question(self, question: str, analysis_context: Dict[str, Any]) -> str:
        """Answer follow-up questions about a property analysis"""
        
        prompt = f"""
        You are helping an investor understand their property analysis. Answer their follow-up question clearly and helpfully.
        
        Original Analysis Context:
        {json.dumps(analysis_context, indent=2)}
        
        Follow-up Question: {question}
        
        Provide a helpful, specific answer based on the analysis data. If you don't have enough information, 
        suggest what additional data or analysis might be needed.
        """
        
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error answering follow-up question: {e}")
            return "I'd be happy to help with that question, but I'm having trouble accessing the analysis details right now. Could you please be more specific about what you'd like to know?"
    
    # Fallback methods when AI fails
    
    def _fallback_explanation(self, analysis_result: Dict[str, Any]) -> str:
        """Fallback explanation when AI fails"""
        deal_score = analysis_result.get("deal_score", 0)
        investment_potential = analysis_result.get("investment_potential", "Unknown")
        
        if deal_score >= 80:
            return f"This looks like an excellent investment opportunity with a deal score of {deal_score}/100! The analysis suggests this property has strong potential for good returns."
        elif deal_score >= 60:
            return f"This property shows good investment potential with a score of {deal_score}/100. It's worth taking a closer look and maybe getting a professional inspection."
        elif deal_score >= 40:
            return f"This property has moderate potential ({deal_score}/100). You might want to negotiate on price or look for ways to improve the returns."
        else:
            return f"This property scores {deal_score}/100, which suggests it may not be the best investment opportunity. You might want to keep looking for better deals."
    
    def _fallback_deal_score_explanation(self, score: float, rating: str) -> str:
        """Fallback deal score explanation"""
        if score >= 80:
            return f"A score of {score}/100 is excellent! This means the property is likely undervalued and has strong cash flow potential. These are the deals investors dream of finding."
        elif score >= 60:
            return f"A score of {score}/100 is good. This property meets most investment criteria and could be a solid addition to your portfolio with proper due diligence."
        elif score >= 40:
            return f"A score of {score}/100 is fair. The property has some positive aspects but also some concerns. You'd want to negotiate or find ways to improve the returns."
        else:
            return f"A score of {score}/100 suggests this property doesn't meet typical investment criteria. You might want to look for better opportunities."
    
    def _fallback_strategy_explanation(self, strategy: str) -> str:
        """Fallback strategy explanation"""
        strategy_explanations = {
            "buy_and_hold": "Buy and hold means purchasing this property to rent out for steady monthly income and long-term appreciation. It's great for building wealth over time.",
            "flip": "Flipping means buying, renovating, and quickly reselling this property for a profit. It requires more work but can provide faster returns.",
            "brrrr": "BRRRR (Buy, Rehab, Rent, Refinance, Repeat) means improving the property, renting it out, then refinancing to pull your money out and do it again.",
            "wholesale": "Wholesaling means getting this property under contract and selling that contract to another investor for a quick profit without owning the property."
        }
        
        return strategy_explanations.get(strategy, f"The recommended {strategy} strategy could be a good approach for this property.")
    
    def _fallback_next_steps(self, deal_score: float, investment_potential: str) -> List[str]:
        """Fallback next steps based on deal score"""
        
        if deal_score >= 70:
            return [
                "Schedule a property inspection to verify condition",
                "Research the neighborhood and comparable sales",
                "Get pre-approved for financing",
                "Make an offer with appropriate contingencies",
                "Plan your renovation budget if needed"
            ]
        elif deal_score >= 50:
            return [
                "Negotiate a lower purchase price",
                "Get a detailed inspection to identify issues",
                "Research local rental rates more thoroughly",
                "Consider different financing options",
                "Look for ways to increase property value"
            ]
        else:
            return [
                "Keep searching for better deals",
                "Review your investment criteria",
                "Consider different neighborhoods or property types",
                "Build your knowledge of local markets",
                "Network with other investors for deal flow"
            ]
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Customer Agent health status"""
        try:
            test_response = await self.model.generate_content_async("Hello, are you working?")
            response_time = 0.5  # Placeholder for actual timing
            
            return {
                "status": "healthy" if test_response.text else "degraded",
                "model": "gemini-2.5-flash",
                "response_time_ms": int(response_time * 1000),
                "last_check": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "model": "gemini-2.5-flash",
                "last_check": datetime.now().isoformat()
            }