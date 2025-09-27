"""
Agent 3: Deal Finder for Real Estate Investment Platform
Background service that continuously monitors new listings and flags undervalued properties
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
import json
import uuid
from dataclasses import dataclass
from enum import Enum

from models.data_models import PropertyDetails, MarketMetrics, ATTOMSearchCriteria, InvestmentStrategy
from integrations.attom_api import ATTOMDataBridge

logger = logging.getLogger(__name__)


class AlertType(Enum):
    UNDERVALUED_PROPERTY = "undervalued_property"
    PRICE_DROP = "price_drop"
    HIGH_CASH_FLOW = "high_cash_flow"
    DISTRESSED_SALE = "distressed_sale"
    NEW_LISTING = "new_listing"
    MARKET_OPPORTUNITY = "market_opportunity"


class AlertPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


@dataclass
class PropertyAlert:
    """Deal alert for a specific property"""
    alert_id: str
    property_address: str
    alert_type: AlertType
    priority: AlertPriority
    title: str
    description: str
    key_metrics: Dict[str, Any]
    estimated_value: Optional[float] = None
    listing_price: Optional[float] = None
    potential_profit: Optional[float] = None
    confidence_score: float = 0.0
    created_at: datetime = None
    expires_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class SearchCriteria:
    """User-defined search criteria for deal finding"""
    max_price: Optional[float] = None
    min_deal_score: float = 70.0
    preferred_strategies: List[InvestmentStrategy] = None
    target_locations: List[str] = None
    property_types: List[str] = None
    min_cash_flow: Optional[float] = None
    max_risk_score: Optional[int] = None
    keywords: List[str] = None
    
    def __post_init__(self):
        if self.preferred_strategies is None:
            self.preferred_strategies = [InvestmentStrategy.BUY_AND_HOLD]
        if self.target_locations is None:
            self.target_locations = []
        if self.property_types is None:
            self.property_types = ["SFR", "CON", "TWH"]  # Single family, condo, townhouse
        if self.keywords is None:
            self.keywords = []


class DealFinder:
    """
    Agent 3: Deal Finder Background Service
    Continuously monitors new listings and identifies investment opportunities
    """
    
    def __init__(self, attom_bridge: Optional[ATTOMDataBridge] = None, analysis_engine=None):
        """Initialize the Deal Finder"""
        self.attom_bridge = attom_bridge
        self.analysis_engine = analysis_engine
        
        # State management
        self.is_running = False
        self.monitored_properties: Set[str] = set()
        self.user_criteria: Dict[str, SearchCriteria] = {}
        self.active_alerts: List[PropertyAlert] = []
        self.processed_properties: Set[str] = set()
        
        # Configuration
        self.scan_interval_minutes = 15  # How often to check for new listings
        self.alert_retention_days = 7    # How long to keep alerts
        self.max_alerts_per_user = 50    # Maximum alerts to keep per user
        self.max_concurrent_analyses = 5  # Limit concurrent property analyses
        
        # Background tasks
        self.scan_task: Optional[asyncio.Task] = None
        self.cleanup_task: Optional[asyncio.Task] = None
        
        logger.info("Deal Finder initialized")
    
    async def start_monitoring(self):
        """Start the background monitoring service"""
        if self.is_running:
            logger.warning("Deal Finder already running")
            return
        
        self.is_running = True
        
        # Start background tasks
        self.scan_task = asyncio.create_task(self._continuous_scan())
        self.cleanup_task = asyncio.create_task(self._cleanup_expired_alerts())
        
        logger.info("Deal Finder monitoring started")
    
    async def stop_monitoring(self):
        """Stop the background monitoring service"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel background tasks
        if self.scan_task:
            self.scan_task.cancel()
        if self.cleanup_task:
            self.cleanup_task.cancel()
        
        # Wait for tasks to complete
        tasks = [t for t in [self.scan_task, self.cleanup_task] if t and not t.done()]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info("Deal Finder monitoring stopped")
    
    def add_user_criteria(self, user_id: str, criteria: SearchCriteria):
        """Add search criteria for a specific user"""
        self.user_criteria[user_id] = criteria
        logger.info(f"Added search criteria for user {user_id}")
    
    def remove_user_criteria(self, user_id: str):
        """Remove search criteria for a user"""
        if user_id in self.user_criteria:
            del self.user_criteria[user_id]
            logger.info(f"Removed search criteria for user {user_id}")
    
    async def monitor_specific_property(self, address: str) -> bool:
        """Add a specific property to monitoring list"""
        self.monitored_properties.add(address.lower())
        logger.info(f"Added property to monitoring: {address}")
        return True
    
    async def find_deals_now(self, criteria: SearchCriteria, max_results: int = 20) -> List[PropertyAlert]:
        """Immediate deal search based on criteria"""
        logger.info("Starting immediate deal search")
        
        if not self.attom_bridge:
            logger.warning("ATTOM bridge not available, using mock data")
            return await self._generate_mock_deals(criteria, max_results)
        
        try:
            # Convert criteria to ATTOM search parameters
            search_params = self._convert_criteria_to_attom_search(criteria)
            
            # Search for properties
            properties = await self.attom_bridge.search_properties(search_params)
            
            # Analyze properties and generate alerts
            alerts = []
            for property_data in properties[:max_results]:
                try:
                    alert = await self._analyze_property_for_deal(property_data, criteria)
                    if alert:
                        alerts.append(alert)
                except Exception as e:
                    logger.error(f"Error analyzing property {property_data.address}: {e}")
                    continue
            
            # Sort alerts by priority and confidence
            alerts.sort(key=lambda x: (x.priority.value, x.confidence_score), reverse=True)
            
            logger.info(f"Found {len(alerts)} potential deals")
            return alerts
            
        except Exception as e:
            logger.error(f"Deal search failed: {e}")
            return []
    
    async def get_alerts_for_user(self, user_id: str) -> List[PropertyAlert]:
        """Get active alerts for a specific user"""
        # Filter alerts based on user criteria
        user_criteria = self.user_criteria.get(user_id)
        if not user_criteria:
            return []
        
        relevant_alerts = []
        for alert in self.active_alerts:
            if self._alert_matches_criteria(alert, user_criteria):
                relevant_alerts.append(alert)
        
        return relevant_alerts[:self.max_alerts_per_user]
    
    async def _continuous_scan(self):
        """Background task for continuous property scanning"""
        logger.info("Starting continuous property scanning")
        
        while self.is_running:
            try:
                await self._scan_for_new_opportunities()
                await asyncio.sleep(self.scan_interval_minutes * 60)  # Convert to seconds
            except asyncio.CancelledError:
                logger.info("Continuous scan cancelled")
                break
            except Exception as e:
                logger.error(f"Error in continuous scan: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _scan_for_new_opportunities(self):
        """Scan for new investment opportunities"""
        logger.debug("Scanning for new opportunities")
        
        if not self.user_criteria:
            return
        
        # Scan for each user's criteria
        for user_id, criteria in self.user_criteria.items():
            try:
                new_deals = await self.find_deals_now(criteria, max_results=10)
                
                # Add new alerts (avoid duplicates)
                for deal in new_deals:
                    if not self._is_duplicate_alert(deal):
                        self.active_alerts.append(deal)
                        logger.info(f"New deal alert: {deal.property_address} ({deal.alert_type.value})")
                
            except Exception as e:
                logger.error(f"Error scanning for user {user_id}: {e}")
    
    async def _analyze_property_for_deal(self, property_data, criteria: SearchCriteria) -> Optional[PropertyAlert]:
        """Analyze a property to see if it's a good deal"""
        
        # Skip if already processed recently
        property_key = f"{property_data.address}_{datetime.now().date()}"
        if property_key in self.processed_properties:
            return None
        
        self.processed_properties.add(property_key)
        
        try:
            # Basic deal analysis (simplified without full analysis engine)
            estimated_value = property_data.estimated_value or 0
            listing_price = property_data.last_sale_price or estimated_value
            
            if not listing_price or listing_price <= 0:
                return None
            
            # Check if it meets basic criteria
            if criteria.max_price and listing_price > criteria.max_price:
                return None
            
            # Calculate potential profit
            potential_profit = estimated_value - listing_price if estimated_value > listing_price else 0
            profit_percentage = (potential_profit / listing_price * 100) if listing_price > 0 else 0
            
            # Determine if it's worth alerting about
            if profit_percentage < 10:  # Less than 10% profit potential
                return None
            
            # Create alert
            alert_type = self._determine_alert_type(property_data, profit_percentage)
            priority = self._determine_priority(profit_percentage, property_data)
            
            alert = PropertyAlert(
                alert_id=str(uuid.uuid4()),
                property_address=property_data.address,
                alert_type=alert_type,
                priority=priority,
                title=f"Potential Deal: {property_data.address}",
                description=self._generate_alert_description(property_data, profit_percentage),
                key_metrics={
                    "estimated_value": estimated_value,
                    "listing_price": listing_price,
                    "profit_percentage": profit_percentage,
                    "bedrooms": property_data.bedrooms,
                    "bathrooms": property_data.bathrooms,
                    "square_feet": property_data.square_feet
                },
                estimated_value=estimated_value,
                listing_price=listing_price,
                potential_profit=potential_profit,
                confidence_score=min(0.9, profit_percentage / 20),  # Higher profit = higher confidence
                expires_at=datetime.now() + timedelta(days=self.alert_retention_days)
            )
            
            return alert
            
        except Exception as e:
            logger.error(f"Error analyzing property {property_data.address}: {e}")
            return None
    
    def _convert_criteria_to_attom_search(self, criteria: SearchCriteria) -> ATTOMSearchCriteria:
        """Convert user criteria to ATTOM search parameters"""
        return ATTOMSearchCriteria(
            max_price=criteria.max_price,
            property_types=criteria.property_types,
            max_results=50
        )
    
    def _determine_alert_type(self, property_data, profit_percentage: float) -> AlertType:
        """Determine the type of alert based on property data"""
        if profit_percentage > 25:
            return AlertType.UNDERVALUED_PROPERTY
        elif profit_percentage > 15:
            return AlertType.HIGH_CASH_FLOW
        else:
            return AlertType.NEW_LISTING
    
    def _determine_priority(self, profit_percentage: float, property_data) -> AlertPriority:
        """Determine alert priority"""
        if profit_percentage > 30:
            return AlertPriority.URGENT
        elif profit_percentage > 20:
            return AlertPriority.HIGH
        elif profit_percentage > 10:
            return AlertPriority.MEDIUM
        else:
            return AlertPriority.LOW
    
    def _generate_alert_description(self, property_data, profit_percentage: float) -> str:
        """Generate description for the alert"""
        return (
            f"Property may be undervalued by {profit_percentage:.1f}%. "
            f"{property_data.bedrooms}BR/{property_data.bathrooms}BA, "
            f"{property_data.square_feet} sqft. Consider for quick analysis."
        )
    
    def _alert_matches_criteria(self, alert: PropertyAlert, criteria: SearchCriteria) -> bool:
        """Check if an alert matches user criteria"""
        # Check price limit
        if criteria.max_price and alert.listing_price and alert.listing_price > criteria.max_price:
            return False
        
        # Check minimum cash flow (simplified)
        if criteria.min_cash_flow and alert.key_metrics.get("profit_percentage", 0) < 15:
            return False
        
        # Check location (simplified - would need proper location matching)
        if criteria.target_locations:
            # Simple substring match for demo
            address_lower = alert.property_address.lower()
            if not any(loc.lower() in address_lower for loc in criteria.target_locations):
                return False
        
        return True
    
    def _is_duplicate_alert(self, new_alert: PropertyAlert) -> bool:
        """Check if this alert already exists"""
        for existing_alert in self.active_alerts:
            if (existing_alert.property_address.lower() == new_alert.property_address.lower() and
                existing_alert.alert_type == new_alert.alert_type):
                return True
        return False
    
    async def _cleanup_expired_alerts(self):
        """Background task to clean up expired alerts"""
        while self.is_running:
            try:
                current_time = datetime.now()
                
                # Remove expired alerts
                self.active_alerts = [
                    alert for alert in self.active_alerts 
                    if not alert.expires_at or alert.expires_at > current_time
                ]
                
                # Clean up processed properties (keep only recent ones)
                cutoff_date = (current_time - timedelta(days=1)).date()
                self.processed_properties = {
                    prop for prop in self.processed_properties 
                    if not prop.endswith(str(cutoff_date))
                }
                
                logger.debug(f"Cleanup: {len(self.active_alerts)} active alerts, {len(self.processed_properties)} processed properties")
                
                # Sleep for 1 hour
                await asyncio.sleep(3600)
                
            except asyncio.CancelledError:
                logger.info("Cleanup task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying
    
    async def _generate_mock_deals(self, criteria: SearchCriteria, max_results: int) -> List[PropertyAlert]:
        """Generate mock deals for testing when ATTOM is not available"""
        mock_deals = []
        
        mock_properties = [
            {
                "address": "123 Investment Ave, Blacksburg, VA 24060",
                "estimated_value": 280000,
                "listing_price": 250000,
                "bedrooms": 3,
                "bathrooms": 2,
                "square_feet": 1500
            },
            {
                "address": "456 Cash Flow St, Christiansburg, VA 24073",
                "estimated_value": 320000,
                "listing_price": 285000,
                "bedrooms": 4,
                "bathrooms": 2.5,
                "square_feet": 1800
            },
            {
                "address": "789 Rental Ln, Radford, VA 24141",
                "estimated_value": 195000,
                "listing_price": 175000,
                "bedrooms": 3,
                "bathrooms": 1.5,
                "square_feet": 1200
            }
        ]
        
        for prop in mock_properties[:max_results]:
            potential_profit = prop["estimated_value"] - prop["listing_price"]
            profit_percentage = (potential_profit / prop["listing_price"]) * 100
            
            if profit_percentage >= 10:  # Only include if good deal
                alert = PropertyAlert(
                    alert_id=str(uuid.uuid4()),
                    property_address=prop["address"],
                    alert_type=AlertType.UNDERVALUED_PROPERTY,
                    priority=AlertPriority.HIGH if profit_percentage > 15 else AlertPriority.MEDIUM,
                    title=f"Great Deal Found: {prop['address']}",
                    description=f"Property appears undervalued by {profit_percentage:.1f}% - excellent cash flow potential!",
                    key_metrics={
                        "estimated_value": prop["estimated_value"],
                        "listing_price": prop["listing_price"],
                        "profit_percentage": profit_percentage,
                        "bedrooms": prop["bedrooms"],
                        "bathrooms": prop["bathrooms"],
                        "square_feet": prop["square_feet"]
                    },
                    estimated_value=prop["estimated_value"],
                    listing_price=prop["listing_price"],
                    potential_profit=potential_profit,
                    confidence_score=0.8,
                    expires_at=datetime.now() + timedelta(days=7)
                )
                mock_deals.append(alert)
        
        return mock_deals
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            "is_running": self.is_running,
            "monitored_properties": len(self.monitored_properties),
            "active_alerts": len(self.active_alerts),
            "user_criteria_count": len(self.user_criteria),
            "processed_properties": len(self.processed_properties),
            "scan_interval_minutes": self.scan_interval_minutes,
            "last_scan": datetime.now().isoformat() if self.is_running else None
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Deal Finder health status"""
        try:
            status = "healthy" if self.is_running else "stopped"
            
            # Check if background tasks are running
            scan_task_status = "running" if self.scan_task and not self.scan_task.done() else "stopped"
            cleanup_task_status = "running" if self.cleanup_task and not self.cleanup_task.done() else "stopped"
            
            return {
                "status": status,
                "background_tasks": {
                    "scan_task": scan_task_status,
                    "cleanup_task": cleanup_task_status
                },
                "monitoring_stats": self.get_monitoring_status(),
                "last_check": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }