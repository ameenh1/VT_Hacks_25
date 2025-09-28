"""
Integration Bridge for Comprehensive Property Features
=====================================================

This file creates the bridge between the enhanced property schema and the existing analysis engine.
It converts comprehensive features into analysis-ready formats and calculates adjustments.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import json
import logging

# Import your comprehensive schema
from agents.enhanced_property_schema import (
    ComprehensivePropertyFeatures, ComprehensiveAdjustmentRates,
    PropertyStructure, LocationNeighborhood, PropertyAmenities,
    LegalFinancial, PropertySystems, SiteLot
)

logger = logging.getLogger(__name__)


class ComprehensiveFeatureAnalyzer:
    """
    Converts comprehensive property features into valuation adjustments
    This bridges your enhanced schema with the analysis engine
    """
    
    def __init__(self):
        self.adjustment_rates = ComprehensiveAdjustmentRates()
        logger.info("Comprehensive Feature Analyzer initialized")
    
    def calculate_comprehensive_adjustments(self, 
                                          subject_property: ComprehensivePropertyFeatures,
                                          comparable_property: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate all adjustments between subject and comparable property
        Returns: Dictionary of adjustment categories and dollar amounts
        """
        adjustments = {}
        
        try:
            # 1. STRUCTURE ADJUSTMENTS
            structure_adj = self._calculate_structure_adjustments(
                subject_property.structure, comparable_property
            )
            adjustments.update(structure_adj)
            
            # 2. LOCATION ADJUSTMENTS  
            location_adj = self._calculate_location_adjustments(
                subject_property.location, comparable_property
            )
            adjustments.update(location_adj)
            
            # 3. AMENITY ADJUSTMENTS
            amenity_adj = self._calculate_amenity_adjustments(
                subject_property.amenities, comparable_property
            )
            adjustments.update(amenity_adj)
            
            # 4. SYSTEMS ADJUSTMENTS
            systems_adj = self._calculate_systems_adjustments(
                subject_property.systems, comparable_property
            )
            adjustments.update(systems_adj)
            
            # 5. SITE/LOT ADJUSTMENTS
            site_adj = self._calculate_site_adjustments(
                subject_property.site, comparable_property
            )
            adjustments.update(site_adj)
            
            # 6. LEGAL/FINANCIAL ADJUSTMENTS
            legal_adj = self._calculate_legal_adjustments(
                subject_property.legal, comparable_property
            )
            adjustments.update(legal_adj)
            
            logger.info(f"Calculated {len(adjustments)} comprehensive adjustments")
            return adjustments
            
        except Exception as e:
            logger.error(f"Error calculating comprehensive adjustments: {str(e)}")
            return {}
    
    def _calculate_structure_adjustments(self, 
                                       subject_structure: PropertyStructure,
                                       comparable: Dict[str, Any]) -> Dict[str, float]:
        """Calculate structure-related adjustments"""
        adjustments = {}
        
        # GLA (Gross Living Area) adjustment
        comp_gla = comparable.get('gla', subject_structure.finished_sqft)
        gla_diff = subject_structure.finished_sqft - comp_gla
        if gla_diff != 0:
            adjustments['gla_adjustment'] = gla_diff * 75.0  # $75 per sqft
        
        # Bedroom adjustment
        comp_bedrooms = comparable.get('bedrooms', subject_structure.bedrooms)
        bedroom_diff = subject_structure.bedrooms - comp_bedrooms
        if bedroom_diff != 0:
            adjustments['bedroom_adjustment'] = bedroom_diff * 8000.0  # $8K per bedroom
        
        # Bathroom adjustment
        comp_bathrooms = comparable.get('bathrooms', subject_structure.bathrooms)
        bathroom_diff = subject_structure.bathrooms - comp_bathrooms
        if bathroom_diff != 0:
            adjustments['bathroom_adjustment'] = bathroom_diff * 4500.0  # $4.5K per bath
        
        # Condition adjustment (multiplier difference)
        condition_multipliers = {
            'excellent': 1.12, 'good': 1.0, 'average': 0.96, 'fair': 0.88, 'poor': 0.75
        }
        subject_multiplier = condition_multipliers.get(subject_structure.condition.value, 1.0)
        comp_condition = comparable.get('condition', 'average')
        comp_multiplier = condition_multipliers.get(comp_condition, 1.0)
        
        if subject_multiplier != comp_multiplier:
            # Apply to a base value (estimated from comparable price)
            base_value = comparable.get('sale_price', 300000)
            adjustments['condition_adjustment'] = base_value * (subject_multiplier - comp_multiplier)
        
        # Stories preference (main floor bedroom premium)
        if subject_structure.bedroom_on_main and not comparable.get('bedroom_on_main', False):
            adjustments['main_floor_bedroom'] = 5000.0
        elif not subject_structure.bedroom_on_main and comparable.get('bedroom_on_main', False):
            adjustments['main_floor_bedroom'] = -5000.0
        
        return adjustments
    
    def _calculate_location_adjustments(self, 
                                      subject_location: LocationNeighborhood,
                                      comparable: Dict[str, Any]) -> Dict[str, float]:
        """Calculate location and neighborhood adjustments"""
        adjustments = {}
        
        # School rating adjustments (major factor!)
        comp_school_rating = comparable.get('elementary_school_rating', 5)
        school_diff = subject_location.elementary_school_rating - comp_school_rating
        if school_diff != 0:
            adjustments['school_rating_adjustment'] = school_diff * 5000.0  # $5K per rating point
        
        # Crime safety adjustment
        comp_crime_index = comparable.get('crime_index', 50)
        crime_diff = comp_crime_index - subject_location.crime_index  # Lower crime = better
        if crime_diff != 0:
            adjustments['crime_safety_adjustment'] = crime_diff * 300.0  # $300 per point improvement
        
        # Walkability adjustment
        comp_walk_score = comparable.get('walk_score', 50)
        walk_diff = subject_location.walk_score - comp_walk_score
        if walk_diff != 0:
            adjustments['walkability_adjustment'] = walk_diff * 200.0  # $200 per walk score point
        
        # Commute time adjustment (downtown access)
        comp_commute = comparable.get('commute_time_downtown', 30)
        commute_diff = comp_commute - subject_location.commute_time_downtown  # Shorter = better
        if commute_diff != 0:
            adjustments['commute_adjustment'] = commute_diff * 100.0  # $100 per minute saved
        
        return adjustments
    
    def _calculate_amenity_adjustments(self, 
                                     subject_amenities: PropertyAmenities,
                                     comparable: Dict[str, Any]) -> Dict[str, float]:
        """Calculate amenity-related adjustments"""
        adjustments = {}
        
        # Pool adjustment
        subject_has_pool = subject_amenities.has_pool
        comp_has_pool = comparable.get('has_pool', False)
        if subject_has_pool and not comp_has_pool:
            pool_value = 15000 if subject_amenities.pool_type == "inground" else 5000
            adjustments['pool_adjustment'] = pool_value
        elif not subject_has_pool and comp_has_pool:
            adjustments['pool_adjustment'] = -10000  # Comparable has pool, subject doesn't
        
        # Fireplace adjustment
        subject_fireplaces = subject_amenities.fireplace_count
        comp_fireplaces = comparable.get('fireplace_count', 0)
        fireplace_diff = subject_fireplaces - comp_fireplaces
        if fireplace_diff != 0:
            adjustments['fireplace_adjustment'] = fireplace_diff * 3000.0  # $3K per fireplace
        
        # Yard and outdoor features
        yard_diff = subject_amenities.yard_usability - comparable.get('yard_usability', 3)
        if yard_diff != 0:
            adjustments['yard_quality_adjustment'] = yard_diff * 2000.0  # $2K per quality point
        
        return adjustments
    
    def _calculate_systems_adjustments(self, 
                                     subject_systems: PropertySystems,
                                     comparable: Dict[str, Any]) -> Dict[str, float]:
        """Calculate systems and technology adjustments"""
        adjustments = {}
        
        # HVAC age adjustment
        comp_hvac_age = comparable.get('hvac_age', 10)
        hvac_age_diff = comp_hvac_age - subject_systems.hvac_age  # Newer = better
        if hvac_age_diff != 0:
            adjustments['hvac_age_adjustment'] = hvac_age_diff * 200.0  # $200 per year newer
        
        # Solar panel adjustment
        if subject_systems.has_solar and not comparable.get('has_solar', False):
            adjustments['solar_adjustment'] = subject_systems.solar_kw * 3000.0  # $3K per kW
        elif not subject_systems.has_solar and comparable.get('has_solar', False):
            comp_solar_kw = comparable.get('solar_kw', 5.0)
            adjustments['solar_adjustment'] = -(comp_solar_kw * 3000.0)
        
        # EV charger adjustment
        if subject_systems.has_ev_charger and not comparable.get('has_ev_charger', False):
            adjustments['ev_charger_adjustment'] = 2000.0
        
        # Smart home features
        subject_smart_count = len(subject_systems.smart_home_features)
        comp_smart_count = len(comparable.get('smart_home_features', []))
        if subject_smart_count > comp_smart_count:
            adjustments['smart_home_adjustment'] = (subject_smart_count - comp_smart_count) * 1000.0
        
        return adjustments
    
    def _calculate_site_adjustments(self, 
                                  subject_site: SiteLot,
                                  comparable: Dict[str, Any]) -> Dict[str, float]:
        """Calculate site and lot adjustments"""
        adjustments = {}
        
        # Lot size adjustment
        comp_lot_size = comparable.get('lot_size_sqft', subject_site.lot_size_sqft)
        lot_diff = subject_site.lot_size_sqft - comp_lot_size
        if lot_diff != 0:
            adjustments['lot_size_adjustment'] = lot_diff * 3.0  # $3 per sqft
        
        # Waterfront premium
        if subject_site.waterfront and not comparable.get('waterfront', False):
            water_premiums = {'ocean': 0.15, 'lake': 0.08, 'river': 0.05}
            premium_pct = water_premiums.get(subject_site.water_type, 0.05)
            comp_price = comparable.get('sale_price', 300000)
            adjustments['waterfront_adjustment'] = comp_price * premium_pct
        
        # Flood zone discount
        if subject_site.flood_zone != 'X' and comparable.get('flood_zone', 'X') == 'X':
            comp_price = comparable.get('sale_price', 300000)
            adjustments['flood_zone_adjustment'] = -comp_price * 0.10  # 10% discount
        
        return adjustments
    
    def _calculate_legal_adjustments(self, 
                                   subject_legal: LegalFinancial,
                                   comparable: Dict[str, Any]) -> Dict[str, float]:
        """Calculate legal and financial adjustments"""
        adjustments = {}
        
        # HOA fee adjustment (negative impact)
        comp_hoa_fee = comparable.get('monthly_hoa_fee', 0)
        hoa_diff = subject_legal.monthly_hoa_fee - comp_hoa_fee
        if hoa_diff != 0:
            # Higher HOA fees reduce value
            adjustments['hoa_fee_adjustment'] = -hoa_diff * 20.0  # -$20 value per $1 monthly HOA
        
        # Property tax rate adjustment
        comp_tax_rate = comparable.get('tax_rate_per_1000', 12.5)
        tax_diff = subject_legal.tax_rate_per_1000 - comp_tax_rate
        if tax_diff != 0:
            # Higher tax rate reduces value
            comp_price = comparable.get('sale_price', 300000)
            annual_impact = (tax_diff / 1000) * comp_price
            adjustments['property_tax_adjustment'] = -annual_impact * 10  # Capitalize at 10%
        
        return adjustments
    
    def get_total_adjustments(self, adjustments: Dict[str, float]) -> float:
        """Sum all adjustments to get total dollar adjustment"""
        return sum(adjustments.values())
    
    def get_adjustment_summary(self, adjustments: Dict[str, float]) -> Dict[str, Any]:
        """Create a summary of adjustments for reporting"""
        total = self.get_total_adjustments(adjustments)
        
        # Group by category
        categories = {
            'structure': [k for k in adjustments.keys() if any(x in k for x in ['gla', 'bedroom', 'bathroom', 'condition'])],
            'location': [k for k in adjustments.keys() if any(x in k for x in ['school', 'crime', 'walk', 'commute'])],
            'amenities': [k for k in adjustments.keys() if any(x in k for x in ['pool', 'fireplace', 'yard'])],
            'systems': [k for k in adjustments.keys() if any(x in k for x in ['hvac', 'solar', 'ev', 'smart'])],
            'site': [k for k in adjustments.keys() if any(x in k for x in ['lot', 'waterfront', 'flood'])],
            'legal': [k for k in adjustments.keys() if any(x in k for x in ['hoa', 'tax'])]
        }
        
        category_totals = {}
        for category, keys in categories.items():
            category_totals[category] = sum(adjustments.get(k, 0) for k in keys)
        
        return {
            'total_adjustment': total,
            'category_totals': category_totals,
            'individual_adjustments': adjustments,
            'adjustment_count': len(adjustments)
        }


def create_sample_comprehensive_comparable() -> Dict[str, Any]:
    """
    Create a sample comparable property for testing
    This simulates what you'd get from MLS/ATTOM data
    """
    return {
        'address': '456 Comparable Street',
        'sale_price': 425000,
        'sale_date': '2024-08-15',
        'gla': 2100,
        'bedrooms': 3,
        'bathrooms': 2.0,
        'garage_spaces': 2,
        'lot_size_sqft': 7500,
        'age': 15,
        'condition': 'average',
        'elementary_school_rating': 6,
        'crime_index': 40,
        'walk_score': 60,
        'commute_time_downtown': 35,
        'has_pool': False,
        'fireplace_count': 1,
        'yard_usability': 3,
        'hvac_age': 12,
        'has_solar': False,
        'has_ev_charger': False,
        'smart_home_features': [],
        'waterfront': False,
        'flood_zone': 'X',
        'monthly_hoa_fee': 0,
        'tax_rate_per_1000': 13.0
    }


# EXAMPLE USAGE FOR TESTING
if __name__ == "__main__":
    # This shows you how to use the comprehensive features
    from agents.enhanced_property_schema import create_sample_comprehensive_property
    
    # Create analyzer
    analyzer = ComprehensiveFeatureAnalyzer()
    
    # Get sample comprehensive property
    subject = create_sample_comprehensive_property()
    
    # Get sample comparable
    comparable = create_sample_comprehensive_comparable()
    
    # Calculate adjustments
    adjustments = analyzer.calculate_comprehensive_adjustments(subject, comparable)
    
    # Get summary
    summary = analyzer.get_adjustment_summary(adjustments)
    
    print("=== COMPREHENSIVE ADJUSTMENT ANALYSIS ===")
    print(f"Total Adjustment: ${summary['total_adjustment']:,.0f}")
    print("\nCategory Breakdowns:")
    for category, total in summary['category_totals'].items():
        if total != 0:
            print(f"  {category.title()}: ${total:,.0f}")
    
    print(f"\nComparable Sale Price: ${comparable['sale_price']:,}")
    print(f"Adjusted Value: ${comparable['sale_price'] + summary['total_adjustment']:,}")