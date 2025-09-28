"""
🚀 COMPREHENSIVE ANALYSIS ENGINE
Integrates the comprehensive property features system with existing analysis engine
WITHOUT modifying the original analysis_engine.py

This file provides a wrapper that uses your 50+ factor comprehensive system
while maintaining compatibility with existing code.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

# Import the comprehensive system
from .enhanced_property_schema import (
    ComprehensivePropertyFeatures, 
    create_sample_comprehensive_property,
    convert_basic_to_comprehensive
)
from .analysisSchemasChangesCharlotte import ComprehensiveFeatureAnalyzer

# Import original analysis engine components
try:
    from .analysis_engine import (
        PropertyAnalysisEngine, 
        PropertyFeatures,  # Original basic class
        AnalysisResult,
        MarketData,
        ComparableSale
    )
except ImportError:
    print("⚠️ Could not import original analysis_engine.py - creating stub classes")
    
    @dataclass
    class PropertyFeatures:
        """Stub for original PropertyFeatures if import fails"""
        pass
    
    @dataclass
    class AnalysisResult:
        """Stub for original AnalysisResult if import fails"""
        pass
    
    class PropertyAnalysisEngine:
        """Stub for original engine if import fails"""
        pass

@dataclass
class ComprehensiveAnalysisResult:
    """Enhanced analysis result with comprehensive insights"""
    # Original analysis result data
    estimated_value: float
    confidence_score: float
    analysis_method: str
    comparable_sales: List[Dict]
    
    # NEW: Comprehensive analysis insights
    comprehensive_adjustments: Dict[str, float]
    total_comprehensive_adjustment: float
    feature_impact_breakdown: Dict[str, Dict[str, float]]
    investment_recommendation: str
    equity_opportunity: float
    equity_percentage: float
    
    # NEW: Advanced insights
    premium_features: List[str]
    risk_factors: List[str]
    value_drivers: List[str]
    market_position: str  # "premium", "average", "discount"
    
    # Enhanced confidence metrics
    comprehensive_confidence: float
    data_completeness_score: float
    adjustment_reliability: float

class ComprehensivePropertyAnalysisEngine:
    """
    🚀 ENHANCED ANALYSIS ENGINE
    Combines original analysis logic with comprehensive 50+ factor system
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.comprehensive_analyzer = ComprehensiveFeatureAnalyzer()
        
        # Try to initialize original engine
        try:
            self.original_engine = PropertyAnalysisEngine()
            self.has_original_engine = True
            print("✅ Original PropertyAnalysisEngine loaded successfully")
        except:
            self.original_engine = None
            self.has_original_engine = False
            print("⚠️ Running in comprehensive-only mode")
    
    def analyze_property_comprehensive(
        self, 
        subject_property: ComprehensivePropertyFeatures,
        comparable_sales: List[Dict],
        market_data: Optional[Dict] = None
    ) -> ComprehensiveAnalysisResult:
        """
        🎯 MAIN ANALYSIS METHOD
        Performs comprehensive property analysis using 50+ factors
        """
        print("🔍 Starting Comprehensive Property Analysis...")
        print(f"📍 Property: {subject_property.address}")
        print(f"📊 Analyzing {len(comparable_sales)} comparable sales")
        
        # Step 1: Run comprehensive adjustments on each comparable
        adjusted_comparables = []
        all_adjustments = []
        
        for i, comp_sale in enumerate(comparable_sales):
            print(f"🏠 Analyzing comparable {i+1}/{len(comparable_sales)}")
            
            # Calculate comprehensive adjustments
            adjustments = self.comprehensive_analyzer.calculate_comprehensive_adjustments(
                subject_property, comp_sale
            )
            
            adjustment_summary = self.comprehensive_analyzer.get_adjustment_summary(adjustments)
            all_adjustments.append(adjustment_summary)
            
            # Create adjusted comparable
            adjusted_value = comp_sale.get('sale_price', 0) + adjustment_summary['total_adjustment']
            adjusted_comp = {
                **comp_sale,
                'adjusted_value': adjusted_value,
                'total_adjustment': adjustment_summary['total_adjustment'],
                'adjustments': adjustments
            }
            adjusted_comparables.append(adjusted_comp)
            
            print(f"  💰 Original: ${comp_sale.get('sale_price', 0):,}")
            print(f"  🔧 Adjusted: ${adjusted_value:,} ({adjustment_summary['total_adjustment']:+,})")
        
        # Step 2: Calculate estimated value using adjusted comparables
        estimated_value = self._calculate_weighted_value(adjusted_comparables, subject_property)
        
        # Step 3: Analyze investment opportunity
        equity_opportunity = 0
        equity_percentage = 0
        investment_recommendation = "Unknown"
        
        if subject_property.listing_price:
            equity_opportunity = estimated_value - subject_property.listing_price
            equity_percentage = (equity_opportunity / subject_property.listing_price) * 100
            investment_recommendation = self._get_investment_recommendation(equity_percentage)
        
        # Step 4: Extract insights from adjustments
        feature_insights = self._analyze_feature_impacts(all_adjustments)
        
        # Step 5: Calculate confidence metrics
        confidence_metrics = self._calculate_confidence_metrics(
            adjusted_comparables, subject_property, all_adjustments
        )
        
        # Step 6: Create comprehensive result
        result = ComprehensiveAnalysisResult(
            # Core analysis
            estimated_value=estimated_value,
            confidence_score=confidence_metrics['overall_confidence'],
            analysis_method="Comprehensive Sales Comparison (50+ Factors)",
            comparable_sales=adjusted_comparables,
            
            # Comprehensive insights
            comprehensive_adjustments=feature_insights['average_adjustments'],
            total_comprehensive_adjustment=feature_insights['average_total_adjustment'],
            feature_impact_breakdown=feature_insights['category_impacts'],
            investment_recommendation=investment_recommendation,
            equity_opportunity=equity_opportunity,
            equity_percentage=equity_percentage,
            
            # Advanced insights
            premium_features=feature_insights['premium_features'],
            risk_factors=feature_insights['risk_factors'],
            value_drivers=feature_insights['value_drivers'],
            market_position=feature_insights['market_position'],
            
            # Enhanced confidence
            comprehensive_confidence=confidence_metrics['comprehensive_confidence'],
            data_completeness_score=confidence_metrics['data_completeness'],
            adjustment_reliability=confidence_metrics['adjustment_reliability']
        )
        
        print("✅ Comprehensive Analysis Complete!")
        return result
    
    def _calculate_weighted_value(
        self, 
        adjusted_comparables: List[Dict], 
        subject_property: ComprehensivePropertyFeatures
    ) -> float:
        """Calculate weighted estimated value from adjusted comparables"""
        if not adjusted_comparables:
            return 0
        
        # Simple average for now - could implement distance/similarity weighting
        total_value = sum(comp['adjusted_value'] for comp in adjusted_comparables)
        estimated_value = total_value / len(adjusted_comparables)
        
        print(f"📊 Estimated Value: ${estimated_value:,.0f} (average of {len(adjusted_comparables)} adjusted comps)")
        return estimated_value
    
    def _get_investment_recommendation(self, equity_percentage: float) -> str:
        """Generate investment recommendation based on equity opportunity"""
        if equity_percentage > 20:
            return "🔥 EXCELLENT DEAL - Strong equity opportunity!"
        elif equity_percentage > 10:
            return "✅ GOOD DEAL - Solid equity potential"
        elif equity_percentage > 0:
            return "⚖️ FAIR DEAL - Limited equity opportunity"
        elif equity_percentage > -10:
            return "⚠️ MARKET PRICE - Consider other factors"
        else:
            return "❌ OVERPRICED - Significant risk"
    
    def _analyze_feature_impacts(self, all_adjustments: List[Dict]) -> Dict[str, Any]:
        """Analyze feature impacts across all comparables"""
        if not all_adjustments:
            return {}
        
        # Calculate average adjustments
        avg_adjustments = {}
        category_impacts = {}
        
        # Collect all adjustment types
        all_adjustment_keys = set()
        for adj_summary in all_adjustments:
            all_adjustment_keys.update(adj_summary['individual_adjustments'].keys())
        
        # Calculate averages
        for key in all_adjustment_keys:
            values = [adj['individual_adjustments'].get(key, 0) for adj in all_adjustments]
            avg_adjustments[key] = sum(values) / len(values)
        
        # Category impacts
        for adj_summary in all_adjustments:
            for category, value in adj_summary['category_totals'].items():
                if category not in category_impacts:
                    category_impacts[category] = []
                category_impacts[category].append(value)
        
        # Average category impacts
        for category in category_impacts:
            category_impacts[category] = sum(category_impacts[category]) / len(category_impacts[category])
        
        # Identify premium features, risks, and value drivers
        premium_features = []
        risk_factors = []
        value_drivers = []
        
        for key, value in avg_adjustments.items():
            if value > 5000:  # Significant positive impact
                feature_name = key.replace('_', ' ').title()
                premium_features.append(f"{feature_name}: ${value:+,.0f}")
                value_drivers.append(feature_name)
            elif value < -5000:  # Significant negative impact
                feature_name = key.replace('_', ' ').title()
                risk_factors.append(f"{feature_name}: ${value:+,.0f}")
        
        # Determine market position
        avg_total = sum(adj['total_adjustment'] for adj in all_adjustments) / len(all_adjustments)
        if avg_total > 15000:
            market_position = "premium"
        elif avg_total > -15000:
            market_position = "average"
        else:
            market_position = "discount"
        
        return {
            'average_adjustments': avg_adjustments,
            'average_total_adjustment': avg_total,
            'category_impacts': category_impacts,
            'premium_features': premium_features[:5],  # Top 5
            'risk_factors': risk_factors[:5],  # Top 5 risks
            'value_drivers': value_drivers[:5],  # Top 5 drivers
            'market_position': market_position
        }
    
    def _calculate_confidence_metrics(
        self,
        adjusted_comparables: List[Dict],
        subject_property: ComprehensivePropertyFeatures,
        all_adjustments: List[Dict]
    ) -> Dict[str, float]:
        """Calculate comprehensive confidence metrics"""
        
        # Overall confidence based on number of comparables and data quality
        comp_count_score = min(len(adjusted_comparables) / 5.0, 1.0)  # Max confidence at 5+ comps
        
        # Data completeness from subject property
        data_completeness = getattr(subject_property.data_quality, 'mls_data_completeness', 0.8) if hasattr(subject_property, 'data_quality') else 0.8
        
        # Adjustment reliability - lower variance = higher reliability
        if all_adjustments:
            adjustment_values = [adj['total_adjustment'] for adj in all_adjustments]
            if len(adjustment_values) > 1:
                import statistics
                mean_adj = statistics.mean(adjustment_values)
                variance = statistics.variance(adjustment_values)
                cv = (variance ** 0.5) / abs(mean_adj) if mean_adj != 0 else 0
                adjustment_reliability = max(0, 1 - min(cv / 0.5, 1))  # Higher variance = lower reliability
            else:
                adjustment_reliability = 0.7
        else:
            adjustment_reliability = 0.5
        
        # Comprehensive confidence combines all factors
        comprehensive_confidence = (
            comp_count_score * 0.3 +
            data_completeness * 0.4 +
            adjustment_reliability * 0.3
        )
        
        # Overall confidence (weighted average)
        overall_confidence = (comprehensive_confidence + adjustment_reliability) / 2
        
        return {
            'overall_confidence': overall_confidence,
            'comprehensive_confidence': comprehensive_confidence,
            'data_completeness': data_completeness,
            'adjustment_reliability': adjustment_reliability
        }
    
    def analyze_with_basic_property(
        self,
        basic_property: PropertyFeatures,
        comparable_sales: List[Dict],
        market_data: Optional[Dict] = None
    ) -> ComprehensiveAnalysisResult:
        """
        🔄 COMPATIBILITY METHOD
        Accepts basic PropertyFeatures and converts to comprehensive analysis
        """
        print("🔄 Converting basic property to comprehensive features...")
        
        # Convert basic to comprehensive
        comprehensive_property = convert_basic_to_comprehensive(basic_property)
        
        # Run comprehensive analysis
        return self.analyze_property_comprehensive(
            comprehensive_property, comparable_sales, market_data
        )
    
    def print_analysis_report(self, result: ComprehensiveAnalysisResult):
        """
        📊 GENERATE COMPREHENSIVE REPORT
        Beautiful formatted output of the analysis results
        """
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE PROPERTY ANALYSIS REPORT")
        print("=" * 80)
        
        # Core Results
        print(f"\n💰 ESTIMATED VALUE: ${result.estimated_value:,.0f}")
        print(f"🎯 CONFIDENCE SCORE: {result.confidence_score:.1%}")
        print(f"📈 ANALYSIS METHOD: {result.analysis_method}")
        
        # Investment Analysis
        if result.equity_opportunity != 0:
            print(f"\n🏦 INVESTMENT ANALYSIS:")
            print(f"  💡 Equity Opportunity: ${result.equity_opportunity:+,.0f}")
            print(f"  📊 Equity Percentage: {result.equity_percentage:+.1f}%")
            print(f"  🎯 Recommendation: {result.investment_recommendation}")
        
        # Feature Insights
        if result.premium_features:
            print(f"\n🌟 PREMIUM FEATURES:")
            for feature in result.premium_features[:5]:
                print(f"  • {feature}")
        
        if result.risk_factors:
            print(f"\n⚠️ RISK FACTORS:")
            for risk in result.risk_factors[:5]:
                print(f"  • {risk}")
        
        if result.value_drivers:
            print(f"\n🚀 VALUE DRIVERS:")
            for driver in result.value_drivers[:3]:
                print(f"  • {driver}")
        
        # Market Position
        print(f"\n📍 MARKET POSITION: {result.market_position.upper()}")
        
        # Comparable Analysis
        print(f"\n🏠 COMPARABLE SALES ANALYSIS:")
        for i, comp in enumerate(result.comparable_sales[:3], 1):
            print(f"  Comp {i}: ${comp.get('sale_price', 0):,} → ${comp.get('adjusted_value', 0):,} ({comp.get('total_adjustment', 0):+,})")
        
        # Confidence Metrics
        print(f"\n📊 CONFIDENCE METRICS:")
        print(f"  Comprehensive Confidence: {result.comprehensive_confidence:.1%}")
        print(f"  Data Completeness: {result.data_completeness_score:.1%}")
        print(f"  Adjustment Reliability: {result.adjustment_reliability:.1%}")
        
        print("\n" + "=" * 80)
        print("✅ ANALYSIS COMPLETE - Powered by 50+ Factor Comprehensive System")
        print("=" * 80)

# Convenience functions for easy integration
def analyze_comprehensive_property(
    property_address: str,
    property_data: Dict,
    comparable_sales: List[Dict]
) -> ComprehensiveAnalysisResult:
    """
    🎯 ONE-FUNCTION ANALYSIS
    Simplified interface for comprehensive property analysis
    """
    engine = ComprehensivePropertyAnalysisEngine()
    
    # Create comprehensive property from data
    comprehensive_prop = create_sample_comprehensive_property()
    comprehensive_prop.address = property_address
    
    # Update with provided data
    for key, value in property_data.items():
        if hasattr(comprehensive_prop, key):
            setattr(comprehensive_prop, key, value)
    
    return engine.analyze_property_comprehensive(comprehensive_prop, comparable_sales)

def quick_analysis_demo():
    """
    🎪 DEMO FUNCTION
    Shows the comprehensive system in action
    """
    print("🎪 COMPREHENSIVE ANALYSIS DEMO")
    print("=" * 50)
    
    engine = ComprehensivePropertyAnalysisEngine()
    
    # Create sample property
    property_data = create_sample_comprehensive_property()
    property_data.address = "123 Demo Street, Example City"
    
    # Create sample comparables
    from .analysisSchemasChangesCharlotte import create_sample_comprehensive_comparable
    
    comparables = [
        create_sample_comprehensive_comparable(),
        {**create_sample_comprehensive_comparable(), 'sale_price': 435000},
        {**create_sample_comprehensive_comparable(), 'sale_price': 415000}
    ]
    
    # Run analysis
    result = engine.analyze_property_comprehensive(property_data, comparables)
    
    # Print report
    engine.print_analysis_report(result)
    
    return result

if __name__ == "__main__":
    print("🚀 Comprehensive Analysis Engine - Running Demo")
    quick_analysis_demo()