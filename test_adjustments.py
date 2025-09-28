"""
Test Comprehensive Property Adjustments
=====================================

Run this script to test your new comprehensive property forecasting system
"""

import sys
import os

# Add the current directory to Python path so imports work
sys.path.append(os.getcwd())

def test_comprehensive_adjustments():
    """Test the comprehensive adjustment calculations"""
    
    try:
        print("🚀 Testing Comprehensive Property Adjustments...")
        print("=" * 50)
        
        # Import our modules
        from agents.analysisSchemasChangesCharlotte import ComprehensiveFeatureAnalyzer, create_sample_comprehensive_comparable
        from agents.enhanced_property_schema import create_test_property_for_analysis
        
        print("✅ Successfully imported modules")
        
        # Create the analyzer
        analyzer = ComprehensiveFeatureAnalyzer()
        print("✅ Created ComprehensiveFeatureAnalyzer")
        
        # Create test properties
        subject_property = create_test_property_for_analysis()
        comparable_property = create_sample_comprehensive_comparable()
        
        print("✅ Created test properties")
        print(f"📍 Subject: {subject_property.address}")
        print(f"📍 Comparable: {comparable_property['address']}")
        
        # Calculate adjustments
        print("\n🧮 Calculating comprehensive adjustments...")
        adjustments = analyzer.calculate_comprehensive_adjustments(subject_property, comparable_property)
        
        if not adjustments:
            print("❌ No adjustments calculated - check for errors")
            return
        
        # Get summary
        summary = analyzer.get_adjustment_summary(adjustments)
        
        # Display results
        print("\n" + "=" * 60)
        print("🏠 COMPREHENSIVE PROPERTY ANALYSIS RESULTS")
        print("=" * 60)
        
        print(f"💰 Comparable Sale Price: ${comparable_property['sale_price']:,}")
        print(f"📊 Total Adjustment: ${summary['total_adjustment']:,}")
        print(f"🎯 Adjusted Subject Value: ${comparable_property['sale_price'] + summary['total_adjustment']:,}")
        print(f"📈 Number of Factors: {summary['adjustment_count']}")
        
        # Show category breakdown
        print(f"\n📋 ADJUSTMENT BREAKDOWN BY CATEGORY:")
        print("-" * 40)
        for category, total in summary['category_totals'].items():
            if total != 0:
                print(f"  {category.title()}: ${total:,}")
        
        # Show individual adjustments
        print(f"\n🔍 DETAILED ADJUSTMENTS:")
        print("-" * 40)
        for adjustment_name, value in summary['individual_adjustments'].items():
            if value != 0:
                sign = "+" if value > 0 else ""
                print(f"  {adjustment_name.replace('_', ' ').title()}: {sign}${value:,}")
        
        print("\n" + "=" * 60)
        print("✅ TEST COMPLETED SUCCESSFULLY!")
        print("🎉 Your comprehensive forecasting system is working!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure you're in the vthacks2025 directory")
        return False
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        print(f"🐛 Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_comprehensive_adjustments()
    
    if success:
        print("\n🚀 NEXT STEPS:")
        print("1. Try modifying the test properties to see different adjustments")
        print("2. Add real property data using convert_basic_to_comprehensive()")
        print("3. Integrate with your analysis_engine.py")
    else:
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Make sure you're in the vthacks2025 directory")
        print("2. Check that all files exist: enhanced_property_schema.py and analysisSchemasChangesCharlotte")
        print("3. Run: python test_adjustments.py")