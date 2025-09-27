"""
ATTOM Data API Integration for Real Estate Investment Platform
Provides property data, market trends, valuations, and comparable sales
"""

import httpx
import logging
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import os
from dataclasses import dataclass
import json

from models.data_models import (
    ATTOMPropertyData, ATTOMMarketData, ATTOMSearchCriteria,
    PropertyDetails, MarketMetrics, ComparableProperty, PropertyType
)

logger = logging.getLogger(__name__)


class ATTOMAPIError(Exception):
    """Custom exception for ATTOM API errors"""
    pass


@dataclass
class APIEndpoints:
    """ATTOM API endpoint configuration"""
    PROPERTY_DETAIL = "https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/detail"
    MARKET_SNAPSHOT = "https://api.gateway.attomdata.com/propertyapi/v1.0.0/market/snapshot"
    COMPARABLE_SALES = "https://api.gateway.attomdata.com/propertyapi/v1.0.0/sale/detail"
    PROPERTY_SEARCH = "https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/basicprofile"
    ESTIMATED_VALUE = "https://api.gateway.attomdata.com/propertyapi/v1.0.0/avm/detail"
    RENTAL_ESTIMATE = "https://api.gateway.attomdata.com/propertyapi/v1.0.0/rentalestimate/detail"


class ATTOMDataBridge:
    """
    ATTOM Data API integration bridge for the real estate platform
    Handles all interactions with ATTOM's property data services
    """
    
    def __init__(self, api_key: str, environment: str = "production"):
        """Initialize ATTOM Data API client"""
        self.api_key = api_key
        self.environment = environment
        self.base_headers = {
            "Accept": "application/json",
            "apikey": api_key
        }
        
        # Rate limiting (ATTOM allows different rates based on subscription)
        self.max_requests_per_minute = 120  # Adjust based on your ATTOM plan
        self.request_timestamps = []
        
        # Cache settings
        self.cache_duration_hours = 1  # Cache data for 1 hour
        self.property_cache = {}
        self.market_cache = {}
        
        logger.info(f"ATTOM Data Bridge initialized for {environment} environment")
    
    async def _make_request(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make rate-limited request to ATTOM API"""
        
        # Rate limiting
        await self._enforce_rate_limit()
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params, headers=self.base_headers)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    raise ATTOMAPIError("Invalid API key or authentication failed")
                elif response.status_code == 429:
                    raise ATTOMAPIError("Rate limit exceeded")
                elif response.status_code == 404:
                    logger.warning(f"No data found for request: {params}")
                    return {}
                else:
                    raise ATTOMAPIError(f"API request failed with status {response.status_code}: {response.text}")
                    
        except httpx.TimeoutException:
            raise ATTOMAPIError("API request timeout")
        except Exception as e:
            logger.error(f"ATTOM API request failed: {e}")
            raise ATTOMAPIError(f"Request failed: {str(e)}")
    
    async def _enforce_rate_limit(self):
        """Enforce API rate limits"""
        now = datetime.now()
        
        # Remove timestamps older than 1 minute
        self.request_timestamps = [
            ts for ts in self.request_timestamps 
            if now - ts < timedelta(minutes=1)
        ]
        
        # If we're at the limit, wait
        if len(self.request_timestamps) >= self.max_requests_per_minute:
            wait_time = 60 - (now - self.request_timestamps[0]).total_seconds()
            if wait_time > 0:
                logger.info(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)
        
        # Record this request
        self.request_timestamps.append(now)
    
    def _get_cache_key(self, endpoint: str, params: Dict[str, Any]) -> str:
        """Generate cache key for request"""
        return f"{endpoint}:{hash(json.dumps(sorted(params.items())))}"
    
    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid"""
        if not cache_entry:
            return False
        
        cache_time = cache_entry.get('timestamp')
        if not cache_time:
            return False
        
        return datetime.now() - cache_time < timedelta(hours=self.cache_duration_hours)
    
    async def get_property_details(self, address: str) -> Optional[ATTOMPropertyData]:
        """Get detailed property information"""
        
        cache_key = self._get_cache_key("property_detail", {"address": address})
        
        # Check cache first
        if cache_key in self.property_cache and self._is_cache_valid(self.property_cache[cache_key]):
            logger.debug(f"Using cached property data for {address}")
            return self.property_cache[cache_key]['data']
        
        params = {
            "address1": address,
            "format": "json"
        }
        
        try:
            response = await self._make_request(APIEndpoints.PROPERTY_DETAIL, params)
            
            if not response or 'property' not in response:
                logger.warning(f"No property data found for address: {address}")
                return None
            
            property_data = response['property'][0]  # Take first result
            
            # Convert to our data model
            attom_property = ATTOMPropertyData(
                property_id=property_data.get('identifier', {}).get('fips', ''),
                address=address,
                city=property_data.get('address', {}).get('locality', ''),
                state=property_data.get('address', {}).get('countrySubd', ''),
                zip_code=property_data.get('address', {}).get('postal1', ''),
                county=property_data.get('address', {}).get('county', ''),
                fips_code=property_data.get('identifier', {}).get('fips'),
                apn=property_data.get('identifier', {}).get('apn'),
                property_type=property_data.get('summary', {}).get('propType', ''),
                bedrooms=property_data.get('building', {}).get('rooms', {}).get('beds'),
                bathrooms=property_data.get('building', {}).get('rooms', {}).get('bathstotal'),
                square_feet=property_data.get('building', {}).get('size', {}).get('livingsize'),
                lot_size_sqft=property_data.get('lot', {}).get('lotsize1'),
                year_built=property_data.get('summary', {}).get('yearbuilt'),
                estimated_value=property_data.get('assessment', {}).get('market', {}).get('mktttlvalue'),
                last_sale_price=property_data.get('sale', {}).get('amount', {}).get('saleamt'),
                last_sale_date=self._parse_date(property_data.get('sale', {}).get('amount', {}).get('salerecdate')),
                tax_assessed_value=property_data.get('assessment', {}).get('tax', {}).get('taxamt'),
                tax_year=property_data.get('assessment', {}).get('tax', {}).get('taxyear')
            )
            
            # Cache the result
            self.property_cache[cache_key] = {
                'data': attom_property,
                'timestamp': datetime.now()
            }
            
            logger.info(f"Retrieved property details for {address}")
            return attom_property
            
        except Exception as e:
            logger.error(f"Failed to get property details for {address}: {e}")
            return None
    
    async def get_market_data(self, county_fips: str, state: str) -> Optional[ATTOMMarketData]:
        """Get market analytics for a specific area"""
        
        cache_key = self._get_cache_key("market_data", {"county_fips": county_fips, "state": state})
        
        # Check cache
        if cache_key in self.market_cache and self._is_cache_valid(self.market_cache[cache_key]):
            logger.debug(f"Using cached market data for {county_fips}")
            return self.market_cache[cache_key]['data']
        
        params = {
            "geoid": county_fips,
            "interval": "monthly",
            "format": "json"
        }
        
        try:
            response = await self._make_request(APIEndpoints.MARKET_SNAPSHOT, params)
            
            if not response or 'market' not in response:
                logger.warning(f"No market data found for county: {county_fips}")
                return None
            
            market_data = response['market'][0]
            
            attom_market = ATTOMMarketData(
                county_fips=county_fips,
                county_name=market_data.get('county', ''),
                state=state,
                median_sale_price=market_data.get('salesPrice', {}).get('median', 0),
                median_price_per_sqft=market_data.get('pricePerSQFT', {}).get('median', 0),
                median_days_on_market=market_data.get('daysOnMarket', {}).get('median', 0),
                months_of_supply=market_data.get('inventory', {}).get('monthsOfSupply', 0),
                price_change_3m=market_data.get('salesPrice', {}).get('change3m', 0),
                price_change_6m=market_data.get('salesPrice', {}).get('change6m', 0),
                price_change_12m=market_data.get('salesPrice', {}).get('change12m', 0),
                sales_volume=market_data.get('salesCount', 0),
                new_listings=market_data.get('newListings', 0),
                foreclosure_rate=market_data.get('foreclosureRate'),
                rental_yield=market_data.get('rentalYield')
            )
            
            # Cache the result
            self.market_cache[cache_key] = {
                'data': attom_market,
                'timestamp': datetime.now()
            }
            
            logger.info(f"Retrieved market data for {county_fips}")
            return attom_market
            
        except Exception as e:
            logger.error(f"Failed to get market data for {county_fips}: {e}")
            return None
    
    async def get_comparable_sales(self, address: str, radius_miles: float = 0.5, 
                                 max_results: int = 10) -> List[ComparableProperty]:
        """Get comparable property sales"""
        
        params = {
            "address1": address,
            "radius": radius_miles,
            "minSaleDate": (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d"),
            "orderBy": "saleDate",
            "pageSize": max_results,
            "format": "json"
        }
        
        try:
            response = await self._make_request(APIEndpoints.COMPARABLE_SALES, params)
            
            if not response or 'sale' not in response:
                logger.warning(f"No comparable sales found for {address}")
                return []
            
            comparables = []
            for sale in response['sale']:
                try:
                    comp = ComparableProperty(
                        address=sale.get('property', {}).get('address', {}).get('oneline', ''),
                        distance=sale.get('distance', 0),
                        price=sale.get('amount', {}).get('saleamt', 0),
                        price_per_sqft=self._calculate_price_per_sqft(
                            sale.get('amount', {}).get('saleamt', 0),
                            sale.get('property', {}).get('building', {}).get('size', {}).get('livingsize', 1)
                        ),
                        bedrooms=sale.get('property', {}).get('building', {}).get('rooms', {}).get('beds', 0),
                        bathrooms=sale.get('property', {}).get('building', {}).get('rooms', {}).get('bathstotal', 0),
                        square_feet=sale.get('property', {}).get('building', {}).get('size', {}).get('livingsize', 0),
                        days_on_market=sale.get('daysOnMarket', 0),
                        sale_date=self._parse_date(sale.get('salerecdate')),
                        similarity_score=0.8  # Placeholder - could be calculated based on property features
                    )
                    comparables.append(comp)
                except Exception as e:
                    logger.warning(f"Error processing comparable sale: {e}")
                    continue
            
            logger.info(f"Found {len(comparables)} comparable sales for {address}")
            return comparables
            
        except Exception as e:
            logger.error(f"Failed to get comparable sales for {address}: {e}")
            return []
    
    async def get_estimated_value(self, address: str) -> Optional[float]:
        """Get ATTOM's estimated property value (AVM)"""
        
        params = {
            "address1": address,
            "format": "json"
        }
        
        try:
            response = await self._make_request(APIEndpoints.ESTIMATED_VALUE, params)
            
            if not response or 'avm' not in response:
                logger.warning(f"No estimated value found for {address}")
                return None
            
            avm_data = response['avm'][0]
            estimated_value = avm_data.get('amount', {}).get('value')
            
            logger.info(f"Retrieved estimated value for {address}: ${estimated_value:,.2f}")
            return estimated_value
            
        except Exception as e:
            logger.error(f"Failed to get estimated value for {address}: {e}")
            return None
    
    async def get_rental_estimate(self, address: str) -> Optional[float]:
        """Get estimated rental value"""
        
        params = {
            "address1": address,
            "format": "json"
        }
        
        try:
            response = await self._make_request(APIEndpoints.RENTAL_ESTIMATE, params)
            
            if not response or 'rentalestimate' not in response:
                logger.warning(f"No rental estimate found for {address}")
                return None
            
            rental_data = response['rentalestimate'][0]
            rental_estimate = rental_data.get('amount', {}).get('value')
            
            logger.info(f"Retrieved rental estimate for {address}: ${rental_estimate:,.2f}")
            return rental_estimate
            
        except Exception as e:
            logger.error(f"Failed to get rental estimate for {address}: {e}")
            return None
    
    async def search_properties(self, criteria: ATTOMSearchCriteria) -> List[ATTOMPropertyData]:
        """Search for properties based on criteria"""
        
        params = {
            "format": "json",
            "pageSize": criteria.max_results
        }
        
        # Add search criteria
        if criteria.address:
            params["address1"] = criteria.address
        if criteria.city:
            params["locality"] = criteria.city
        if criteria.state:
            params["countrysubdivision"] = criteria.state
        if criteria.zip_code:
            params["postalcode"] = criteria.zip_code
        if criteria.min_price:
            params["minSalePrice"] = criteria.min_price
        # Note: maxSalePrice not supported by ATTOM API - will filter client-side
        # if criteria.max_price:
        #     params["maxSalePrice"] = criteria.max_price
        if criteria.min_bedrooms:
            params["minBeds"] = criteria.min_bedrooms
        if criteria.max_bedrooms:
            params["maxBeds"] = criteria.max_bedrooms
        if criteria.property_types:
            params["propertyType"] = ",".join(criteria.property_types)
        
        try:
            response = await self._make_request(APIEndpoints.PROPERTY_SEARCH, params)
            
            if not response or 'property' not in response:
                logger.warning("No properties found matching search criteria")
                return []
            
            properties = []
            for prop_data in response['property']:
                try:
                    # Extract key sections
                    address_info = prop_data.get('address', {})
                    building_info = prop_data.get('building', {})
                    summary_info = prop_data.get('summary', {})
                    assessment_info = prop_data.get('assessment', {})
                    sale_info = prop_data.get('sale', {})
                    location_info = prop_data.get('location', {})
                    
                    # Extract address - use oneLine which is available
                    full_address = address_info.get('oneLine', '')
                    
                    # Extract building size information
                    size_info = building_info.get('size', {})
                    rooms_info = building_info.get('rooms', {})
                    
                    # Extract assessment values (this is where the valuation data is)
                    assessed_info = assessment_info.get('assessed', {})
                    market_info = assessment_info.get('market', {})
                    
                    property_obj = ATTOMPropertyData(
                        property_id=str(prop_data.get('identifier', {}).get('attomId', '')),
                        address=full_address,
                        city=address_info.get('locality', ''),
                        state=address_info.get('countrySubd', ''),
                        zip_code=address_info.get('postal1', ''),
                        latitude=float(location_info.get('latitude', 0)) if location_info.get('latitude') else None,
                        longitude=float(location_info.get('longitude', 0)) if location_info.get('longitude') else None,
                        property_type=summary_info.get('propType', ''),
                        bedrooms=rooms_info.get('beds'),
                        bathrooms=rooms_info.get('bathsTotal'),
                        square_footage=int(size_info.get('livingSize', 0)) if size_info.get('livingSize') else None,
                        lot_size=prop_data.get('lot', {}).get('lotSize2'),  # lot size in sqft
                        build_year=summary_info.get('yearBuilt'),
                        # Assessment values (these are what we have for valuation)
                        assessed_value=assessed_info.get('assdTtlValue'),
                        avm_value=market_info.get('mktTtlValue'),  # Use market value as AVM equivalent
                        # Sale information - may not be available in basic profile
                        last_sale_price=sale_info.get('amount', {}).get('saleamt') if sale_info.get('amount') else None,
                        last_sale_date=sale_info.get('amount', {}).get('salerecdate') if sale_info.get('amount') else None,
                        listing_price=None,  # Not available in basic profile
                        rental_estimate=None  # Not available in basic profile
                    )
                    properties.append(property_obj)
                except Exception as e:
                    logger.warning(f"Error processing property search result: {e}")
                    continue
            
            logger.info(f"Found {len(properties)} properties matching search criteria")
            return properties
            
        except Exception as e:
            logger.error(f"Property search failed: {e}")
            return []
    
    # Helper methods
    
    def _parse_date(self, date_string: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime object"""
        if not date_string:
            return None
        
        try:
            # ATTOM typically returns dates in YYYY-MM-DD format
            return datetime.strptime(date_string, "%Y-%m-%d")
        except ValueError:
            try:
                # Try alternative format
                return datetime.strptime(date_string, "%m/%d/%Y")
            except ValueError:
                logger.warning(f"Unable to parse date: {date_string}")
                return None
    
    def _calculate_price_per_sqft(self, price: float, square_feet: int) -> float:
        """Calculate price per square foot"""
        if not square_feet or square_feet <= 0:
            return 0
        return round(price / square_feet, 2)
    
    # Data conversion methods for Analysis Engine
    
    def convert_to_property_details(self, attom_data: ATTOMPropertyData, 
                                   listing_price: Optional[float] = None) -> PropertyDetails:
        """Convert ATTOM data to our PropertyDetails model"""
        
        # Map ATTOM property types to our enum
        property_type_mapping = {
            "SFR": PropertyType.SINGLE_FAMILY,
            "CON": PropertyType.CONDO,
            "TWH": PropertyType.TOWNHOUSE,
            "APT": PropertyType.MULTI_FAMILY,
            "COM": PropertyType.COMMERCIAL
        }
        
        property_type = property_type_mapping.get(
            attom_data.property_type, 
            PropertyType.SINGLE_FAMILY
        )
        
        return PropertyDetails(
            address=attom_data.address,
            city=attom_data.city,
            state=attom_data.state,
            zip_code=attom_data.zip_code,
            property_type=property_type,
            bedrooms=attom_data.bedrooms or 3,
            bathrooms=attom_data.bathrooms or 2.0,
            square_feet=attom_data.square_feet or 1500,
            lot_size=attom_data.lot_size_sqft / 43560 if attom_data.lot_size_sqft else None,  # Convert to acres
            year_built=attom_data.year_built,
            listing_price=listing_price,
            zestimate=attom_data.estimated_value
        )
    
    def convert_to_market_metrics(self, attom_market: ATTOMMarketData) -> MarketMetrics:
        """Convert ATTOM market data to our MarketMetrics model"""
        
        return MarketMetrics(
            median_home_price=attom_market.median_sale_price,
            price_per_sqft=attom_market.median_price_per_sqft,
            days_on_market=attom_market.median_days_on_market,
            inventory_months=attom_market.months_of_supply,
            price_trend_3m=attom_market.price_change_3m,
            price_trend_6m=attom_market.price_change_6m,
            price_trend_1y=attom_market.price_change_12m,
            rental_yield_avg=attom_market.rental_yield or 6.5,
            cap_rate_avg=5.5,  # Placeholder - calculate from rental_yield if available
            absorption_rate=None,
            new_listings=attom_market.new_listings,
            price_cuts=None
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check ATTOM API connectivity and status"""
        
        test_params = {
            "address1": "1600 Amphitheatre Parkway, Mountain View, CA",
            "format": "json"
        }
        
        try:
            start_time = datetime.now()
            response = await self._make_request(APIEndpoints.PROPERTY_DETAIL, test_params)
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                "status": "healthy" if response else "degraded",
                "response_time_ms": int(response_time),
                "api_version": "1.0.0",
                "rate_limit_remaining": self.max_requests_per_minute - len(self.request_timestamps),
                "cache_entries": len(self.property_cache) + len(self.market_cache)
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time_ms": None,
                "api_version": "1.0.0"
            }