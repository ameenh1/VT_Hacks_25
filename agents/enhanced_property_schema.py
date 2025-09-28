"""
Enhanced Property Schema for Comprehensive Analysis
=================================================

This implements the full "everything we should track" checklist for home pricing
with robust feature tracking and valuation adjustments.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

class PropertyType(str, Enum):
    SINGLE_FAMILY = "single_family"
    CONDO = "condo"
    TOWNHOME = "townhome"
    MULTI_FAMILY = "multi_family"
    MANUFACTURED = "manufactured"

class ConditionRating(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    FAIR = "fair"
    POOR = "poor"

class RiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class PropertyStructure:
    """Property structure and livability features"""
    # Basic structure
    total_sqft: int
    finished_sqft: int
    bedrooms: int
    bathrooms: float
    bed_bath_ratio: float
    ceiling_height: float
    stories: int
    bedroom_on_main: bool
    
    # Condition and age
    condition: ConditionRating
    effective_age: int
    renovation_year: Optional[int] = None
    
    # Material grades (1-5 scale)
    flooring_grade: int = 3
    counter_grade: int = 3
    window_grade: int = 3
    roof_grade: int = 3
    
    # Kitchen/Bath details
    kitchen_count: int = 1
    kitchen_size_sqft: int = 150
    kitchen_quality: int = 3  # 1-5 scale
    full_baths: int = 2
    half_baths: int = 1
    master_bath_luxury: bool = False

@dataclass
class PropertySystems:
    """HVAC, electrical, plumbing, and technology systems"""
    # HVAC
    hvac_type: str = "central_air"  # central_air, heat_pump, baseboard, etc.
    hvac_age: int = 10
    has_ac: bool = True
    
    # Electrical/Plumbing
    electrical_panel_amps: int = 200
    plumbing_type: str = "copper"  # copper, pex, galvanized
    water_heater_age: int = 8
    water_heater_type: str = "gas"  # gas, electric, tankless
    
    # Modern tech
    has_solar: bool = False
    solar_kw: float = 0.0
    has_ev_charger: bool = False
    smart_home_features: List[str] = None
    
    def __post_init__(self):
        if self.smart_home_features is None:
            self.smart_home_features = []

@dataclass
class PropertyEnergy:
    """Energy efficiency and utility information"""
    insulation_rating: int = 3  # 1-5 scale
    window_efficiency: int = 3  # 1-5 scale
    hers_score: Optional[int] = None  # Lower is better
    energy_star_rating: bool = False
    avg_monthly_electric: float = 150.0
    avg_monthly_gas: float = 80.0
    avg_monthly_total_utilities: float = 250.0

@dataclass
class PropertySpaces:
    """Flexible spaces, storage, and parking"""
    # Flex spaces
    has_office: bool = False
    has_den: bool = False
    finished_basement: bool = False
    finished_attic: bool = False
    has_adu: bool = False  # Accessory Dwelling Unit
    separate_entrance_count: int = 1
    
    # Storage and parking
    garage_spaces: int = 2
    garage_type: str = "attached"  # attached, detached, carport
    driveway_spaces: int = 2
    covered_parking_spaces: int = 0
    total_parking_spaces: int = 4
    storage_sqft: int = 100

@dataclass
class PropertyAmenities:
    """Luxury and lifestyle amenities"""
    has_pool: bool = False
    pool_type: str = ""  # inground, above_ground, spa
    has_spa: bool = False
    has_sauna: bool = False
    
    outdoor_features: List[str] = None
    fireplace_count: int = 0
    fireplace_types: List[str] = None
    
    yard_usability: int = 3  # 1-5 scale
    fencing_type: str = "none"  # none, partial, full, privacy
    
    def __post_init__(self):
        if self.outdoor_features is None:
            self.outdoor_features = []
        if self.fireplace_types is None:
            self.fireplace_types = []

@dataclass
class PropertyViews:
    """Views, orientation, and environmental factors"""
    view_type: str = "standard"  # water, city, mountain, golf, standard
    view_quality: int = 3  # 1-5 scale
    privacy_level: int = 3  # 1-5 scale
    natural_light: int = 3  # 1-5 scale
    noise_level: int = 3  # 1-5 scale (lower is quieter)
    orientation: str = "south"  # north, south, east, west

@dataclass
class SiteLot:
    """Lot characteristics and site conditions"""
    lot_size_sqft: float
    buildable_area_sqft: float
    lot_shape: str = "rectangular"  # rectangular, irregular, flag, corner
    frontage_feet: float = 75.0
    backyard_depth_feet: float = 100.0
    
    # Topography
    slope_condition: str = "flat"  # flat, gentle_slope, steep_slope
    drainage_quality: int = 3  # 1-5 scale
    soil_conditions: str = "stable"  # stable, clay, sandy, rocky
    
    # Water features
    waterfront: bool = False
    water_type: str = ""  # ocean, lake, river, canal
    flood_zone: str = "X"  # X (no flood), A, AE, VE
    
    # Utilities and access
    sewer_type: str = "public"  # public, septic
    water_source: str = "public"  # public, well
    alley_access: bool = False

@dataclass
class LocationNeighborhood:
    """Location quality and neighborhood characteristics"""
    # Schools
    elementary_school_rating: int = 5  # 1-10 scale
    middle_school_rating: int = 5
    high_school_rating: int = 5
    school_district_quality: int = 5
    
    # Safety and walkability
    crime_index: int = 50  # 0-100, lower is safer
    walk_score: int = 50  # 0-100, higher is more walkable
    bike_score: int = 50
    transit_score: int = 50
    
    # Proximity scores (1-5, higher is closer/better)
    proximity_parks: int = 3
    proximity_shopping: int = 3
    proximity_healthcare: int = 3
    proximity_employment: int = 3
    proximity_airport: int = 3
    commute_time_downtown: int = 30  # minutes
    
    # Demographics
    median_household_income: float = 65000.0
    owner_occupancy_rate: float = 0.7
    neighborhood_stability: int = 3  # 1-5 scale

@dataclass
class MarketLiquidity:
    """Market conditions and liquidity factors"""
    months_of_inventory: float = 3.0
    median_days_on_market: int = 45
    sale_to_list_ratio: float = 0.98
    price_cut_rate: float = 0.15
    
    # Seasonality (1.0 = baseline, >1.0 = premium, <1.0 = discount)
    spring_seasonality: float = 1.05
    summer_seasonality: float = 1.02
    fall_seasonality: float = 0.98
    winter_seasonality: float = 0.95
    
    investor_activity_pct: float = 0.15
    cash_buyer_pct: float = 0.25

@dataclass
class LegalFinancial:
    """Legal, financial, and regulatory factors"""
    # Property taxes
    annual_property_tax: float = 8000.0
    tax_rate_per_1000: float = 12.5
    homestead_exemption: bool = True
    recent_reassessment: bool = False
    
    # HOA and fees
    monthly_hoa_fee: float = 0.0
    hoa_reserve_health: int = 3  # 1-5 scale
    special_assessments: float = 0.0
    
    # Insurance and risks
    annual_insurance_cost: float = 1500.0
    flood_insurance_required: bool = False
    wildfire_risk: RiskLevel = RiskLevel.LOW
    earthquake_risk: RiskLevel = RiskLevel.LOW
    
    # Permits and compliance
    permit_issues: bool = False
    code_violations: bool = False
    unpermitted_additions: bool = False

@dataclass
class DataQuality:
    """Data quality and confidence metrics"""
    comp_count_within_half_mile: int = 10
    comp_variance: float = 0.15  # Coefficient of variation
    photo_count: int = 25
    has_floor_plan: bool = True
    has_3d_tour: bool = False
    mls_data_completeness: float = 0.85  # 0-1 scale
    last_updated: datetime = datetime.now()

@dataclass
class ComprehensivePropertyFeatures:
    """Master property features class combining all aspects"""
    # Basic identification (required fields first)
    address: str
    property_type: PropertyType
    structure: PropertyStructure
    systems: PropertySystems
    energy: PropertyEnergy
    spaces: PropertySpaces
    amenities: PropertyAmenities
    views: PropertyViews
    site: SiteLot
    location: LocationNeighborhood
    market: MarketLiquidity
    legal: LegalFinancial
    data_quality: DataQuality
    
    # Optional fields with defaults (must come last)
    listing_price: Optional[float] = None
    total_score: Optional[float] = None
    confidence_level: Optional[float] = None
    
    def calculate_comprehensive_score(self, weights: Dict[str, float]) -> float:
        """Calculate weighted comprehensive property score"""
        # This would implement the full scoring algorithm
        # using all the feature categories with proper weights
        pass

class ComprehensiveAdjustmentRates:
    """Comprehensive adjustment rates for all property factors"""
    
    def __init__(self):
        self.adjustment_rates = {
            # Structure adjustments
            'gla_per_sqft': 75.0,  # Increased from basic $50
            'bedroom_value': 8000.0,
            'bathroom_value': 4500.0,
            'ceiling_height_per_foot': 2000.0,
            'main_floor_bedroom': 5000.0,
            
            # System adjustments
            'hvac_age_per_year': -200.0,
            'roof_age_per_year': -150.0,
            'solar_per_kw': 3000.0,
            'ev_charger': 2000.0,
            'smart_home_package': 5000.0,
            
            # Energy efficiency
            'energy_star_premium': 3000.0,
            'hers_score_adjustment': -50.0,  # Per point below 100
            
            # Amenities
            'pool_inground': 15000.0,
            'pool_above_ground': 5000.0,
            'fireplace_value': 3000.0,
            'garage_per_space': 8000.0,
            
            # Views and location
            'water_view_premium': {
                'ocean': 0.15,  # 15% premium
                'lake': 0.08,
                'river': 0.05
            },
            'view_quality_per_point': 2000.0,
            
            # School quality (major factor)
            'school_rating_per_point': 5000.0,  # Per point on 1-10 scale
            
            # Safety and walkability
            'walk_score_per_point': 200.0,
            'crime_index_per_point': -300.0,  # Negative for higher crime
            
            # Market liquidity adjustments
            'high_inventory_discount': -0.05,  # 5% discount in buyer's market
            'low_inventory_premium': 0.03,    # 3% premium in seller's market
            
            # Risk adjustments
            'flood_zone_discount': -0.10,  # 10% discount for flood zones
            'wildfire_risk_discount': -0.08,
            'hoa_fee_per_dollar': -20.0,  # $20 value reduction per $1 monthly HOA
            
            # Condition multipliers (expanded)
            'condition_multipliers': {
                'excellent': 1.12,
                'good': 1.0,
                'average': 0.96,
                'fair': 0.88,
                'poor': 0.75
            },
            
            # Seasonal adjustments
            'seasonal_multipliers': {
                'spring': 1.05,
                'summer': 1.02,
                'fall': 0.98,
                'winter': 0.95
            }
        }
    
    def get_adjustment_value(self, category: str, property_features: ComprehensivePropertyFeatures) -> float:
        """Calculate specific adjustment value for a property feature"""
        # Implementation would calculate actual dollar adjustments
        # based on the comprehensive feature set
        pass

# Usage example for integration
def create_sample_comprehensive_property() -> ComprehensivePropertyFeatures:
    """Create a sample property with comprehensive features"""
    return ComprehensivePropertyFeatures(
        address="123 Investment Way",
        property_type=PropertyType.SINGLE_FAMILY,
        listing_price=485000.0,
        
        structure=PropertyStructure(
            total_sqft=2400,
            finished_sqft=2200,
            bedrooms=4,
            bathrooms=2.5,
            bed_bath_ratio=1.6,
            ceiling_height=9.0,
            stories=2,
            bedroom_on_main=True,
            condition=ConditionRating.GOOD,
            effective_age=12,
            renovation_year=2020
        ),
        
        systems=PropertySystems(
            hvac_type="heat_pump",
            hvac_age=5,
            has_ac=True,
            electrical_panel_amps=200,
            has_solar=True,
            solar_kw=8.5,
            has_ev_charger=True
        ),
        
        location=LocationNeighborhood(
            elementary_school_rating=8,
            middle_school_rating=7,
            high_school_rating=9,
            crime_index=25,
            walk_score=72,
            proximity_parks=4,
            commute_time_downtown=25
        ),
        
        # ... other feature groups would be populated
        
        energy=PropertyEnergy(
            insulation_rating=4,
            window_efficiency=4,
            energy_star_rating=True,
            avg_monthly_electric=120.0,
            avg_monthly_gas=65.0
        ),
        
        spaces=PropertySpaces(
            garage_spaces=2,
            garage_type="attached",
            has_office=True,
            finished_basement=True,
            total_parking_spaces=4
        ),
        
        amenities=PropertyAmenities(
            has_pool=True,
            pool_type="inground",
            fireplace_count=2,
            yard_usability=4,
            fencing_type="privacy"
        ),
        
        views=PropertyViews(
            view_type="mountain",
            view_quality=4,
            privacy_level=4,
            natural_light=5,
            noise_level=2
        ),
        
        site=SiteLot(
            lot_size_sqft=9500.0,
            buildable_area_sqft=8000.0,
            frontage_feet=85.0,
            slope_condition="gentle_slope",
            drainage_quality=4,
            flood_zone="X"
        ),
        
        market=MarketLiquidity(
            months_of_inventory=2.8,
            median_days_on_market=35,
            sale_to_list_ratio=1.02,
            spring_seasonality=1.08
        ),
        
        legal=LegalFinancial(
            annual_property_tax=7500.0,
            tax_rate_per_1000=11.8,
            monthly_hoa_fee=0.0,
            annual_insurance_cost=1200.0,
            wildfire_risk=RiskLevel.LOW
        ),
        
        data_quality=DataQuality(
            comp_count_within_half_mile=15,
            photo_count=35,
            has_floor_plan=True,
            has_3d_tour=True,
            mls_data_completeness=0.95
        )
    )


def convert_basic_to_comprehensive(basic_property: Dict[str, Any]) -> ComprehensivePropertyFeatures:
    """
    Convert a basic property dict (like current PropertyFeatures) to comprehensive features
    This helps bridge your existing data to the new comprehensive format
    """
    
    # Extract basic info
    address = basic_property.get('address', 'Unknown Address')
    listing_price = basic_property.get('listing_price')
    
    # Build comprehensive structure
    structure = PropertyStructure(
        total_sqft=basic_property.get('gla', 2000),
        finished_sqft=basic_property.get('gla', 2000),
        bedrooms=basic_property.get('bedrooms', 3),
        bathrooms=basic_property.get('bathrooms', 2.0),
        bed_bath_ratio=basic_property.get('bedrooms', 3) / max(basic_property.get('bathrooms', 2.0), 1),
        ceiling_height=9.0,  # Default
        stories=2 if basic_property.get('gla', 2000) > 1800 else 1,
        bedroom_on_main=basic_property.get('gla', 2000) < 1500,  # Guess based on size
        condition=ConditionRating(basic_property.get('condition', 'average')),
        effective_age=basic_property.get('age', 15)
    )
    
    systems = PropertySystems(
        hvac_age=basic_property.get('age', 15) // 2,  # Guess HVAC is half the age
        has_solar=False,  # Default
        smart_home_features=[]
    )
    
    location = LocationNeighborhood(
        elementary_school_rating=5,  # Default middle rating
        crime_index=50,  # Default middle
        walk_score=50,  # Default middle
        commute_time_downtown=30  # Default
    )
    
    site = SiteLot(
        lot_size_sqft=basic_property.get('lot_size', 8000.0),
        buildable_area_sqft=basic_property.get('lot_size', 8000.0) * 0.8,
        flood_zone="X"  # Default no flood
    )
    
    # Fill in other required components with defaults
    energy = PropertyEnergy()
    spaces = PropertySpaces(garage_spaces=basic_property.get('garage_spaces', 2))
    amenities = PropertyAmenities()
    views = PropertyViews()
    market = MarketLiquidity()
    legal = LegalFinancial()
    data_quality = DataQuality()
    
    return ComprehensivePropertyFeatures(
        address=address,
        property_type=PropertyType.SINGLE_FAMILY,  # Default
        listing_price=listing_price,
        structure=structure,
        systems=systems,
        energy=energy,
        spaces=spaces,
        amenities=amenities,
        views=views,
        site=site,
        location=location,
        market=market,
        legal=legal,
        data_quality=data_quality
    )


def create_test_property_for_analysis() -> ComprehensivePropertyFeatures:
    """
    Create a realistic test property for testing your analysis integration
    """
    return ComprehensivePropertyFeatures(
        address="789 Test Investment Drive",
        property_type=PropertyType.SINGLE_FAMILY,
        listing_price=395000.0,
        
        structure=PropertyStructure(
            total_sqft=2150,
            finished_sqft=2000,
            bedrooms=3,
            bathrooms=2.5,
            bed_bath_ratio=1.2,
            ceiling_height=9.0,
            stories=2,
            bedroom_on_main=False,
            condition=ConditionRating.GOOD,
            effective_age=8,
            renovation_year=2022,
            kitchen_quality=4,
            flooring_grade=4
        ),
        
        systems=PropertySystems(
            hvac_type="heat_pump",
            hvac_age=3,
            has_ac=True,
            has_solar=False,
            has_ev_charger=True,
            smart_home_features=["smart_thermostat", "smart_doorbell", "smart_locks"]
        ),
        
        energy=PropertyEnergy(
            insulation_rating=4,
            window_efficiency=3,
            energy_star_rating=False,
            avg_monthly_electric=135.0,
            avg_monthly_gas=75.0
        ),
        
        spaces=PropertySpaces(
            garage_spaces=2,
            garage_type="attached",
            has_office=True,
            finished_basement=False,
            total_parking_spaces=3
        ),
        
        amenities=PropertyAmenities(
            has_pool=False,
            fireplace_count=1,
            fireplace_types=["gas"],
            yard_usability=4,
            fencing_type="partial"
        ),
        
        views=PropertyViews(
            view_type="standard",
            view_quality=3,
            privacy_level=4,
            natural_light=4,
            noise_level=2
        ),
        
        site=SiteLot(
            lot_size_sqft=8200.0,
            buildable_area_sqft=6500.0,
            frontage_feet=75.0,
            slope_condition="flat",
            drainage_quality=4,
            waterfront=False,
            flood_zone="X"
        ),
        
        location=LocationNeighborhood(
            elementary_school_rating=7,
            middle_school_rating=6,
            high_school_rating=8,
            crime_index=35,  # Lower = safer
            walk_score=65,
            bike_score=55,
            transit_score=45,
            proximity_parks=4,
            proximity_shopping=3,
            commute_time_downtown=28
        ),
        
        market=MarketLiquidity(
            months_of_inventory=3.2,
            median_days_on_market=42,
            sale_to_list_ratio=0.99,
            price_cut_rate=0.18,
            spring_seasonality=1.06,
            investor_activity_pct=0.12
        ),
        
        legal=LegalFinancial(
            annual_property_tax=6200.0,
            tax_rate_per_1000=12.8,
            monthly_hoa_fee=0.0,
            annual_insurance_cost=1350.0,
            wildfire_risk=RiskLevel.LOW,
            earthquake_risk=RiskLevel.MODERATE
        ),
        
        data_quality=DataQuality(
            comp_count_within_half_mile=12,
            comp_variance=0.12,
            photo_count=28,
            has_floor_plan=True,
            has_3d_tour=False,
            mls_data_completeness=0.88
        )
    )