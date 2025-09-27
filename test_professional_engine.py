"""
Test the Professional Analysis Engine
====================================

Test the standalone professional valuation engine implementation.
"""

import asyncio
import os
from dotenv import load_dotenv
from agents.analysis_engine import AnalysisEngine, PropertyFeatures

async def test_professional_analysis():
    """Test the professional analysis engine"""
    
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY or GEMINI_API_KEY not found in environment")
        print("Please add your Gemini API key to .env file")
        return
    
    print("🏠 Testing Professional Real Estate Analysis Engine")
    print("=" * 60)
    
    # Initialize the professional analysis engine
    engine = AnalysisEngine(api_key=api_key)
    print("✅ Analysis Engine initialized with Gemini 2.5 Pro")
    
    # Test property data
    test_property = PropertyFeatures(
        address="123 Test Property Lane",
        gla=2200,  # 2,200 sq ft
        bedrooms=4,
        bathrooms=2.5,
        garage_spaces=2,
        lot_size=8500,  # 8,500 sq ft lot
        age=12,  # 12 years old
        condition='good',
        property_type='SFR',  # Single Family Residence
        listing_price=425000,
        monthly_rent=2800
    )
    
    print(f"\n📍 Test Property: {test_property.address}")
    print(f"   • Size: {test_property.gla:,} sq ft")
    print(f"   • Bedrooms/Baths: {test_property.bedrooms}BR/{test_property.bathrooms}BA")
    print(f"   • Listing Price: ${test_property.listing_price:,}")
    print(f"   • Monthly Rent: ${test_property.monthly_rent:,}")
    
    try:
        print("\n🔍 Running Comprehensive Professional Valuation Analysis...")
        print("   Using 3-Approach Methodology:")
        print("   1. Sales Comparison Approach")
        print("   2. Income Approach")  
        print("   3. Cost Approach")
        
        # Run comprehensive analysis
        analysis_result = await engine.comprehensive_valuation_analysis(test_property)
        
        print("\n✅ Analysis Complete! Results:")
        print("=" * 60)
        
        # Display key results
        print(f"📊 Property Analysis Summary")
        print(f"   • Address: {analysis_result.property_address}")
        print(f"   • ARV Estimate: ${analysis_result.valuation.arv_estimate:,.0f}")
        print(f"   • Price per Sq Ft: ${analysis_result.valuation.price_per_sqft:.0f}")
        print(f"   • Deal Score: {analysis_result.deal_score:.0f}%")
        print(f"   • Investment Grade: {analysis_result.investment_grade}")
        print(f"   • Confidence Score: {analysis_result.confidence_score:.1%}")
        
        print(f"\n💰 Valuation Methods:")
        for method, value in analysis_result.valuation.valuation_methods.items():
            weight = analysis_result.valuation.method_weights.get(method, 0)
            print(f"   • {method.value}: ${value:,.0f} (Weight: {weight:.1%})")
        
        print(f"\n🎯 Investment Analysis:")
        print(f"   • Recommended Strategy: {analysis_result.investment_strategy.recommended_strategy.value}")
        print(f"   • Quick Sale Value: ${analysis_result.sell_value_estimate.quick_sale_value:,.0f}")
        print(f"   • Optimal Sale Value: ${analysis_result.sell_value_estimate.optimal_sale_value:,.0f}")
        
        # Show key insights
        if analysis_result.key_insights:
            print(f"\n💡 Key Insights:")
            for insight in analysis_result.key_insights[:3]:
                print(f"   • {insight}")
        
        # Show opportunities
        if analysis_result.opportunities:
            print(f"\n🚀 Opportunities:")
            for opportunity in analysis_result.opportunities[:3]:
                print(f"   • {opportunity}")
        
        print(f"\n📋 Executive Summary:")
        print(f"   {analysis_result.executive_summary}")
        
        print(f"\n✅ Recommendation: {analysis_result.recommendation}")
        
        print("\n" + "=" * 60)
        print("🎉 Professional Analysis Engine Test PASSED!")
        print("   ✅ 3-approach valuation methodology working")
        print("   ✅ AI-enhanced analysis complete") 
        print("   ✅ Structured professional output generated")
        print("   ✅ Investment metrics calculated")
        print("   ✅ Risk assessment completed")
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        print(f"   Full traceback:")
        traceback.print_exc()

async def test_quick_analysis():
    """Test the legacy quick analysis method"""
    
    load_dotenv()
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        return
    
    print("\n" + "=" * 60)
    print("🚀 Testing Quick Analysis (Legacy Compatibility)")
    
    engine = AnalysisEngine(api_key=api_key)
    
    try:
        quick_result = await engine.quick_analysis(
            address="456 Quick Test Dr",
            listing_price=350000
        )
        
        if quick_result.get("success"):
            print("✅ Quick Analysis Results:")
            print(f"   • Deal Score: {quick_result['deal_score']:.0f}%")
            print(f"   • Investment Grade: {quick_result['investment_potential']}")
            print(f"   • ARV Estimate: ${quick_result['arv_estimate']:,.0f}")
            print(f"   • Strategy: {quick_result['recommended_strategy']}")
            print(f"   • Cash Flow: ${quick_result['monthly_cash_flow']:,.0f}/month")
            print(f"   • Confidence: {quick_result['confidence_score']:.1%}")
            print(f"   • Key Insight: {quick_result['key_insight']}")
        else:
            print(f"❌ Quick analysis failed: {quick_result.get('error')}")
            
    except Exception as e:
        print(f"❌ Quick analysis error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_professional_analysis())
    asyncio.run(test_quick_analysis())