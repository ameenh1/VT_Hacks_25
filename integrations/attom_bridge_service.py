"""
ATTOM Bridge Service for Real Estate AI Platform
===============================================

This service provides a clean, async interface between the AI agents and the ATTOM Data API.
It wraps the existing attom_housing_data.py functionality with agent-optimized endpoints.
"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
import logging
import asyncio
import httpx
from enum import Enum
import os
from dataclasses import asdict

# Import the existing ATTOM client
from integrations.attom_housing_data import AttomDataClient, PropertyData, HousingDataAnalyzer

logger = logging.getLogger(__name__)

class PropertySearchCriteria(BaseModel):
    """Search criteria for property lookup"""
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_bedrooms: Optional[int] = None
    max_bedrooms: Optional[int] = None
    min_bathrooms: Optional[float] = None
    max_bathrooms: Optional[float] = None
    property_type: Optional[str] = None
    max_results: int = Field(default=10, le=50)

class PropertyValuationRequest(BaseModel):
    """Request model for property valuation"""
    address: str
    include_comps: bool = True
    comp_radius_miles: float = Field(default=1.0, le=5.0)
    max_comps: int = Field(default=5, le=10)

class MarketAnalysisRequest(BaseModel):
    """Request model for market analysis"""
    city: str
    state: str
    property_type: Optional[str] = None
    time_period_months: int = Field(default=12, le=24)

class PropertyResponse(BaseModel):
    """Response model for property data"""
    success: bool
    property_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class PropertyListResponse(BaseModel):
    """Response model for property search results"""
    success: bool
    properties: List[Dict[str, Any]] = []
    total_found: int = 0
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class ValuationResponse(BaseModel):
    """Response model for property valuation"""
    success: bool
    property_address: str
    estimated_value: Optional[float] = None
    value_range_low: Optional[float] = None
    value_range_high: Optional[float] = None
    comparable_properties: List[Dict[str, Any]] = []
    confidence_score: Optional[float] = None
    valuation_date: datetime = Field(default_factory=datetime.now)
    error_message: Optional[str] = None

class MarketAnalysisResponse(BaseModel):
    """Response model for market analysis"""
    success: bool
    location: str
    median_price: Optional[float] = None
    price_trend_pct: Optional[float] = None
    inventory_months: Optional[float] = None
    days_on_market: Optional[int] = None
    market_temperature: Optional[str] = None  # "hot", "balanced", "cold"
    analysis_period: str
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class ATTOMBridgeService:
    """
    Bridge service between AI agents and ATTOM Data API
    Provides async, agent-optimized access to real estate data
    """
    
    def __init__(self, attom_api_key: str):
        """Initialize the ATTOM bridge service"""
        self.api_key = attom_api_key
        self.client = AttomDataClient(attom_api_key)
        self.analyzer = HousingDataAnalyzer()
        
        # Cache for frequently accessed data
        self.property_cache = {}
        self.market_cache = {}
        self.cache_duration_minutes = 30
        
        logger.info("ATTOM Bridge Service initialized")
    
    async def search_properties(self, criteria: PropertySearchCriteria) -> PropertyListResponse:
        """
        Search for properties based on criteria
        Optimized for Agent 3 (Deal Finder) bulk searches
        """
        try:
            # Convert criteria to search parameters
            search_params = {}
            if criteria.address:
                search_params['address'] = criteria.address
            if criteria.city:
                search_params['city'] = criteria.city
            if criteria.state:
                search_params['state'] = criteria.state
            if criteria.zip_code:
                search_params['zip_code'] = criteria.zip_code
            
            # Use the existing client to search
            properties_data = await self._run_sync_in_async(
                self.client.get_properties_by_criteria, search_params
            )
            
            if not properties_data:
                return PropertyListResponse(
                    success=False,
                    error_message="No properties found matching criteria"
                )
            
            # Filter by price and other criteria
            filtered_properties = []
            for prop in properties_data:
                if self._matches_criteria(prop, criteria):
                    filtered_properties.append(asdict(prop))
            
            return PropertyListResponse(
                success=True,
                properties=filtered_properties[:criteria.max_results],
                total_found=len(filtered_properties)
            )
            
        except Exception as e:
            logger.error(f"Property search failed: {e}")
            return PropertyListResponse(
                success=False,
                error_message=f"Search failed: {str(e)}"
            )
    
    async def get_property_details(self, address: str) -> PropertyResponse:
        """
        Get detailed property information
        Optimized for Agent 2 (Analysis Engine) detailed analysis
        """
        try:
            # Check cache first
            cache_key = f"property_{address}"
            if cache_key in self.property_cache:
                cached_data, timestamp = self.property_cache[cache_key]
                if datetime.now() - timestamp < timedelta(minutes=self.cache_duration_minutes):
                    return PropertyResponse(success=True, property_data=cached_data)
            
            # Fetch property details
            property_data = await self._run_sync_in_async(
                self.client.get_property_by_address, address
            )
            
            if not property_data:
                return PropertyResponse(
                    success=False,
                    error_message=f"No property found at address: {address}"
                )
            
            # Convert to dict and cache
            property_dict = asdict(property_data)
            self.property_cache[cache_key] = (property_dict, datetime.now())
            
            return PropertyResponse(
                success=True,
                property_data=property_dict
            )
            
        except Exception as e:
            logger.error(f"Property details fetch failed: {e}")
            return PropertyResponse(
                success=False,
                error_message=f"Failed to fetch property details: {str(e)}"
            )
    
    async def get_property_valuation(self, request: PropertyValuationRequest) -> ValuationResponse:
        """
        Get property valuation with comparable sales
        Optimized for Agent 2 (Analysis Engine) ARV calculations
        """
        try:
            # Get property details first
            property_response = await self.get_property_details(request.address)
            if not property_response.success:
                return ValuationResponse(
                    success=False,
                    property_address=request.address,
                    error_message=property_response.error_message
                )
            
            property_data = property_response.property_data
            
            # Get comparable sales if requested
            comparable_properties = []
            if request.include_comps:
                comps = await self._get_comparable_sales(
                    request.address,
                    request.comp_radius_miles,
                    request.max_comps
                )
                comparable_properties = comps
            
            # Calculate valuation using analyzer
            estimated_value = await self._calculate_property_value(
                property_data, comparable_properties
            )
            
            # Calculate confidence score based on data quality and comp similarity
            confidence_score = self._calculate_confidence_score(
                property_data, comparable_properties
            )
            
            return ValuationResponse(
                success=True,
                property_address=request.address,
                estimated_value=estimated_value,
                value_range_low=estimated_value * 0.9 if estimated_value else None,
                value_range_high=estimated_value * 1.1 if estimated_value else None,
                comparable_properties=comparable_properties,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error(f"Property valuation failed: {e}")
            return ValuationResponse(
                success=False,
                property_address=request.address,
                error_message=f"Valuation failed: {str(e)}"
            )
    
    async def get_market_analysis(self, request: MarketAnalysisRequest) -> MarketAnalysisResponse:
        """
        Get market analysis for a location
        Optimized for Agent 1 (Customer Agent) market insights
        """
        try:
            # Check cache first
            cache_key = f"market_{request.city}_{request.state}"
            if cache_key in self.market_cache:
                cached_data, timestamp = self.market_cache[cache_key]
                if datetime.now() - timestamp < timedelta(minutes=self.cache_duration_minutes):
                    return cached_data
            
            # Get market data using analyzer
            market_stats = await self._run_sync_in_async(
                self.analyzer.analyze_market_trends,
                request.city,
                request.state,
                request.time_period_months
            )
            
            # Determine market temperature
            market_temp = self._determine_market_temperature(market_stats)
            
            response = MarketAnalysisResponse(
                success=True,
                location=f"{request.city}, {request.state}",
                median_price=market_stats.get('median_price'),
                price_trend_pct=market_stats.get('price_trend_pct'),
                inventory_months=market_stats.get('inventory_months'),
                days_on_market=market_stats.get('avg_days_on_market'),
                market_temperature=market_temp,
                analysis_period=f"{request.time_period_months} months"
            )
            
            # Cache the response
            self.market_cache[cache_key] = (response, datetime.now())
            
            return response
            
        except Exception as e:
            logger.error(f"Market analysis failed: {e}")
            return MarketAnalysisResponse(
                success=False,
                location=f"{request.city}, {request.state}",
                error_message=f"Market analysis failed: {str(e)}"
            )
    
    async def _run_sync_in_async(self, sync_func, *args, **kwargs):
        """Run synchronous function in async context"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, sync_func, *args, **kwargs)
    
    def _matches_criteria(self, property_data: PropertyData, criteria: PropertySearchCriteria) -> bool:
        """Check if property matches search criteria"""
        if criteria.min_price and property_data.listing_price and property_data.listing_price < criteria.min_price:
            return False
        if criteria.max_price and property_data.listing_price and property_data.listing_price > criteria.max_price:
            return False
        if criteria.min_bedrooms and property_data.bedrooms and property_data.bedrooms < criteria.min_bedrooms:
            return False
        if criteria.max_bedrooms and property_data.bedrooms and property_data.bedrooms > criteria.max_bedrooms:
            return False
        if criteria.min_bathrooms and property_data.bathrooms and property_data.bathrooms < criteria.min_bathrooms:
            return False
        if criteria.max_bathrooms and property_data.bathrooms and property_data.bathrooms > criteria.max_bathrooms:
            return False
        if criteria.property_type and property_data.property_type and property_data.property_type.lower() != criteria.property_type.lower():
            return False
        
        return True
    
    async def _get_comparable_sales(self, address: str, radius_miles: float, max_comps: int) -> List[Dict[str, Any]]:
        """Get comparable sales for property valuation"""
        try:
            # Implementation would use ATTOM API to find comparable sales
            # For now, return empty list as placeholder
            return []
        except Exception as e:
            logger.error(f"Failed to get comparable sales: {e}")
            return []
    
    async def _calculate_property_value(self, property_data: Dict[str, Any], comparables: List[Dict[str, Any]]) -> Optional[float]:
        """Calculate property value based on property data and comparables"""
        try:
            # Use existing listing price if available
            if property_data.get('listing_price'):
                return float(property_data['listing_price'])
            
            # Use assessed value if available
            if property_data.get('assessed_value'):
                return float(property_data['assessed_value'])
            
            # Use AVM value if available
            if property_data.get('avm_value'):
                return float(property_data['avm_value'])
            
            # If we have comparables, calculate based on them
            if comparables:
                comp_values = [comp.get('sale_price', 0) for comp in comparables if comp.get('sale_price')]
                if comp_values:
                    return sum(comp_values) / len(comp_values)
            
            return None
            
        except Exception as e:
            logger.error(f"Property value calculation failed: {e}")
            return None
    
    def _calculate_confidence_score(self, property_data: Dict[str, Any], comparables: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for valuation"""
        score = 0.5  # Base score
        
        # Increase score based on available data
        if property_data.get('listing_price'):
            score += 0.2
        if property_data.get('assessed_value'):
            score += 0.1
        if property_data.get('avm_value'):
            score += 0.1
        if len(comparables) >= 3:
            score += 0.1
        
        return min(score, 1.0)
    
    def _determine_market_temperature(self, market_stats: Dict[str, Any]) -> str:
        """Determine market temperature based on statistics"""
        days_on_market = market_stats.get('avg_days_on_market', 60)
        price_trend = market_stats.get('price_trend_pct', 0)
        
        if days_on_market < 30 and price_trend > 5:
            return "hot"
        elif days_on_market > 90 and price_trend < -2:
            return "cold"
        else:
            return "balanced"

# Initialize the bridge service (will be used by main.py)
attom_bridge_service = None

def get_attom_bridge_service(api_key: str) -> ATTOMBridgeService:
    """Get or create ATTOM bridge service instance"""
    global attom_bridge_service
    if not attom_bridge_service:
        attom_bridge_service = ATTOMBridgeService(api_key)
    return attom_bridge_service